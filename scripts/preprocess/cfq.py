import collections
import os
import string
from typing import Any, Dict, List, Tuple
import json
import mmap
from tqdm import tqdm
import tarfile
from pathlib import Path

import collections
import re
from scripts.utils.io import write_file, read_file, mkdir

reverse_dic = {}
reverse_dic['film.film.executive_produced_by'] = 'film.producer.films_executive_produced'
reverse_dic['film.film.directed_by'] = 'film.director.film'
reverse_dic['film.film.written_by'] = 'film.writer.film'
reverse_dic['influence.influence_node.influenced_by'] = 'influence.influence_node.influenced'
reverse_dic['film.film.edited_by'] = 'film.editor.film'
reverse_dic[
    'film.film.produced_by|ns:film.film.production_companies'] = 'film.producer.film|ns:film.production_company.films'
reverse_dic[
    'people.person.employment_history/ns:business.employment_tenure.company'] = 'business.employer.employees/ns:business.employment_tenure.person'
reverse_dic['organization.organization.founders'] = 'organization.organization_founder.organizations_founded'
reverse_dic[
    'film.film.distributors/ns:film.film_film_distributor_relationship.distributor'] = 'film.film_distributor.films_distributed/ns:film.film_film_distributor_relationship.film'
reverse_dic[
    'organization.organization.acquired_by/ns:business.acquisition.acquiring_company'] = 'organization.organization.companies_acquired/ns:business.acquisition.company_acquired'
# Also add trimmed relation mappings
reverse_dic['film.film.production_companies'] = 'film.production_company.films'
reverse_dic['business.employment_tenure.company'] = 'business.employment_tenure.person'
reverse_dic['film.film_film_distributor_relationship.distributor'] = 'film.film_film_distributor_relationship.film'
reverse_dic['business.acquisition.acquiring_company'] = 'business.acquisition.company_acquired'

trim_for_T5 = True
replace_for_T5 = True
merge_conjuncts = True
trim_FILTER = False
normalize_relation = True
add_brackets = True
sort_alphabetically = True

def tokenize_punctuation(text):
  text = map(lambda c: ' %s ' % c if c in string.punctuation else c, text)
  return ' '.join(''.join(text).split())

def preprocess_sparql(query):
  """Do various preprocessing on the SPARQL query."""
  # Tokenize braces.
  query = query.replace('count(*)', 'count ( * )')

  tokens = []
  for token in query.split():
    # Replace 'ns:' prefixes.
    if not trim_for_T5:
        if token.startswith('ns:'):
          token = token[3:]
        # Replace mid prefixes.
        if token.startswith('m.'):
          token = 'm_' + token[2:]
    #  The raw program contains ns:m.2xxx token. Replace . with _ are applied whether trim_for_t5 is true or false.
    if token.startswith("ns:m."):
        token = "ns:m_"+token[5:]
    tokens.append(token)

  return ' '.join(tokens).replace('\\n', ' ')

def preprocess_program(program):
    """Switches OOV T5 tokens to in-vocabulary tokens."""
    program_processed = str(program)
    program_processed = program_processed.replace("{", "lb")
    program_processed = program_processed.replace("}", "rb")
    program_processed = program_processed.replace("^", "#")
    return program_processed


def get_encode_decode_pair(sample):
  # Apply some simple preprocessing on the tokenizaton, which improves the
  # performance of the models significantly.
  encode_text = tokenize_punctuation(sample['questionPatternModEntities'])
  decode_text = preprocess_sparql(sample['sparqlPatternModEntities'])
  return (encode_text, decode_text)


def load_data(fname: str) -> Tuple[List[str], List[str]]:
    # Split the JSON manually, otherwise it requires infinite RAM and is very slow.
    pin = "complexityMeasures".encode()
    offset = 1
    cnt = 0

    inputs = []
    outputs = []

    with open(fname, "r") as f:
        data = mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ)
        pbar = tqdm(total=len(data))
        pbar.update(offset)

        while True:
            pos = data.find(pin, offset + 6)
            if pos < 0:
                this = data[offset: len(data) - 2]
            else:
                this = data[offset: pos - 5]
                new_offset = pos - 4
                pbar.update(new_offset - offset)
                offset = new_offset
            d = json.loads(this.decode())
            # sent = tokenize_punctuation(d["questionPatternModEntities"])
            inputs.append(tokenize_punctuation(d["questionPatternModEntities"]))
            # sparql = preprocess_sparql(d["sparqlPatternModEntities"])
            outputs.append(preprocess_sparql(d["sparqlPatternModEntities"]))

            cnt += 1
            if pos < 0:
                break

    return inputs, outputs

def write_dataset(dirpath):
    cfq_dirpath = dirpath
    with tarfile.open('{}/cfq1.1.tar.gz'.format(cfq_dirpath), "r") as tf:
        tf.extractall(path=cfq_dirpath)

    src_sentences, tgt_sentences = load_data('{}/cfq/dataset.json'.format(dirpath))

    for split_name in ['mcd1', 'mcd2', 'mcd3']:
        split_path = '{}/cfq/splits/{}.json'.format(dirpath, split_name)
        with open(split_path, "r") as split_f:
            ind = json.loads(split_f.read())
            index_table = {
                "train": ind["trainIdxs"],
                "dev": ind["devIdxs"],
                "test": ind["testIdxs"]
            }
        tgt_split_name = split_name
        for filename in ['train', 'dev', 'test']:
            output = []
            mkdir('{}/{}/'.format(cfq_dirpath, tgt_split_name))
            filepath = '{}/{}/{}_raw.tsv'.format(cfq_dirpath, tgt_split_name, filename)
            for i, idx in enumerate(index_table[filename]):
                line = '{}\t{}\n'.format(src_sentences[idx], tgt_sentences[idx])
                output.append(line)
            write_file(filepath, output)


def get_trimmed_relations(train_examples):
    """Gets a mapping between relations and their short naming."""
    relations = set()
    for example in train_examples:
        example_src, example_tgt = example.rstrip().split("\t")
        tokens = example_tgt.split()
        for token in tokens:
            if "." in token and token != ".":  # Identify tokens that are relations.
                relations.add(token)
            # if "people.person.nationality" in token and token != "ns:people.person.nationality":
            #     print(example)
            #     raise RuntimeError()

    trimmed_relations = {}
    relations_original = set(relations)
    for relation in relations_original:
        # Trim relations that contain "ns:".
        if "ns:" in relation and not relation.startswith("#") and not relation.startswith("^"):
            relation_trimmed = relation.split("ns:")[-1]
            if relation_trimmed in relations:
                raise RuntimeError(
                    "The trimmed relation {} is not unique!".format(relation_trimmed))
            relations.add(relation_trimmed)
            trimmed_relations[relation] = relation_trimmed
    return trimmed_relations

def get_program_parts(program):
    """Parses a SPARQL program into a prefix and conjuncts."""
    # Remove the closing bracket and split on opening bracket.
    if not program.endswith(" rb"):
      raise ValueError("Wrong program format.")
    program_no_closing = program[:-3]
    parts = program_no_closing.split(" lb ")
    if len(parts) != 2:
      raise ValueError("Wrong program format.")
    prefix = parts[0]
    conjuncts_str = parts[1]
    conjuncts = conjuncts_str.split(" . ")
    return prefix, conjuncts

def convert_example(example, trimmed_relations,
                    # trim_for_T5 = False,
                    # replace_for_T5 = False,
                    # merge_conjuncts = False,
                    # trim_FILTER = False,
                    # normalize_relation = False,
                    # add_brackets = False
                    ):

    example_src, example_tgt = example.rstrip().split("\t")

    # return "{}\t{}\n".format(example_src, f_reversible(example, trim_mapping))

    def get_subj_rel_to_objects(conjuncts):
        """Merges conjuncts that share the same subject and relation."""
        subj_rel_to_objects = collections.OrderedDict()
        for conjunct in conjuncts:
            if conjunct.startswith("FILTER"):  # Keep FILTER conjunts as is.
                subj_rel_to_objects[conjunct] = None
            else:
                subj, rel, obj = conjunct.split()  # A (subj, rel, obj) triple.
                if rel == "a":  # Keep unary conjuncts as is.
                    subj_rel_to_objects[conjunct] = None
                else:  # Handle a binary conjunct.
                    if rel in reverse_dic and normalize_relation:
                        rel = reverse_dic[rel]
                        subj, obj = obj, subj
                    subj_rel = (subj, rel)
                    if subj_rel not in subj_rel_to_objects:
                        subj_rel_to_objects[subj_rel] = []
                    subj_rel_to_objects[subj_rel].append(obj)
        return subj_rel_to_objects

    def get_conjuncts_reversible(
            subj_rel_to_objects,
            subj_objs_to_rels):
        """Generates conjuncts in their reversible intermediate representation."""
        conjuncts_reversible = []
        added_subj_objs = []
        for subj_rel, objects in subj_rel_to_objects.items():
            if objects is None:  # Only wrap the conjunct with parentheses.
                if add_brackets:
                    conjuncts_reversible.append("( {} )".format(subj_rel))
                else:
                    conjuncts_reversible.append("{}".format(subj_rel))
            else:
                # Prepare conjunct in the form of (s , (r_1 r_2 ...) (o_1 , o_2 ...)).
                subj, _ = subj_rel
                objects_tup = tuple(objects)
                if (objects_tup, subj) in added_subj_objs:
                    # Already handled the conjuncts with this subject and objects list.
                    continue
                else:
                    added_subj_objs.append((objects_tup, subj))
                if add_brackets:
                    conjunct_reversible = "( {} ( {} ) ( {} ) )".format(
                        subj, " , ".join(subj_objs_to_rels[(objects_tup, subj)]),
                        " , ".join(objects))
                else:
                    conjunct_reversible = "{} {} {}".format(
                        subj, " ".join(subj_objs_to_rels[(objects_tup, subj)]),
                        " ".join(objects))
                conjuncts_reversible.append(conjunct_reversible)
        return conjuncts_reversible

    program_str = example_tgt
    # Replace oov tokens for T5
    if replace_for_T5:
        program_str = preprocess_program(program_str)

    # Trim long relations.
    if trim_for_T5:
        program_str = str(program_str)
        # Sort relations in the reverse order to avoid bad replacement.
        # trimmed_relations = get_trimmed_relations(train_examples=train)
        sorted_relations = sorted(
            trimmed_relations.keys(),
            key=lambda x: x.count("ns:"),
            reverse=True)
        for relation in sorted_relations:
            relation_trimmed = trimmed_relations[relation]
            program_str = program_str.replace(relation, relation_trimmed)

    # Merge conjuncts e.g. (s1,r1,o1), (s1,r1,o2) into (s1,r1,o1,o2)
    if merge_conjuncts:
        prefix, conjuncts = get_program_parts(program_str)

        # Prepare subject-relation to objects map.
        subj_rel_to_objects = get_subj_rel_to_objects(conjuncts)

        # Prepare subject-objects to relations map.
        subj_objs_to_rels = collections.defaultdict(list)
        for subj_rel, objects in subj_rel_to_objects.items():
            if objects is not None:
                objects_tuple = tuple(objects)
                subj, rel = subj_rel
                key = (objects_tuple, subj)
                subj_objs_to_rels[key].append(rel)

        conjuncts_reversible = get_conjuncts_reversible(subj_rel_to_objects,
                                                        subj_objs_to_rels)
        # Sort the conjunctions again! We do this to avoid triming relations disturbed the original alphabetical order.
        # This might be a little unfair?
        if sort_alphabetically:
            conjuncts_reversible = sorted(list(conjuncts_reversible))

        # add leaky brackets
        program_str = "{} lb {} rb".format(prefix, " . ".join(conjuncts_reversible))

    # Trim the ending . and } symbol in the FILTER term
    if trim_FILTER:
        prog = re.compile(r"FILTER [^.]+ [.}]")
        filter_matches = prog.findall(program_str)
        # print(program_str)
        for filter_match in filter_matches:
            print(filter_match)
            program_str = program_str.replace(filter_match, filter_match[:-2])
        # print(program_str)
        # if length(filter_matches) == 2:
        #     raise ValueError("FILTER term not found in {}".format(program_str))

    return "{}\t{}\n".format(example_src, program_str)


def convert_corpus(data_dir):
    f_names = {"train.tsv": "train_raw.tsv", "dev.tsv": "dev_raw.tsv", "test.tsv": "test_raw.tsv"}
    f_examples = {}
    for f in f_names:
        examples = read_file(data_dir+f_names[f])
        f_examples[f] = examples
    trim_mapping = get_trimmed_relations(f_examples["train.tsv"])
    for f in f_examples:
        converted_examples = [convert_example(example, trim_mapping) for example in f_examples[f]]
        write_file(data_dir+f, converted_examples)
        print("Coverted {} sentences into {}".format(len(converted_examples), data_dir+f))

if __name__ == "__main__":

    # Extract raw MCD data. These data is made with minial preprocess steps consisting of 1) tokenization punctuation
    # 2) remove \n symbols to get one-line MR
    # 3) replace m.xxx with m_xxx
    write_dataset("data/cfq/")

    # Heavy preprocess for raw MCD data
    convert_corpus("data/cfq/mcd1/")
    convert_corpus("data/cfq/mcd2/")
    convert_corpus("data/cfq/mcd3/")
