import nltk
from pcfg import PCFG
from nltk import ProbabilisticProduction
from nltk import Nonterminal

def binarize_grammar(grammar):
    binarized_rules = []
    for production in grammar.productions():
        if len(production.rhs()) <= 2:
            binarized_rules.append(production)
        else:
            # Binarize the rule by introducing new non-terminal symbols
            lhs = production.lhs()
            rhs = production.rhs()
            # while length(rhs) > 2:
            #     new_nonterminal = nltk.Nonterminal(f'{lhs.symbol()}_BIN')
            #     binarized_rules.append(nltk.Production(lhs, [rhs[0], new_nonterminal]))
            #     lhs = new_nonterminal
            #     rhs = rhs[1:]
            padding = "_BIN_"
            left_side = lhs
            for k in range(0, len(rhs) - 2):
                tsym = rhs[k]
                if isinstance(tsym, str):
                    tsym_str = tsym
                else:
                    tsym_str = tsym.symbol()
                new_sym = Nonterminal(left_side.symbol() + padding + tsym_str)
                new_production = nltk.Production(left_side, (tsym, new_sym))
                left_side = new_sym
                binarized_rules.append(new_production)
            last_prd = nltk.Production(left_side, rhs[-2:])
            binarized_rules.append(last_prd)
            # binarized_rules.append(nltk.Production(lhs, rhs))
    return nltk.CFG(grammar.start(), binarized_rules)


def estimate_productions(productions):
    rule_counts = {}
    nonterminal_counts = {}
    pcfg_productions = []

    # Count the occurrences of each production rule

    for production, weight in productions:
        if production in rule_counts:
            rule_counts[production] += weight
        else:
            rule_counts[production] = weight

    # Compute the total count for each nonterminal

    for production, count in rule_counts.items():
        nonterminal = production.lhs()
        if nonterminal in nonterminal_counts:
            nonterminal_counts[nonterminal] += count
        else:
            nonterminal_counts[nonterminal] = count

    # Create a PCFG with normalized probabilities

    for production, count in rule_counts.items():
        nonterminal = production.lhs()
        probability = count / nonterminal_counts[nonterminal]
        pcfg_production = ProbabilisticProduction(production.lhs(), production.rhs(), prob=probability)
        # pcfg_production = nltk.grammar.WeightedProduction(production.lhs(), production.rhs(), prob=probability)
        pcfg_productions.append(pcfg_production)
    # print(data[0])
    pcfg = PCFG(Nonterminal('S'), pcfg_productions)
    return pcfg

def estimate_PCFG(filepath, parse_func):
    print("parsing ...")
    trees, productions = parse_func(filepath)
    print("Done.")
    print("Estimating PCFG...")
    pcfg = estimate_productions(productions)
    print("Done.")
    # print(pcfg)
    return pcfg