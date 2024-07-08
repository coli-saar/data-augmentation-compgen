import random
import nltk

random.seed(0)

def normalize(probs):
    # leftover_prob = 1-sum(probs)
    # probs = probs + leftover_prob/length(probs)
    leftover_prob = sum(probs)
    probs = [prob / leftover_prob for prob in probs ]
    return probs

def get_word_probs(mrs, num=0, add_quotes=True, dense_prob=0):
    # dense_prob = dense_prob
    if num > 0:
        dense_probs = [dense_prob/num for _ in range(num)]
        left_probs = [(1.0-dense_prob)/(len(mrs)-num) for _ in mrs[num:]]
        probs = normalize(dense_probs+left_probs)
    else:
        probs = [1.0/len(mrs) for _ in mrs]
        probs = normalize(probs)
    rhs_items = []
    for mr in mrs:
        if add_quotes:
            rhs = "\""+mr+"\""
        else:
            rhs = mr
        rhs_items.append(rhs)
    rhs_grammar_str = " | ".join("{} [{}]".format(n, p) for n, p in zip(rhs_items, probs))
    return rhs_grammar_str

unary_args = ['people.person', 'film.cinematographer', 'film.film',
              'film.film_art_director', 'business.employer', 'film.producer',
              'film.actor', 'film.writer', 'film.director', 'film.editor',
              'film.production_company', 'film.film_costumer_designer',
              'fictional_universe.fictional_character', 'film.film_distributor']

binary_args = ['fictional_universe.marriage_of_fictional_characters.spouses',
               'influence.influence_node.influenced',
               'fictional_universe.sibling_relationship_of_fictional_characters.siblings',
               'film.writer.film', 'film.director.film',
               'film.performance.film', 'film.film_costumer_designer.costume_design_for_film',
               'film.production_company.films',
               'organization.organization_founder.organizations_founded',
               'film.producer.films_executive_produced', 'business.employment_tenure.person',
               'film.performance.character', 'organization.organization_relationship.child',
               'organization.organization_relationship.parent',
               'film.film_film_distributor_relationship.film', 'film.editor.film',
               'film.film.prequel', 'film.film.sequel',
               'film.cinematographer.film', 'film.performance.actor',
               'film.film_art_director.films_art_directed',
               'business.acquisition.company_acquired',
               'film.film.film_art_direction_by', 'film.film.cinematography',
               'film.film.costume_design_by']

other_words = ['SELECT', 'count', '(', '*', ')', 'WHERE', 'lb', '?x0', '?x1', 'M1', ',',
               'M2', 'a', 'FILTER', '!=', 'rb', 'M0', 'ns:m_05zppz', 'M3', 'M4', 'DISTINCT',
               'M5', 'M6', 'ns:m_0f8l9c', 'ns:m_06mkj', '?x2', 'ns:m_0b90_r', 'ns:m_09c7w0',
               'ns:m_03rjj', 'ns:m_0d0vqn', 'ns:m_02zsn', 'ns:m_0d060g', 'ns:m_0345h', '?x3',
               'ns:m_03_3d', 'ns:m_07ssc', 'ns:m_059j2', 'ns:m_0d05w3', 'M7', 'M8', '?x4',
               'M9', '?x5']

gender_rels = 'people.person.gender'
gender_var_rels = '#people.person.gender'
nation_rels = 'people.person.nationality'
nation_var_rels = '#people.person.nationality'
gender_values = ['ns:m_05zppz', 'ns:m_02zsn']
nation_values = ['ns:m_0f8l9c', 'ns:m_06mkj', 'ns:m_0b90_r', 'ns:m_09c7w0', 'ns:m_03rjj',
                 'ns:m_0d0vqn', 'ns:m_0d060g', 'ns:m_0345h', 'ns:m_03_3d', 'ns:m_07ssc',
                 'ns:m_059j2', 'ns:m_0d05w3']
FILMTYPE = 'FILMTYPE'
ORGTYPE = 'ORGTYPE'
PEOPLETYPE = 'PEOPLETYPE'
GENDERTYPE = 'GENDERTYPE'
NATIONTYPE = 'NATIONTYPE'

GRAMMAR_DICTIONARY = {}
GRAMMAR_DICTIONARY["all"] = {}
GRAMMAR_DICTIONARY["all"]["binary"] = binary_args +[gender_var_rels, nation_var_rels, gender_rels, nation_rels]
GRAMMAR_DICTIONARY["all"]["unary"] = unary_args


GRAMMAR_DICTIONARY["film"] = {}
# Accept FILMTYPE, PEOPLETYPE
GRAMMAR_DICTIONARY["film"]["binary_by"] = ['film.film.film_art_direction_by', 'film.film.costume_design_by',
                                           'film.film.cinematography', 'film.performance.actor',]
                                           # 'film.performance.character']
# Accept FILMTYPE, FILMTYPE
GRAMMAR_DICTIONARY["film"]["binary_of"] = ['film.film.prequel', 'film.film.sequel',]
# Accept PEOPLETYPE, FILMTYPE
GRAMMAR_DICTIONARY["film"]["binary"] = ['film.writer.film', 'film.director.film', 'film.performance.film',
                                        'film.film_costumer_designer.costume_design_for_film',
                                        'film.production_company.films', 'film.producer.films_executive_produced',
                                        'film.film_film_distributor_relationship.film', 'film.editor.film',
                                        'film.cinematographer.film', 'film.film_art_director.films_art_directed',
                                        'film.performance.character']
# Accept FILMTYPE
GRAMMAR_DICTIONARY["film"]["unary"] = ['film.film', ]
GRAMMAR_DICTIONARY["film"]["type"] = [FILMTYPE]

GRAMMAR_DICTIONARY["organization"] = {}
# Accept ORGTYPE, ORGTYPE
GRAMMAR_DICTIONARY["organization"]["binary"] = ['organization.organization_relationship.child',
                                                'organization.organization_relationship.parent',
                                                'business.acquisition.company_acquired']
# Accept ORGTYPE, FILMTYPE
GRAMMAR_DICTIONARY["organization"]["binary_produce"] = ['film.production_company.films', 'film.film_film_distributor_relationship.film',
                                                        'film.writer.film', 'film.director.film', 'film.film_costumer_designer.costume_design_for_film',
                                                        'film.producer.films_executive_produced', 'film.editor.film',
                                                        'film.cinematographer.film', 'film.film_art_director.films_art_directed']
# Accept PEOPLETYPE, ORGTYPE
GRAMMAR_DICTIONARY["organization"]["binary_founder"] = ['organization.organization_founder.organizations_founded',
                                                        'film.performance.character']
# Accept ORGTYPE, PEOPLETYPE
GRAMMAR_DICTIONARY["organization"]["binary_employ"] = ['business.employment_tenure.person', '#people.person.nationality']
# Accept ORGTYPE
GRAMMAR_DICTIONARY["organization"]["unary"] = ['film.production_company', 'business.employer',
                                               'film.film_distributor', 'film.cinematographer', 'film.film_art_director',
                                               'film.producer', 'film.actor', 'film.writer', 'film.director', 'film.editor',
                                               'film.film_costumer_designer', 'fictional_universe.fictional_character']
GRAMMAR_DICTIONARY["organization"]["type"] = [ORGTYPE]

GRAMMAR_DICTIONARY["people"] = {}
# Accept PEOPLETYPE, PEOPLETYPE
GRAMMAR_DICTIONARY["people"]["binary"] = ['fictional_universe.marriage_of_fictional_characters.spouses',
                                          'fictional_universe.sibling_relationship_of_fictional_characters.siblings',
                                          'influence.influence_node.influenced',
                                          # 'organization.organization_founder.organizations_founded',
                                          'organization.organization_relationship.child',
                                          'organization.organization_relationship.parent', 'film.performance.character']

GRAMMAR_DICTIONARY["people"]["unary"] = ['people.person', 'film.cinematographer', 'film.film_art_director',
                                         'film.producer', 'film.actor', 'film.writer', 'film.director', 'film.editor',
                                         'film.film_costumer_designer', 'fictional_universe.fictional_character']
GRAMMAR_DICTIONARY["people"]["type"] = [PEOPLETYPE]

GRAMMAR_DICTIONARY["gender"] = {}
GRAMMAR_DICTIONARY["gender"]["binary"] = ['people.person.gender']
GRAMMAR_DICTIONARY["gender"]["binary_of"] = ['#people.person.gender']
GRAMMAR_DICTIONARY["gender"]["type"] = ['GENDERTYPE']
GRAMMAR_DICTIONARY["gender"]["values"] = gender_values

GRAMMAR_DICTIONARY["nation"] = {}
GRAMMAR_DICTIONARY["nation"]["binary"] = ['people.person.nationality']
GRAMMAR_DICTIONARY["nation"]["binary_of"] = ['#people.person.nationality']
GRAMMAR_DICTIONARY["nation"]["binary_employ"] = ['business.employment_tenure.person',]
GRAMMAR_DICTIONARY["nation"]["type"] = ['NATIONTYPE']
GRAMMAR_DICTIONARY["nation"]["values"] = nation_values

GRAMMAR_DICTIONARY["filter"] = {}
GRAMMAR_DICTIONARY["filter"]["type"] = ['FILTERTYPE']

GRAMMAR_DICTIONARY["vars"] = ['?x0', '?x1', '?x2', '?x3', '?x4', '?x5']
GRAMMAR_DICTIONARY["ents"] = ['M0', 'M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7', 'M8', 'M9']
GRAMMAR_DICTIONARY["type"] = ['?x0', '?x1', '?x2', '?x3', '?x4', '?x5',
                                            'M0', 'M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7', 'M8', 'M9']

GRAMMAR_DICTIONARY["all"]["rel2type"] = {}
for x in GRAMMAR_DICTIONARY["all"]["unary"]:
    GRAMMAR_DICTIONARY["all"]["rel2type"][x] = []
    for type in ["film", "organization", "people"]:
        if x in GRAMMAR_DICTIONARY[type]["unary"]:
            GRAMMAR_DICTIONARY["all"]["rel2type"][x].append(GRAMMAR_DICTIONARY[type]["type"][0])
    for x in GRAMMAR_DICTIONARY["all"]["binary"]:
        GRAMMAR_DICTIONARY["all"]["rel2type"][x] = {"arg1":[], "arg2": []}
        for type in ["film", "organization", "people", "gender", "nation"]:
            if type == "film":
                if x in GRAMMAR_DICTIONARY[type]["binary"]:
                    GRAMMAR_DICTIONARY["all"]["rel2type"][x]["arg1"].append(PEOPLETYPE)
                    GRAMMAR_DICTIONARY["all"]["rel2type"][x]["arg2"].append(FILMTYPE)
                if x in GRAMMAR_DICTIONARY[type]["binary_by"]:
                    GRAMMAR_DICTIONARY["all"]["rel2type"][x]["arg1"].append(FILMTYPE)
                    GRAMMAR_DICTIONARY["all"]["rel2type"][x]["arg2"].append(PEOPLETYPE)
                if x in GRAMMAR_DICTIONARY[type]["binary_of"]:
                    GRAMMAR_DICTIONARY["all"]["rel2type"][x]["arg1"].append(FILMTYPE)
                    GRAMMAR_DICTIONARY["all"]["rel2type"][x]["arg2"].append(FILMTYPE)

            if type == "organization":
                if x in GRAMMAR_DICTIONARY[type]["binary"]:
                    GRAMMAR_DICTIONARY["all"]["rel2type"][x]["arg1"].append(ORGTYPE)
                    GRAMMAR_DICTIONARY["all"]["rel2type"][x]["arg2"].append(ORGTYPE)
                if x in GRAMMAR_DICTIONARY[type]["binary_founder"]:
                    GRAMMAR_DICTIONARY["all"]["rel2type"][x]["arg1"].append(PEOPLETYPE)
                    GRAMMAR_DICTIONARY["all"]["rel2type"][x]["arg2"].append(ORGTYPE)
                if x in GRAMMAR_DICTIONARY[type]["binary_produce"]:
                    GRAMMAR_DICTIONARY["all"]["rel2type"][x]["arg1"].append(ORGTYPE)
                    GRAMMAR_DICTIONARY["all"]["rel2type"][x]["arg2"].append(FILMTYPE)
                if x in GRAMMAR_DICTIONARY[type]["binary_employ"]:
                    GRAMMAR_DICTIONARY["all"]["rel2type"][x]["arg1"].append(ORGTYPE)
                    GRAMMAR_DICTIONARY["all"]["rel2type"][x]["arg2"].append(PEOPLETYPE)

            if type == "people":
                if x in GRAMMAR_DICTIONARY[type]["binary"]:
                    GRAMMAR_DICTIONARY["all"]["rel2type"][x]["arg1"].append(PEOPLETYPE)
                    GRAMMAR_DICTIONARY["all"]["rel2type"][x]["arg2"].append(PEOPLETYPE)

            if type == "gender":
                if x in GRAMMAR_DICTIONARY[type]["binary"]:
                    GRAMMAR_DICTIONARY["all"]["rel2type"][x]["arg1"].append(PEOPLETYPE)
                    GRAMMAR_DICTIONARY["all"]["rel2type"][x]["arg2"].append(GENDERTYPE)
                if x in GRAMMAR_DICTIONARY[type]["binary_of"]:
                    GRAMMAR_DICTIONARY["all"]["rel2type"][x]["arg1"].append(GENDERTYPE)
                    GRAMMAR_DICTIONARY["all"]["rel2type"][x]["arg2"].append(PEOPLETYPE)

            if type == "nation":
                if x in GRAMMAR_DICTIONARY[type]["binary"]:
                    GRAMMAR_DICTIONARY["all"]["rel2type"][x]["arg1"].append(PEOPLETYPE)
                    GRAMMAR_DICTIONARY["all"]["rel2type"][x]["arg2"].append(NATIONTYPE)
                if x in GRAMMAR_DICTIONARY[type]["binary_employ"]:
                    GRAMMAR_DICTIONARY["all"]["rel2type"][x]["arg1"].append(NATIONTYPE)
                    GRAMMAR_DICTIONARY["all"]["rel2type"][x]["arg2"].append(PEOPLETYPE)
                if x in GRAMMAR_DICTIONARY[type]["binary_of"]:
                    GRAMMAR_DICTIONARY["all"]["rel2type"][x]["arg1"].append(NATIONTYPE)
                    GRAMMAR_DICTIONARY["all"]["rel2type"][x]["arg2"].append(PEOPLETYPE)

grammar_str = """
S -> prefix main [1.0]
main -> "lb" conjuncts "rb" [1.0]
conjuncts -> conjuncts "." conjunct [0.5] | conjunct [0.5]
conjunct -> Binary_relation [0.33] | Unary_relation [0.33] | Filter_relation [0.34]
Unary_relation -> "(" Film_type "a" Film_unary_arg ")" [0.33] \
                | "(" People_type "a" People_unary_arg ")" [0.33] \
                | "(" Org_type "a" Org_unary_arg ")" [0.34]
Binary_relation -> "(" Film_binary_relation ")" [0.2] \
                | "(" People_binary_relation ")" [0.2] \
                | "(" Org_binary_relation ")" [0.2] \
                | "(" Gender_binary_relation ")" [0.2] \
                | "(" Nation_binary_relation ")" [0.2]
Filter_relation -> "(" "FILTER" "(" Film_type "!=" Film_type ")" ")" [0.2] \
                | "(" "FILTER" "(" People_type "!=" People_type ")" ")" [0.2] \
                | "( FILTER" "(" Org_type "!=" Org_type ")" ")" [0.2] \
                | "( FILTER" "(" Gender_type "!=" Gender_type ")" ")" [0.2] \
                | "( FILTER" "(" Nation_type "!=" Nation_type ")" ")" [0.2]
Film_binary_relation -> People_type "(" Film_binary_relation_types ")" "(" Film_types ")" [0.33] \
                        | Film_type "(" Film_binary_of_relation_types ")" "(" Film_types ")" [0.33] \
                        | Film_type "(" Film_binary_by_relation_types ")" "(" People_types ")" [0.34] 
Film_binary_relation_types -> Film_binary_relation_type [0.5] | Film_binary_relation_types "," Film_binary_relation_type [0.5]
Film_binary_of_relation_types -> Film_binary_of_relation_type [0.5] | Film_binary_of_relation_types "," Film_binary_of_relation_type [0.5]
Film_binary_by_relation_types -> Film_binary_by_relation_type [0.5] | Film_binary_by_relation_types "," Film_binary_by_relation_type [0.5]
Org_binary_relation -> Org_type "(" Org_binary_relation_types ")" "(" Org_types ")" [0.25] \
                        | Org_type "(" Org_binary_employ_relation_types ")" "(" People_types ")" [0.25] \
                        | Org_type "(" Org_binary_produce_relation_types ")" "(" Film_types ")" [0.25] \
                        | People_type "(" Org_binary_found_relation_types ")" "(" Org_types ")" [0.25]
Org_binary_relation_types -> Org_binary_relation_type [0.5] | Org_binary_relation_types "," Org_binary_relation_type [0.5]
Org_binary_employ_relation_types -> Org_binary_employ_relation_type [0.5] | Org_binary_employ_relation_types "," Org_binary_employ_relation_type [0.5]
Org_binary_produce_relation_types -> Org_binary_produce_relation_type [0.5] | Org_binary_produce_relation_types "," Org_binary_produce_relation_type [0.5]
Org_binary_found_relation_types -> Org_binary_found_relation_type [0.5] | Org_binary_found_relation_types "," Org_binary_found_relation_type [0.5]
People_binary_relation -> People_type "(" People_binary_relation_types ")" "(" People_types ")" [1.0]
People_binary_relation_types -> People_binary_relation_type [0.5] | People_binary_relation_types "," People_binary_relation_type [0.5]
Gender_binary_relation -> People_type "(" Gender_binary_relation_type ")" "(" Gender_value ")" [0.5] \
                            | Gender_type "(" Gender_binary_of_relation_type  ")" "(" People_types ")" [0.5]
Nation_binary_relation -> People_type "(" Nation_binary_relation_type ")" "(" Nation_type_or_values ")" [0.33] \
                            | Nation_type "(" Nation_binary_of_relation_type ")" "(" People_types ")" [0.33] \
                            | Nation_type "(" Nation_binary_employ_relation_type ")" "(" People_types ")" [0.34]
Film_types -> Film_type "," Film_types [0.5] | Film_type [0.5]
Org_types -> Org_type "," Org_types [0.5] | Org_type [0.5]
People_types -> People_type "," People_types [0.5] | People_type [0.5]
Nation_type_or_values -> Nation_type_or_value "," Nation_type_or_values [0.5] | Nation_type_or_value [0.5]
Nation_type_or_value -> Nation_type [0.5] | Nation_value [0.5]
Nation_values -> Nation_value "," Nation_values [0.5] | Nation_value [0.5]
prefix -> prefix_count [0.5] | prefix_distinct [0.5]
prefix_count -> "SELECT" "count" "(" "*" ")" "WHERE" [1.0]
prefix_distinct -> "SELECT" "DISTINCT" "?x0" "WHERE" [1.0]
Film_unary_arg -> {Film_unary_arg} 
People_unary_arg -> {People_unary_arg}
Org_unary_arg -> {Org_unary_arg}
Film_binary_relation_type -> {Film_binary_relation_type}
Film_binary_of_relation_type -> {Film_binary_of_relation_type}
Film_binary_by_relation_type -> {Film_binary_by_relation_type}
Org_binary_relation_type -> {Org_binary_relation_type}
Org_binary_employ_relation_type -> {Org_binary_employ_relation_type}
Org_binary_produce_relation_type -> {Org_binary_produce_relation_type}
Org_binary_found_relation_type -> {Org_binary_found_relation_type}
People_binary_relation_type -> {People_binary_relation_type}
Gender_binary_relation_type -> {Gender_binary_relation_type}
Gender_binary_of_relation_type -> {Gender_binary_of_relation_type}
Nation_binary_relation_type -> {Nation_binary_relation_type}
Nation_binary_of_relation_type -> {Nation_binary_of_relation_type}
Nation_binary_employ_relation_type -> {Nation_binary_employ_relation_type}
Film_type -> {Film_type}
People_type -> {People_type}
Org_type -> {Org_type}
Gender_type -> {Gender_type}
Nation_type -> {Nation_type}
Gender_value -> {Gender_value}
Nation_value -> {Nation_value}
""".format(
    Film_unary_arg=get_word_probs(GRAMMAR_DICTIONARY["film"]["unary"]),
    People_unary_arg=get_word_probs(GRAMMAR_DICTIONARY["people"]["unary"]),
    Org_unary_arg=get_word_probs(GRAMMAR_DICTIONARY["organization"]["unary"]),
    Film_binary_relation_type=get_word_probs(GRAMMAR_DICTIONARY["film"]["binary"]),
    Film_binary_of_relation_type=get_word_probs(GRAMMAR_DICTIONARY["film"]["binary_of"]),
    Film_binary_by_relation_type=get_word_probs(GRAMMAR_DICTIONARY["film"]["binary_by"]),
    Org_binary_relation_type=get_word_probs(GRAMMAR_DICTIONARY["organization"]["binary"]),
    Org_binary_employ_relation_type=get_word_probs(GRAMMAR_DICTIONARY["organization"]["binary_employ"]),
    Org_binary_produce_relation_type=get_word_probs(GRAMMAR_DICTIONARY["organization"]["binary_produce"]),
    Org_binary_found_relation_type=get_word_probs(GRAMMAR_DICTIONARY["organization"]["binary_founder"]),
    People_binary_relation_type=get_word_probs(GRAMMAR_DICTIONARY["people"]["binary"]),
    Gender_binary_relation_type=get_word_probs(GRAMMAR_DICTIONARY["gender"]["binary"]),
    Gender_binary_of_relation_type=get_word_probs(GRAMMAR_DICTIONARY["gender"]["binary_of"]),
    Nation_binary_relation_type=get_word_probs(GRAMMAR_DICTIONARY["nation"]["binary"]),
    Nation_binary_of_relation_type=get_word_probs(GRAMMAR_DICTIONARY["nation"]["binary_of"]),
    Nation_binary_employ_relation_type=get_word_probs(GRAMMAR_DICTIONARY["nation"]["binary_employ"]),
    Film_type=get_word_probs(GRAMMAR_DICTIONARY["film"]["type"]),
    People_type=get_word_probs(GRAMMAR_DICTIONARY["people"]["type"]),
    Org_type=get_word_probs(GRAMMAR_DICTIONARY["organization"]["type"]),
    Gender_type=get_word_probs(GRAMMAR_DICTIONARY["gender"]["type"]),
    Nation_type=get_word_probs(GRAMMAR_DICTIONARY["nation"]["type"]),
    Gender_value=get_word_probs(GRAMMAR_DICTIONARY["gender"]["values"]),
    Nation_value=get_word_probs(GRAMMAR_DICTIONARY["nation"]["values"]),
           )

if __name__ == "__main__":

    grammar = nltk.PCFG.fromstring(grammar_str)
    # print(grammar_str)
    for prod in grammar.productions()[:50]:
        left = prod.lhs()
        right = list(prod.rhs())
        print(f"{left} ->", end=" ")
        for item in right:
            print(item, end=" ")
        print("\n")