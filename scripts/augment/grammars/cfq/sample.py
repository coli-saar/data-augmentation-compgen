import numpy as np
import random
from tqdm import tqdm
import collections

# set random seed to 0
import nltk

from scripts.utils.io import read_file, write_file, mkdir
from scripts.augment.grammars.utils.grammar_utils import *
from scripts.augment.grammars.cfq.grammar import *
from scripts.augment.grammars.cfq.utils import *

def parse_CFQ_corpus(grammar, data):
    parser = nltk.ChartParser(grammar)
    productions = []
    trees = []
    for i, mr in tqdm(enumerate(data)):
        tokens = mr.split()
        parse_trees = list(parser.parse(tokens))
        if len(parse_trees) == 0:
            raise Exception("No parse tree found for {}th MR {}".format(i, mr))
        elif len(parse_trees) > 1:
            raise Exception("Multiple parse tree found for {}th MR {}\n {} trees found".format(i, mr, len(parse_trees)))
        else:
            tree = parse_trees[0]
            trees.append(tree)
            # productions.extend(tree.productions())
            cur_productions = tree.productions()
            productions.extend([(prd, 1.0) for prd in cur_productions])

    return trees, productions

def estimate_PCFG(grammar_string, data):
    print("parsing ...")
    grammar = PCFG.fromstring(grammar_string)
    grammar = binarize_grammar(grammar)
    trees, productions = parse_CFQ_corpus(grammar, data)
    print("Done.")
    print("Estimating PCFG...")
    pcfg = estimate_productions(productions)
    print("Done.")
    return pcfg

def estimate_variable(gold_data, mask_data):
    print("Estimating variable probs ...")
    probabilities = {
        # Three values denotes
        # sampling from decided values
        # sampling from entities
        # sampling a new varaible
        TYPE: [0, 0, 0] for TYPE in [FILMTYPE, ORGTYPE, PEOPLETYPE, GENDERTYPE,\
                            NATIONTYPE]
    }

    for i in range(len(gold_data)):
        gold_mr = gold_data[i].rstrip()
        mask_mr = mask_data[i].rstrip()
        gold_mr = gold_mr.split()
        mask_mr = mask_mr.split()
        type2arg = {TYPE: [] for TYPE in [FILMTYPE, ORGTYPE, PEOPLETYPE, GENDERTYPE, NATIONTYPE]}
        for j in range(len(gold_mr)):
            if mask_mr[j] in probabilities:
                TYPE = mask_mr[j]
                arg = gold_mr[j]
                if arg not in type2arg[TYPE]:
                    if arg.startswith("M"):
                        probabilities[TYPE][1] += 1
                    else:
                        probabilities[TYPE][2] += 1
                    type2arg[TYPE].append(arg)
                else:
                    probabilities[TYPE][0] += 1

    for TYPE in [FILMTYPE, ORGTYPE, PEOPLETYPE, GENDERTYPE, NATIONTYPE]:
        count = sum(probabilities[TYPE])
        probabilities[TYPE] = [num/count for num in probabilities[TYPE]]

    print("Done.")

    return probabilities

def generate_corpus(grammar, num, tgt_path, type2prob):
    output = []
    # grammar = PCFG.fromstring(grammar_str)
    pbar = tqdm(total=num)
    MAX_NUM=99999999
    for sent in tqdm(grammar.generate(MAX_NUM)):
        # print(sent)
        if len(output) >= num:
            break

        try:
            sent = post_process_data(sent, type2prob=type2prob)
        except:
            # print("Error in post processing {}".format(sent))
            continue

        # add psudo source as inputs for the back-translation model
        formatted_sent = "None\t{}\n".format(sent)
        if formatted_sent not in output:
            output.append(formatted_sent)
            pbar.update(1)
        # output.append(post_process_data(sent)+"\n")
    write_file(tgt_path, output)

def post_process_data(mr, type2prob=None):
    def fill_typed_variables(mr, type2prob=None):
        # print(mr)
        def sample_name(list1, list2, new_var, probs=None):
            # print(list1, list2)
            # List1 means the list of decided names like ?x0, M0
            # List2 means the list of undecided entity names like  M1, M2
            # new_var means the next available variable name like ?x1
            # Probs means the probability of three cases
            if probs is not None:
                prob_list1, prob_list2, prob_new_var = probs
                prob1 = normalize(probs[1:])[0]
                prob2 = normalize([probs[0]+probs[2]])[0]
                prob3 = prob_list1
            else:
                prob1, prob2, prob3 = 0.5, 0.5, 0.5

            if len(list1) == 0:
                if random.random() < prob1 or new_var is None:
                    return random.choice(list2)
                else:
                    return new_var

            if len(list2) == 0:
                if random.random() < prob2 or new_var is None:
                    return random.choice(list1)
                else:
                    return new_var

            if random.random() < prob3:
                return random.choice(list1)
            else:
                if random.random() < prob1 or new_var is None:
                    return random.choice(list2)
                else:
                    return new_var
        tokens = mr.split()
        tofill_types = ["FILMTYPE", "ORGTYPE", "PEOPLETYPE", "GENDERTYPE", "NATIONTYPE"]
        filledtype2token = {
            "FILMTYPE": [],
            "ORGTYPE": [],
            "PEOPLETYPE": [],
            "GENDERTYPE": [],
            "NATIONTYPE": [],
        }
        candidate_names = GRAMMAR_DICTIONARY["ents"].copy()
        new_var_idx = 0
        output = []
        for i in range(len(tokens)):
            token = tokens[i]
            if token in tofill_types:
                name = sample_name(filledtype2token[token], candidate_names,
                                       GRAMMAR_DICTIONARY["vars"][new_var_idx] if new_var_idx >= 0 else None,
                                        probs=type2prob[token] if type2prob is not None else None)
                if name == GRAMMAR_DICTIONARY["vars"][new_var_idx]:
                    if new_var_idx+1 < len(GRAMMAR_DICTIONARY["vars"]):
                        new_var_idx += 1
                    else:
                        new_var_idx = -1
                if name not in filledtype2token[token]:
                    filledtype2token[token].append(name)
                if name in candidate_names:
                    candidate_names.remove(name)
                output.append(name)
            else:
                output.append(token)
        return " ".join(output)

    def sort_conjuncts(mr):
        start_idx = mr.find("WHERE lb ")
        end_idx = mr.find(" rb")
        prefix = mr[:start_idx+9]
        suffix = mr[end_idx:]
        mr = mr[start_idx+9:end_idx]
        conjuncts = mr.split(" . ")
        conjuncts = postprocess_conjuncts(conjuncts)
        conjuncts.sort()
        sorted_conjuncts = " . ".join(conjuncts)
        return prefix+sorted_conjuncts+suffix

    def get_subj_rel_to_objects(conjuncts):
        subj_rel_to_objects = collections.OrderedDict()
        for conjunct in conjuncts:
            tokens = conjunct.split()
            subj = tokens[1]
            relation_left_bracket_idx = 2
            relation_right_bracket_idx = tokens.index(")")
            relations = tokens[relation_left_bracket_idx + 1:relation_right_bracket_idx]
            relations = [relation for relation in relations if relation != ","]
            # remove duplicate relations and sort
            relations = list(set(relations))

            arg2 = tokens[relation_right_bracket_idx + 2:-2]
            # print(arg2)
            arg2 = [arg for arg in arg2 if arg != "," and arg != subj]
            # remove duplicate arg2 and sort
            arg2 = list(set(arg2))
            arg2.sort()
            for rel in relations:
                subj_rel = (subj, rel)
                if subj_rel not in subj_rel_to_objects:
                    subj_rel_to_objects[subj_rel] = []
                for obj in arg2:
                    subj_rel_to_objects[subj_rel].append(obj)
        return subj_rel_to_objects

    def get_subj_obj_to_rels(subj_rel_to_objects):
        # Prepare subject-objects to relations map.
        subj_objs_to_rels = collections.defaultdict(list)
        for subj_rel, objects in subj_rel_to_objects.items():
            if objects is not None:
                objects_tuple = tuple(objects)
                subj, rel = subj_rel
                key = (objects_tuple, subj)
                subj_objs_to_rels[key].append(rel)
        return subj_objs_to_rels

    def get_binary_conjuncts(subj_rel_to_objects, subj_objs_to_rels):
        conjuncts_reversible = []
        added_subj_objs = []
        for subj_rel, objects in subj_rel_to_objects.items():
            subj, _ = subj_rel
            objects_tup = tuple(objects)
            if (objects_tup, subj) in added_subj_objs:
                # Already handled the conjuncts with this subject and objects list.
                continue
            else:
                added_subj_objs.append((objects_tup, subj))

            conjunct_reversible = "( {} ( {} ) ( {} ) )".format(
                    subj, " , ".join(subj_objs_to_rels[(objects_tup, subj)]),
                    " , ".join(objects))

            conjuncts_reversible.append(conjunct_reversible)
        return conjuncts_reversible

    def postprocess_conjuncts(conjuncts):
        unary_and_filters = []
        binary_conjuncts = []
        for conj in conjuncts:
            tokens = conj.split()
            if tokens[2] == "a" or tokens[1] == "FILTER":
                unary_and_filters.append(conj)
            else:
                binary_conjuncts.append(conj)

        subj_rel_to_objects = get_subj_rel_to_objects(binary_conjuncts)
        subj_objs_to_rels = get_subj_obj_to_rels(subj_rel_to_objects)
        binary_conjuncts = get_binary_conjuncts(subj_rel_to_objects, subj_objs_to_rels)

        output = []
        for conj in unary_and_filters+binary_conjuncts:
            tokens = conj.split()
            # A conjunct has format like ( ?x1 ( film.performance.film ) ( M1 , M2 ) )
            # We need to extract the first argument, the relation, and the second argument
            arg1 = tokens[1]
            if tokens[2] == "a":
                conj = conj
            elif tokens[1] == "FILTER":
                if tokens[3] == tokens[5]:
                    conj = None
                elif tokens[3] > tokens[5]:
                    #     swap the order of the arguments
                    conj = "( FILTER ( {} != {} ) )".format(tokens[5], tokens[3])
                else:
                    conj = conj
            else:
                relation_left_bracket_idx = 2
                relation_right_bracket_idx = tokens.index(")")
                relations = tokens[relation_left_bracket_idx+1:relation_right_bracket_idx]
                relations = [relation for relation in relations if relation != ","]
                # remove duplicate relations and sort
                relations = list(set(relations))
                relations.sort()
                # print(relations)

                arg2 = tokens[relation_right_bracket_idx+2:-2]
                # print(arg2)
                arg2 = [arg for arg in arg2 if arg != "," and arg != arg1]
                # remove duplicate arg2 and sort
                arg2 = list(set(arg2))
                arg2.sort()
                if len(arg2) == 0:
                    conj = None
                else:
                    conj = "( {} ( {} ) ( {} ) )".format(arg1, " , ".join(relations), " , ".join(arg2))
            if conj not in output and conj is not None:
                output.append(conj)

        return output

    mr = fill_typed_variables(mr, type2prob=type2prob)
    mr = sort_conjuncts(mr)
    return mr

if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("estimate_dist", type=str, help="distribution to estimate")
    args = parser.parse_args()
    estimate_dist = args.estimate_dist

    assert estimate_dist in ["train", "uniform", "test"]

    mcd1_dirpath = "data/cfq/mcd1/"
    if estimate_dist != "uniform":
        data = read_file(f"{mcd1_dirpath}/{estimate_dist}.tsv")
        print("Masking variables ...")
        masked_data = mask_variables(data)
        pcfg = estimate_PCFG(grammar_str, masked_data)
        probs = estimate_variable([x.split("\t")[1] for x in data], masked_data)
    else:
        pcfg = PCFG.fromstring(grammar_str)
        probs = None
    mkdir(f"data/cfq/mcd1/pcfg/{estimate_dist}_dist/")
    generate_corpus(pcfg, 100000, f"data/cfq/mcd1/pcfg/{estimate_dist}_dist/samples.tsv", type2prob=probs)

    # mcd2_dirpath = "data/cfq/mcd2/"
    # if estimate_dist != "uniform":
    #     data = read_file(f"{mcd2_dirpath}/{estimate_dist}.tsv")
    #     print("Masking variables ...")
    #     masked_data = mask_variables(data)
    #     pcfg = estimate_PCFG(grammar_str, masked_data)
    #     probs = estimate_variable([x.split("\t")[1] for x in data], masked_data)
    # else:
    #     pcfg = PCFG.fromstring(grammar_str)
    #     probs = None
    # mkdir(f"data/cfq/mcd2/pcfg/{estimate_dist}_dist/")
    # generate_corpus(pcfg, 100000, f"data/cfq/mcd2/pcfg/{estimate_dist}_dist/samples.tsv", type2prob=probs)
    #
    # mcd3_dirpath = "data/cfq/mcd3/"
    # if estimate_dist != "uniform":
    #     data = read_file(f"{mcd3_dirpath}/{estimate_dist}.tsv")
    #     print("Masking variables ...")
    #     masked_data = mask_variables(data)
    #     pcfg = estimate_PCFG(grammar_str, masked_data)
    #     probs = estimate_variable([x.split("\t")[1] for x in data], masked_data)
    # else:
    #     pcfg = PCFG.fromstring(grammar_str)
    #     probs = None
    # mkdir(f"data/cfq/mcd3/pcfg/{estimate_dist}_dist/")
    # generate_corpus(pcfg, 100000, f"data/cfq/mcd3/pcfg/{estimate_dist}_dist/samples.tsv", type2prob=probs)