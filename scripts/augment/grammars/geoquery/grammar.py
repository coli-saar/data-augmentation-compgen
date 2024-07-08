
# from nltk import PCFG
import numpy as np
import random
from pcfg import PCFG
from scripts.utils.io import read_file, write_file
from tqdm import tqdm
import json

# loc_1(arg): with locations arg
# loc_2(arg): located in arg
# most(a, b, c): a set with corresponding b coloumns being the most c
#

GRAMMAR_DICTIONARY = {}

GRAMMAR_DICTIONARY['Query'] = [
    '"answer" "(" City ")"',
    '"answer" "(" Country ")"',
    '"answer" "(" Num ")"',
    '"answer" "(" Place ")"',
    '"answer" "(" State ")"',
    '"answer" "(" River ")"',
]

# Country
GRAMMAR_DICTIONARY['CountryNonterm'] = [
    '"each" "(" Country ")"',
    '"exclude" "(" Country "," Country ")"',
    '"intersection" "(" Country "," Country ")"',
    '"largest" "(" Country ")"',
    '"smallest" "(" Country ")"',
    '"loc_1" "(" City ")"',
    '"loc_1" "(" Place ")"',
    '"loc_1" "(" River ")"',
    '"loc_1" "(" State ")"',
    '"traverse_1" "(" River ")"',
]
GRAMMAR_DICTIONARY['CountryTerm'] = [
    '"countryid" "(" "usa" ")"',
    '"country" "(" "all" ")"',
]

# State
GRAMMAR_DICTIONARY['StateNonterm'] = [
    '"state" "(" State ")"',
    '"smallest" "(" State ")"',
    '"smallest_one" "(" "area_1" "(" State ")" ")"',
    '"smallest_one" "(" "density_1" "(" State ")" ")"',
    '"smallest_one" "(" "population_1" "(" State ")" ")"',
    '"largest" "(" State ")"',
    '"largest_one" "(" "area_1" "(" State ")" ")"',
    '"largest_one" "(" "density_1" "(" State ")" ")"',
    '"largest_one" "(" "population_1" "(" State ")" ")"',
    '"each" "(" State ")"',
    '"exclude" "(" State "," State ")"',
    '"intersection" "(" State "," State ")"',
    '"fewest" "(" State ")"',
    '"most" "(" "state" "(" "loc_1" "(" River ")" ")" ")"',
    '"most" "(" "state" "(" "loc_1" "(" City ")" ")" ")"',
    '"most" "(" "state" "(" "loc_1" "(" Place ")" ")" ")"',
    '"most" "(" "state" "(" "loc_2" "(" Country ")" ")" ")"',
    '"most" "(" "state" "(" "next_to_1" "(" State ")" ")" ")"',
    '"most" "(" "state" "(" "next_to_2" "(" State ")" ")" ")"',
    '"most" "(" "state" "(" "next_to_2" "(" River ")" ")" ")"',
    '"most" "(" "state" "(" "traverse_1" "(" River ")" ")" ")"',
    '"next_to_1" "(" State ")"',
    '"next_to_2" "(" State ")"',
    '"next_to_2" "(" River ")"',
    '"traverse_1" "(" River ")"',
    '"loc_1" "(" River ")"',
    '"capital_2" "(" City ")"',
    '"loc_1" "(" City ")"',
    '"high_point_2" "(" Place ")"',
    '"low_point_2" "(" Place ")"',
    '"loc_1" "(" Place ")"',
    '"loc_2" "(" Country ")"',
]
GRAMMAR_DICTIONARY['StateTerm'] = [
    '"state" "(" "all" ")"',
    '"stateid" "(" StateName ")"',
]
GRAMMAR_DICTIONARY['StateAbbrev'] = ['"\'dc\'"', '"\'pa\'"', '"\'ga\'"', '"\'me\'"', '"\'wa\'"', '"\'tx\'"',
                                     '"\'ma\'"', '"\'sd\'"', '"\'az\'"', '"\'mn\'"', '"\'mo\'"']
# Stateabbrev without quotes
GRAMMAR_DICTIONARY['StateAbbrev_'] = ['"dc"', '"pa"', '"ga"', '"me"', '"wa"', '"tx"',
                                      '"ma"', '"sd"', '"az"', '"mn"', '"mo"']
GRAMMAR_DICTIONARY['StateName'] = ['"\'washington\'"', '"\'kansas\'"', '"\'pennsylvania\'"', '"\'new york\'"', '"\'south carolina\'"', '"\'california\'"', '"\'west virginia\'"', '"\'kentucky\'"', '"\'vermont\'"', '"\'hawaii\'"', '"\'new mexico\'"', '"\'montana\'"', '"\'illinois\'"', '"\'georgia\'"', '"\'louisiana\'"', '"\'indiana\'"', '"\'oklahoma\'"', '"\'utah\'"', '"\'arkansas\'"', '"\'michigan\'"', '"\'alaska\'"', '"\'alabama\'"', '"\'missouri\'"', '"\'wisconsin\'"', '"\'wyoming\'"',
                                   '"\'maine\'"', '"\'florida\'"', '"\'south dakota\'"', '"\'tennessee\'"', '"\'north carolina\'"', '"\'new jersey\'"', '"\'minnesota\'"', '"\'arizona\'"', '"\'new hampshire\'"', '"\'texas\'"', '"\'colorado\'"', '"\'mississippi\'"', '"\'idaho\'"', '"\'oregon\'"', '"\'maryland\'"', '"\'north dakota\'"', '"\'nebraska\'"', '"\'rhode island\'"', '"\'ohio\'"', '"\'massachusetts\'"', '"\'virginia\'"', '"\'nevada\'"', '"\'delaware\'"', '"\'iowa\'"']
# StateName without quotes
GRAMMAR_DICTIONARY['StateName_'] = ['"washington"', '"kansas"', '"pennsylvania"', '"new" "york"', '"south" "carolina"', '"california"', '"west" "virginia"', '"kentucky"', '"vermont"', '"hawaii"', '"new" "mexico"', '"montana"', '"illinois"', '"georgia"', '"louisiana"', '"indiana"', '"oklahoma"', '"utah"', '"arkansas"', '"michigan"', '"alaska"', '"alabama"', '"missouri"', '"wisconsin"', '"wyoming"',
                                    '"maine"', '"florida"', '"south" "dakota"', '"tennessee"', '"north" "carolina"', '"new" "jersey"', '"minnesota"', '"arizona"', '"new" "hampshire"', '"texas"', '"colorado"', '"mississippi"', '"idaho"', '"oregon"', '"maryland"', '"north" "dakota"', '"nebraska"', '"rhode" "island"', '"ohio"', '"massachusetts"', '"virginia"', '"nevada"', '"delaware"', '"iowa"']
# City
GRAMMAR_DICTIONARY['CityNonterm'] = [
    '"city" "(" City ")"',
    '"loc_2" "(" State ")"',
    '"loc_2" "(" Country ")"',
    '"capital" "(" City ")"',
    '"capital" "(" Place ")"',
    '"capital_1" "(" Country ")"',
    '"capital_1" "(" State ")"',
    '"each" "(" City ")"',
    '"exclude" "(" City "," City ")"',
    '"intersection" "(" City "," City ")"',
    '"fewest" "(" City ")"',
    '"largest" "(" City ")"',
    '"largest_one" "(" "density_1" "(" City ")" ")"',
    '"largest_one" "(" "population_1" "(" City ")" ")"',
    '"largest_one" "(" "density_1" "(" City ")" ")"',
    '"smallest" "(" City ")"',
    '"smallest_one" "(" "population_1" "(" City ")" ")"',
    '"loc_1" "(" Place ")"',
    '"major" "(" City ")"',
    '"most" "(" "city" "(" "loc_2" "(" State ")" ")" ")"',
    '"most" "(" "city" "(" "loc_2" "(" Country ")" ")" ")"',
    '"most" "(" "city" "(" "traverse_1" "(" River ")" ")" ")"',
    '"traverse_1" "(" River ")"',
]
GRAMMAR_DICTIONARY['CityTerm'] = [
    '"city" "(" "all" ")"',
    '"capital" "(" "all" ")"',
    '"cityid" "(" CityName "," StateAbbrev ")"',
    '"cityid" "(" CityName "," "_" ")"',
]
GRAMMAR_DICTIONARY['CityName'] = ['"\'washington\'"', '"\'minneapolis\'"', '"\'sacramento\'"', '"\'rochester\'"', '"\'indianapolis\'"', '"\'portland\'"', '"\'new york\'"', '"\'erie\'"', '"\'san diego\'"', '"\'baton rouge\'"', '"\'miami\'"', '"\'kalamazoo\'"', '"\'durham\'"', '"\'salt lake city\'"', '"\'des moines\'"', '"\'pittsburgh\'"', '"\'riverside\'"', '"\'dover\'"', '"\'chicago\'"', '"\'albany\'"', '"\'tucson\'"', '"\'austin\'"',
                                   '"\'san antonio\'"', '"\'houston\'"', '"\'scotts valley\'"', '"\'montgomery\'"', '"\'springfield\'"', '"\'boston\'"', '"\'boulder\'"', '"\'san francisco\'"', '"\'flint\'"', '"\'fort wayne\'"', '"\'spokane\'"', '"\'san jose\'"', '"\'tempe\'"', '"\'dallas\'"', '"\'new orleans\'"', '"\'seattle\'"', '"\'denver\'"', '"\'salem\'"', '"\'detroit\'"', '"\'plano\'"', '"\'atlanta\'"', '"\'columbus\'"']
# Citynames without quotes
GRAMMAR_DICTIONARY['CityName_'] = ['"washington"', '"minneapolis"', '"sacramento"', '"rochester"', '"indianapolis"', '"portland"', '"new" "york"', '"erie"', '"san" "diego"', '"baton" "rouge"', '"miami"', '"kalamazoo"', '"durham"', '"salt" "lake" "city"', '"des" "moines"', '"pittsburgh"', '"riverside"', '"dover"', '"chicago"', '"albany"', '"tucson"', '"austin"',
                                    '"san" "antonio"', '"houston"', '"scotts" "valley"', '"montgomery"', '"springfield"', '"boston"', '"boulder"', '"san" "francisco"', '"flint"', '"fort" "wayne"', '"spokane"', '"san" "jose"', '"tempe"', '"dallas"', '"new" "orleans"', '"seattle"', '"denver"', '"salem"', '"detroit"', '"plano"', '"atlanta"', '"columbus"']
# Num
GRAMMAR_DICTIONARY['NumNonterm'] = [
    'Digit',
    '"area_1" "(" City ")"',
    '"area_1" "(" Country ")"',
    '"area_1" "(" Place ")"',
    '"area_1" "(" State ")"',
    '"count" "(" City ")"',
    '"count" "(" Country ")"',
    '"count" "(" Place ")"',
    '"count" "(" River ")"',
    '"count" "(" State ")"',
    '"density_1" "(" City ")"',
    '"density_1" "(" Country ")"',
    '"density_1" "(" State ")"',
    '"elevation_1" "(" Place ")"',
    '"population_1" "(" City ")"',
    '"population_1" "(" Country ")"',
    '"population_1" "(" State ")"',
    '"size" "(" City ")"',
    '"size" "(" Country ")"',
    '"size" "(" State ")"',
    '"smallest" "(" Num ")"',
    '"sum" "(" Num ")"',
    '"len" "(" River  ")"'
]
GRAMMAR_DICTIONARY['NumTerm'] = [
    'Digit',
]
GRAMMAR_DICTIONARY['Digit'] = ['"0.0"', '"1.0"', '"0"']

# Place
GRAMMAR_DICTIONARY['PlaceNonterm'] = [
    '"loc_2" "(" City ")"',
    '"loc_2" "(" State ")"',
    '"loc_2" "(" Country ")"',
    '"each" "(" Place ")"',
    '"elevation_2" "(" Num ")"',
    '"exclude" "(" Place "," Place ")"',
    '"intersection" "(" Place "," Place ")"',
    '"fewest" "(" Place ")"',
    '"largest" "(" Place ")"',
    '"smallest" "(" Place ")"',
    '"highest" "(" Place ")"',
    '"lowest" "(" Place ")"',
    '"high_point_1" "(" State ")"',
    '"low_point_1" "(" State ")"',
    '"higher_1" "(" Place ")"',
    '"higher_2" "(" Place ")"',
    '"lower_1" "(" Place ")"',
    '"lower_2" "(" Place ")"',
    '"lake" "(" Place ")"',
    '"mountain" "(" Place ")"',
    '"place" "(" Place ")"',
    '"major" "(" Place ")"'
]
GRAMMAR_DICTIONARY['PlaceTerm'] = [
    '"place" "(" "all" ")"',
    '"mountain" "(" "all" ")"',
    '"lake" "(" "all" ")"',
    '"placeid" "(" PlaceName ")"',
]
GRAMMAR_DICTIONARY['PlaceName'] = ['"\'guadalupe peak\'"', '"\'mount whitney\'"',
                                    '"\'mount mckinley\'"', '"\'death valley\'"']
# Placenames without quotes
GRAMMAR_DICTIONARY['PlaceName_'] = ['"guadalupe" "peak"', '"mount" "whitney"',
                                        '"mount" "mckinley"', '"death" "valley"']
# River
GRAMMAR_DICTIONARY['RiverNonterm'] = [
    '"river" "(" River ")"',
    '"loc_2" "(" State ")"',
    '"loc_2" "(" Country ")"',
    '"each" "(" River ")"',
    '"exclude" "(" River "," River ")"',
    '"intersection" "(" River "," River ")"',
    '"fewest" "(" River ")"',
    '"longer" "(" River ")"',
    '"longest" "(" River ")"',
    '"major" "(" River ")"',
    '"most" "(" "river" "(" "loc_2" "(" State ")" ")" ")"',
    '"most" "(" "river" "(" "loc_2" "(" Country ")" ")" ")"',
    '"most" "(" "river" "(" "traverse_2" "(" City ")" ")" ")"',
    '"most" "(" "river" "(" "traverse_2" "(" Country ")" ")" ")"',
    '"most" "(" "river" "(" "traverse_2" "(" State ")" ")" ")"',
    '"shortest" "(" River ")"',
    '"traverse_2" "(" City ")"',
    '"traverse_2" "(" Country ")"',
    '"traverse_2" "(" State ")"',
]
GRAMMAR_DICTIONARY['RiverTerm'] = [
    '"river" "(" "all" ")"',
    '"riverid" "(" RiverName ")"',
]
GRAMMAR_DICTIONARY['RiverName'] = ['"\'chattahoochee\'"', '"\'north platte\'"', '"\'rio grande\'"', '"\'ohio\'"',
                                    '"\'potomac\'"', '"\'missouri\'"', '"\'red\'"', '"\'colorado\'"', '"\'mississippi\'"', '"\'delaware\'"']
# Rivernames without quotes
GRAMMAR_DICTIONARY['RiverName_'] = ['"chattahoochee"', '"north" "platte"', '"rio" "grande"', '"ohio"',
                                    '"potomac"', '"missouri"', '"red"', '"colorado"', '"mississippi"', '"delaware"']
def normalize(probs):
    # leftover_prob = 1-sum(probs)
    # probs = probs + leftover_prob/length(probs)
    leftover_prob = sum(probs)
    probs = [prob / leftover_prob for prob in probs ]
    return probs

def extract_rhs(mrs, num=0, add_quotes=False, flag=False):
    dense_prob = 0.3
    if num > 0:
        dense_probs = [dense_prob/num for _ in range(num)]
        left_probs = [(1.0-dense_prob)/(len(mrs)-num) for _ in mrs[num:]]
        probs = normalize(dense_probs+left_probs)
    else:
        probs = [1.0/len(mrs) for _ in mrs]
        probs = normalize(probs)
    rhs_items = []
    for mr in mrs:
        if flag == True:
            rhs = mr
        else:
            if add_quotes:
                rhs = "\""+mr+"\""
            else:
                rhs = mr
        rhs_items.append(rhs)
    rhs_grammar_str = " | ".join("{} [{}]".format(n, p) for n, p in zip(rhs_items, probs))
    return rhs_grammar_str

query_tables = ["City", "Country", "Place", "State", "River", "Num"]
# print(extract_rhs(GRAMMAR_DICTIONARY["River"]))

grammar_str = """
S -> "answer" "(" Var ")" [1.0]
Var -> {Tables}
City -> CityNonterm [0.5] | CityTerm [0.5]
CityNonterm -> {CityNonterm_rhs}
CityTerm -> {CityTerm_rhs}
CityName -> {CityName_rhs}
State -> StateNonterm [0.5] | StateTerm [0.5]
StateNonterm -> {StateNonterm_rhs}
StateTerm -> {StateTerm_rhs}
StateAbbrev -> {StateAbbrev_rhs}
StateName -> {StateName_rhs}
River -> RiverNonterm [0.5] | RiverTerm [0.5]
RiverNonterm -> {RiverNonterm_rhs}
RiverTerm -> {RiverTerm_rhs}
RiverName -> {RiverName_rhs}
Country -> CountryNonterm [0.5] | CountryTerm [0.5]
CountryNonterm -> {CountryNonterm_rhs}
CountryTerm -> {CountryTerm_rhs}
Num -> NumNonterm [0.5] | NumTerm [0.5]
NumNonterm -> {NumNonterm_rhs}
NumTerm -> {NumTerm_rhs}
Digit -> {Digit_rhs}
Place -> PlaceNonterm [0.5] | PlaceTerm [0.5]
PlaceNonterm -> {PlaceNonterm_rhs}
PlaceTerm -> {PlaceTerm_rhs}
PlaceName -> {PlaceName_rhs}
""".format(Tables=extract_rhs(query_tables),
           CityNonterm_rhs=extract_rhs(GRAMMAR_DICTIONARY["CityNonterm"]),
           CityTerm_rhs=extract_rhs(GRAMMAR_DICTIONARY["CityTerm"]),
           CityName_rhs=extract_rhs(GRAMMAR_DICTIONARY["CityName_"]),
           StateNonterm_rhs=extract_rhs(GRAMMAR_DICTIONARY["StateNonterm"]),
           StateTerm_rhs=extract_rhs(GRAMMAR_DICTIONARY["StateTerm"]),
           StateAbbrev_rhs=extract_rhs(GRAMMAR_DICTIONARY["StateAbbrev_"]),
           StateName_rhs=extract_rhs(GRAMMAR_DICTIONARY["StateName_"]),
           RiverNonterm_rhs=extract_rhs(GRAMMAR_DICTIONARY["RiverNonterm"]),
           RiverTerm_rhs=extract_rhs(GRAMMAR_DICTIONARY["RiverTerm"]),
           RiverName_rhs=extract_rhs(GRAMMAR_DICTIONARY["RiverName_"]),
           CountryNonterm_rhs=extract_rhs(GRAMMAR_DICTIONARY["CountryNonterm"]),
           CountryTerm_rhs=extract_rhs(GRAMMAR_DICTIONARY["CountryTerm"]),
           NumNonterm_rhs=extract_rhs(GRAMMAR_DICTIONARY["NumNonterm"]),
           NumTerm_rhs=extract_rhs(GRAMMAR_DICTIONARY["NumTerm"]),
           Digit_rhs=extract_rhs(GRAMMAR_DICTIONARY["Digit"]),
           PlaceNonterm_rhs=extract_rhs(GRAMMAR_DICTIONARY["PlaceNonterm"]),
           PlaceTerm_rhs=extract_rhs(GRAMMAR_DICTIONARY["PlaceTerm"]),
           PlaceName_rhs=extract_rhs(GRAMMAR_DICTIONARY["PlaceName_"]))


if __name__ == '__main__':
    # print(grammar_str)
    import nltk
    grammar = nltk.PCFG.fromstring(grammar_str)
    # print(grammar_str)
    for prod in grammar.productions()[:50]:
        left = prod.lhs()
        right = list(prod.rhs())
        print(f"{left} ->", end=" ")
        for item in right:
            print(item, end=" ")
        print("\n")
