from pcfg import PCFG
from scripts.utils.io import read_file, write_file
from scripts.augment.grammars.cfq.grammar import *
from scripts.augment.grammars.utils.grammar_utils import binarize_grammar
from tqdm import tqdm

class Conjunct:
    def __init__(self, conjunct):
        self.conjunct = conjunct
        tokens = conjunct.split()
        self.is_nation_value = False
        self.is_gender_value = False
        if tokens[2] == "a":
            self.conj_type = "unary"
            self.arg1 = tokens[1]
            self.arg2 = tokens[3]
        elif tokens[1] == "FILTER":
            self.conj_type = "filter"
            self.arg1 = tokens[tokens.index("!=")-1]
            self.arg2 = tokens[tokens.index("!=")+1]
        else:
            self.conj_type = "binary"
            self.arg1 = tokens[1]
            relation_left_bracket_idx = 2
            relation_right_bracket_idx = tokens.index(")")
            relations = tokens[relation_left_bracket_idx + 1:relation_right_bracket_idx]
            self.relations = [relation for relation in relations if relation != ","]

            args = tokens[relation_right_bracket_idx+2:-2]
            arg2 = []
            for arg in args:
                if arg != "," and arg != self.arg1:
                    arg2.append(arg)
                    self.is_nation_value = True if arg in GRAMMAR_DICTIONARY["nation"]["values"] else self.is_nation_value
                    self.is_gender_value = True if arg in GRAMMAR_DICTIONARY["gender"]["values"] else self.is_gender_value
            # arg2 = [arg for arg in arg2 if arg != "," and arg != self.arg1]
            # remove duplicate arg2 and sort as a list
            self.arg2 = sorted(list(set(arg2)))

        self.get_arg_to_type()

    def get_arg_to_type(self):
        arg2type = {x: set([FILMTYPE, ORGTYPE, PEOPLETYPE, GENDERTYPE, NATIONTYPE]) for x in GRAMMAR_DICTIONARY["type"]}
        if self.conj_type == "unary":
            if self.arg2 in GRAMMAR_DICTIONARY["gender"]["values"]+GRAMMAR_DICTIONARY["nation"]["values"] \
                or self.arg1 in GRAMMAR_DICTIONARY["gender"]["values"]+GRAMMAR_DICTIONARY["nation"]["values"]:
                return arg2type
            allowed_types = set(GRAMMAR_DICTIONARY["all"]["rel2type"][self.arg2])
            # set the intersection of two sets as the type of arg1
            arg2type[self.arg1] = arg2type[self.arg1].intersection(allowed_types)
        elif self.conj_type == "filter":
            pass
        else:
            for rel in self.relations:
                allowed_types = set(GRAMMAR_DICTIONARY["all"]["rel2type"][rel]["arg1"])
                arg2type[self.arg1] = arg2type[self.arg1].intersection(allowed_types)
                for arg in self.arg2:
                    if arg in GRAMMAR_DICTIONARY["gender"]["values"]+GRAMMAR_DICTIONARY["nation"]["values"]:
                        continue
                    allowed_types = set(GRAMMAR_DICTIONARY["all"]["rel2type"][rel]["arg2"])
                    arg2type[arg] = arg2type[arg].intersection(allowed_types)

        self.arg2type = arg2type

    def get_args(self):
        if self.conj_type == "unary":
            return [self.arg1]
        elif self.conj_type == "filter":
            return [self.arg1, self.arg2]
        else:
            return [self.arg1] + self.arg2

class SPARQL_MR:
    def __init__(self, mr):
        self.mr = mr
        start_idx = mr.find("WHERE lb ")
        end_idx = mr.find(" rb")
        self.prefix = mr[:start_idx + 9]
        self.suffix = mr[end_idx:]
        conjuncts_str = mr[start_idx + 9:end_idx]
        self.conjuncts_str = conjuncts_str
        conjuncts = conjuncts_str.split(" . ")
        conjuncts = [conjunct for conjunct in conjuncts if conjunct]
        self.conjuncts = [Conjunct(conjunct) for conjunct in conjuncts] if len(conjuncts) > 0 else []

    def mask(self):
        arg2type = {x: set([FILMTYPE, ORGTYPE, PEOPLETYPE, GENDERTYPE,\
                            NATIONTYPE]) for x in GRAMMAR_DICTIONARY["type"]}
        for conjunct in self.conjuncts:
            # print(conjunct.arg2type)
            for arg in conjunct.arg2type:
                arg2type[arg] = arg2type[arg].intersection(conjunct.arg2type[arg])
        # print(arg2type)
        self.arg2type = arg2type

        mr = self.conjuncts_str

        for arg in arg2type:
            if arg not in mr:
                continue
            assert len(arg2type[arg]) > 0
            if len(arg2type[arg]) == 1:
                mr = mr.replace(arg, list(arg2type[arg])[0])
            else:
                # Cannot randomly sample for each arg independently because
                # Two args may have the same type, and we want to sample the same type for them
                # print(arg_type)
                # arg_type = possible_typecombs[tuple(sorted(list(arg2type[arg])))]
                arg_type = random.sample(arg2type[arg], 1)[0]
                mr = mr.replace(arg, arg_type)
        mr = self.prefix + mr + self.suffix
        return mr


    def __str__(self):
        return self.mr

def mask_variables(data):
    lines = data
    grammar = PCFG.fromstring(grammar_str)
    grammar = binarize_grammar(grammar)
    parser = nltk.ChartParser(grammar)
    output = []
    for line in tqdm(lines):
        src, tgt = line.rstrip().split("\t")
        try:
            mr = SPARQL_MR(tgt)
        except:
            print("Error: {}".format(tgt))
            continue

        new_tgt = mr.mask()
        parse_trees = list(parser.parse(new_tgt.split()))
        while len(parse_trees) == 0:
            new_tgt = mr.mask()
            parse_trees = list(parser.parse(new_tgt.split()))
        output.append("{}\n".format(new_tgt))
    return output