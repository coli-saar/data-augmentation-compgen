import random
from tqdm import tqdm
from pcfg import PCFG
from scripts.augment.grammars.utils.grammar_utils import *
from scripts.augment.grammars.geoquery.grammar import grammar_str
from scripts.augment.grammars.geoquery.geo_utils import *
from scripts.utils.io import read_file, write_file, mkdir

def parse_geoquery(data_path, postprocess_func=postprocess):
    grammar = PCFG.fromstring(grammar_str)
    grammar = binarize_grammar(grammar)
    parser = nltk.ChartParser(grammar)
    lines = read_file(data_path)
    productions = []
    trees = []
    amb_tree_num = {}
    for line in tqdm(lines):
        src, tgt = line.rstrip().split("\t")
        if postprocess_func is not None:
            # print("Preprocessed tgt: {}".format(tgt))
            tgt = postprocess_func(tgt)
        parse_trees = list(parser.parse(tgt.split()))
        if len(parse_trees) == 0:
            print("Error: {}".format(tgt))
        elif len(parse_trees) > 1:
            if len(parse_trees) not in amb_tree_num:
                amb_tree_num[len(parse_trees)] = 0
            amb_tree_num[len(parse_trees)] += 1
            weight = 1.0 / len(parse_trees)
            for tree in parse_trees:
                trees.append(tree)
                cur_productions = tree.productions()
                productions.extend([(prd, weight) for prd in cur_productions])
        # print("Parse trees: {}".format(parse_trees))
        else:
            for tree in parse_trees:
                trees.append(tree)
                cur_productions = tree.productions()
                productions.extend([(prd, 1.0) for prd in cur_productions])

    return trees, productions

def sample_instances(grammar, num, tgt_path):
    output = []
    pbar = tqdm(total=num)
    MAX_NUM = 99999999
    for sent in tqdm(grammar.generate(MAX_NUM)):
        sent = remove_special_symbols(sent)

        sent = remove_duplicates(sent)

        if len(output) >= num:
            break

        formatted_sent = "None\t{}\n".format(sent)

        if formatted_sent not in output:
            output.append(formatted_sent)
            pbar.update(1)

    write_file(tgt_path, output)

if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("estimate_dist", type=str, help="distribution to estimate")
    args = parser.parse_args()
    estimate_dist = args.estimate_dist

    assert estimate_dist in ["train", "uniform", "test"]

    template_dir = "data/geoquery/template/"
    if estimate_dist != "uniform":
        data_path = f"{template_dir}/{estimate_dist}.tsv"
        pcfg = estimate_PCFG(data_path, parse_func=parse_geoquery)
    else:
        pcfg = PCFG.fromstring(grammar_str)
    mkdir(f"{template_dir}/pcfg/{estimate_dist}_dist")
    sample_instances(pcfg, 30000, f"{template_dir}/pcfg/{estimate_dist}_dist/samples.tsv")

    # len_dir = "data/geoquery/length/"
    # if estimate_dist != "uniform":
    #     data_path = f"{len_dir}/{estimate_dist}.tsv"
    #     pcfg = estimate_PCFG(data_path, parse_func=parse_geoquery)
    # else:
    #     pcfg = PCFG.fromstring(grammar_str)
    # mkdir(f"{len_dir}/pcfg/{estimate_dist}_dist")
    # sample_instances(pcfg, 30000, f"{len_dir}/pcfg/{estimate_dist}_dist/samples.tsv")
