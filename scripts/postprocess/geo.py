from scripts.utils.io import read_file, write_file
from typing import List, Dict
from tqdm import tqdm

def filter_geo(lines):
    column_names = {
        "city": ["city_name", "population", "country_name", "state_name"],  # city
        "border_info": ["border", "state_name"],  # border_info
        "highlow": ["highest_elevation", "lowest_point", "highest_point", "lowest_elevation", "state_name"],  # highlow
        "lake": ["lake_name", "area", "country_name", "state_name"],  # lake
        "mountain": ["mountain_name", "mountain_altitude", "state_name", "country_name"],  # mountain
        "river": ["river_name", "length", "traverse", "country_name"],  # river
        "state": ["capital", "density", "state_name", "population", "area", "country_name"],  # state,
    }
    type_to_column = {
        "char": ["state_name", "city_name", "country_name", "border",
                      "highest_elevation", "lowest_point", "highest_point", "lowest_elevation",
                 "river_name", "lake_name", "traverse", "mountain_name", "capital"],
        "digit": ["population", "area", "density", "length", "montain_altitude"],
    }

    column_to_type = {}
    for k in type_to_column:
        for v in type_to_column[k]:
            column_to_type[v] = k
    # print(column_to_type)
    GRAMMAR_DICTIONARY = {}
    GRAMMAR_DICTIONARY["country_name"] = ['"usa"']
    GRAMMAR_DICTIONARY["digit_value"] = ['750', '0', '150000']
    GRAMMAR_DICTIONARY['state_name'] = ['"oregon"', '"georgia"', '"wisconsin"', '"montana"',
                                        '"colorado"', '"west virginia"', '"hawaii"', '"new hampshire"',
                                        '"washington"', '"florida"', '"north dakota"', '"idaho"',
                                        '"minnesota"', '"tennessee"', '"vermont"', '"kentucky"',
                                        '"alabama"', '"oklahoma"', '"maryland"', '"nebraska"',
                                        '"iowa"', '"kansas"', '"california"', '"wyoming"',
                                        '"massachusetts"', '"missouri"', '"nevada"', '"south dakota"',
                                        '"utah"', '"rhode island"', '"new york"', '"new jersey"',
                                        '"indiana"', '"new mexico"', '"maine"', '"illinois"',
                                        '"louisiana"', '"michigan"', '"mississippi"', '"ohio"',
                                        '"south carolina"', '"arkansas"', '"texas"', '"virginia"',
                                        '"pennsylvania"', '"north carolina"', '"alaska"', '"arizona"',
                                        '"delaware"']
    GRAMMAR_DICTIONARY['river_name'] = ['"north platte"',
                                        '"chattahoochee"', '"rio grande"', '"potomac"']
    GRAMMAR_DICTIONARY['mountain_name'] = ['"mckinley"', '"whitney"']
    GRAMMAR_DICTIONARY['place'] = ['"death valley"',
                                   '"mount mckinley"', '"guadalupe peak"']
    GRAMMAR_DICTIONARY['city_name'] = ['"detroit"', '"plano"', '"des moines"', '"boston"',
                                       '"salem"', '"fort wayne"', '"houston"', '"portland"',
                                       '"montgomery"', '"minneapolis"', '"tempe"', '"boulder"',
                                       '"seattle"', '"columbus"', '"dover"', '"indianapolis"',
                                       '"san antonio"', '"albany"', '"flint"', '"chicago"',
                                       '"miami"',
                                       '"scotts valley"', '"san francisco"', '"springfield"',
                                       '"sacramento"', '"salt lake city"', '"new orleans"', '"atlanta"',
                                       '"tucson"', '"denver"', '"riverside"', '"erie"',
                                       '"san jose"', '"durham"', '"kalamazoo"', '"baton rouge"',
                                       '"san diego"', '"pittsburgh"', '"spokane"', '"austin"',
                                       '"rochester"', '"dallas"']
    GRAMMAR_DICTIONARY['capital'] = GRAMMAR_DICTIONARY['city_name']
    digit_coloumns = ["population", "area", "density", "length", "montain_altitude"]

    def isdigit(token):
        if token in type_to_column["digit"]:
            return True
        elif "Count" in token or "Min" in token or "Max" in token or "Sum" in token:
            return True
        elif token in GRAMMAR_DICTIONARY["digit_value"]:
            return True
        return False
    output = []
    for line in lines:
        # print(line)
        append = True
        tokens = line.split()
        if "JOIN" in tokens or "WHERE" not in tokens:
            append = False
        for i, tok in enumerate(tokens):
            # print(tok, append)
            if "Max" in tok or "Min" in tok or "Sum" in tok:
                if "(" in tok and ")" in tok:
                    lid, rid = tok.index("("), tok.index(")")
                    column = tok[lid+1:rid]
                    if column not in digit_coloumns:
                        append = False
            if "Count" in tok:
                if "(" in tok and ")" in tok:
                    lid, rid = tok.index("("), tok.index(")")
                    column = tok[lid+1:rid]
                    if isdigit(column):
                        append = False
            if tok == "=":
                if tokens[i-1] in GRAMMAR_DICTIONARY:
                    if tokens[i+1] in GRAMMAR_DICTIONARY[tokens[i-1]]:
                        pass
                    elif tokens[i+1] in type_to_column[column_to_type[tokens[i-1]]]:
                            pass
                    elif "(" in tokens[i+1]:
                        pass
                    elif "\"" in tokens[i+1] and i+2 < len(tokens):
                        if tokens[i+1]+" "+tokens[i+2] in GRAMMAR_DICTIONARY[tokens[i-1]]:
                            pass
                        else:
                            append = False
                    else:
                        append = False
                elif isdigit(tokens[i-1]):
                    if isdigit(tokens[i+1]):
                        pass
                    elif "(" in tokens[i+1]:
                        pass
                    else:
                        append = False
                elif tok in type_to_column["char"]:
                    if not isdigit(tokens[i+1]):
                        pass
                    elif "(" in tokens[i + 1]:
                        pass
                    else:
                        append = False
            if tok in [">", "<"]:
                if isdigit(tokens[i-1]) and isdigit(tokens[i+1]):
                    pass
                elif isdigit(tokens[i-1]) and "(" in tokens[i+1]:
                    pass
                else:
                    append = False
            if tok == "IN":
                if "(" not in tokens[i+1]:
                    append = False
        if line in output:
            append = False
        if append:
            output.append(line)

    return output


def postprocess_geo(schema_file, mr_file, tgt_file):
    schema_lines = read_file(schema_file)
    table_attr = {}
    for line in schema_lines:
        line = line.lower()
        table_name, attr_name, _, _, _ = line.rstrip().split(", ")
        if table_name == "table name" or table_name=="-":
            continue
        if table_name not in table_attr:
            table_attr[table_name] = []
        table_attr[table_name].append(attr_name)

    alias_state = {k:0 for k in table_attr}
    # print(alias_state)
    def add_alias_for_this_sql(sql_tokens: List[str], alias_state:Dict=None, start_idx=0):
        this_sql_tokens = sql_tokens[start_idx:]
        table_name = this_sql_tokens[this_sql_tokens.index("FROM")+1]
        assert table_name in alias_state

        tgt_sql_tokens = []
        end_idx = len(sql_tokens)
        ignore_idx = -1
        ignore_right_bracket = False
        for i in range(start_idx, len(sql_tokens)):
            tok = sql_tokens[i]
            # print(tgt_sql_tokens)
            if i < ignore_idx:
                continue
            if tok not in table_attr[table_name]:
                tgt_sql_tokens.append(tok)
                if tok == "(":
                    alias_new_state = alias_state.copy()
                    alias_new_state[table_name] += 1
                    new_sql, new_idx = add_alias_for_this_sql(sql_tokens, alias_new_state, start_idx=i+1)
                    tgt_sql_tokens += new_sql
                    ignore_idx = new_idx
                elif "(" in tok:
                    ignore_right_bracket = True
                elif ")" in tok:
                    if ignore_right_bracket:
                        ignore_right_bracket = False
                    else:
                        return tgt_sql_tokens, i+1
                elif tok == table_name:
                    tablealias = "{}alias{}".format(table_name, alias_state[table_name])
                    tgt_sql_tokens.append("AS")
                    tgt_sql_tokens.append(tablealias)
            else:
                tablealias = "{}alias{}".format(table_name, alias_state[table_name])
                # alias_state[table_name] += 1
                tgt_sql_tokens.append("{}.{}".format(tablealias, tok))

        return tgt_sql_tokens, end_idx

    mr_lines = read_file(mr_file)
    mr_lines = filter_geo(mr_lines)
    seen_sqls = []
    output = []
    for i, line in tqdm(enumerate(mr_lines)):
        # if i != 45:
        #     continue
        # print(line)
        if "JOIN" in line:
            # tokens = line.split()
            # filter = False
            # filtered_tokens = []
            # for j in range(length(tokens)):
            #     if tokens[j] == "JOIN":
            #         filter = True
            #     if filter and not tokens[j].islower() and tokens[j] not in ["JOIN", "ON", "AND"] and length(tokens[j]) > 1:
            #         filter = False
            #     if not filter:
            #         filtered_tokens.append(tokens[j])
            #
            # line = " ".join(filtered_tokens)
            # join_idxΩ_idx = tokens.index("JOIN")

            # tokens = tokens[:join_idx]+tokens[where_idx:]
            # line = " ".join(tokens)
            continue
        # line = line.replace("Count", "COUNT")
        line = line.replace("(", "( ")
        line = line.replace(")", " )")
        sql_tokens = line.rstrip().split()
        tgt_sql_tokens, _ = add_alias_for_this_sql(sql_tokens, alias_state=alias_state)
        # print(tgt_sql_tokens)
        tgt_sql_tokens += ";"
        sql =  " ".join(tgt_sql_tokens)
        # if sql not in seen_sqls:
        #     seen_sqls.append(sql)
        newline = "{}\t{}\n".format(i, " ".join(tgt_sql_tokens))
        output.append(newline)
        # print(i, " ".join(tgt_sql_tokens))
        # raise NotImplementedError
    write_file(tgt_file, output)

if __name__ == "__main__":
    # postprocess_geo("text2sql-data/data/geography-schema.csv",\
    # "../tensor2struct-public/experiments/sql2nl/data-ssp-synthetic/500_64_uni",
    #                 "data/geoquery/orig/newtgt_pcfg_500_64_uni.tsv")

    # postprocess_geo("text2sql-data/data/geography-schema.csv", \
    #                 "../tensor2struct-public/experiments/sql2nl/data-ssp-synthetic/500_64_train",
    #                 "data/geoquery/orig/newtgt_pcfg_500_64_train.tsv")
    #
    # postprocess_geo("text2sql-data/data/geography-schema.csv", \
    #                 "../tensor2struct-public/experiments/sql2nl/data-ssp-synthetic/50_64_train",
    #                 "data/geoquery/orig/newtgt_pcfg_50_64_train.tsv")

    #
    # postprocess_geo("text2sql-data/data/geography-schema.csv", \
    #                 "../tensor2struct-public/experiments/sql2nl/data-ssp-synthetic/100_512_test",
    #                 "data/geoquery/orig/newtgt_pcfg_100_512_test.tsv")
    #
    # postprocess_geo("text2sql-data/data/geography-schema.csv", \
    #                 "../tensor2struct-public/experiments/sql2nl/data-ssp-synthetic/100_512_test",
    #                 "data/geoquery/orig/newtgt_pcfg_100_debug.tsv")

    # test_example = ["SELECT state_name FROM state WHERE state_name = \"new york\""]
    # print(filter_geo(test_example))
    postprocess_geo("text2sql-data/data/geography-schema.csv", \
                    "../tensor2struct-public/experiments/sql2nl/data-ssp-synthetic/500_256_test",
                    "data/geoquery/orig/newtgt_pcfg_500_256_test.tsv")