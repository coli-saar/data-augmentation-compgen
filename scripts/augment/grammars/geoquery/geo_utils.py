import os.path
from typing import List, Dict, Union, Set, Tuple
from enum import Enum
from nltk import Tree, ImmutableTree

# from overrides import overrides
# from pyswip import Prolog
import re


GEO_ARITIES = {'stateid': 1, 'place': 1, 'riverid': 1, 'lowest': 1, 'area_1': 1, 'largest': 1, 'mountain': 1,
               'capital': 1, 'river': 1, 'shortest': 1, 'longer': 1, 'high_point_2': 1, 'elevation_1': 1,
               'traverse_1': 1, 'fewest': 1, 'most': 1, 'next_to_1': 1, 'loc_2': 1, 'lake': 1, 'state': 1,
               'traverse_2': 1, 'countryid': 1, 'exclude': 2, 'city': 1, 'high_point_1': 1, 'higher_2': 1, 'placeid': 1,
               'loc_1': 1, 'smallest_one': 1, 'elevation_2': 1, 'intersection': 2, 'size': 1, 'capital_2': 1,
               'capital_1': 1, 'sum': 1, 'highest': 1, 'count': 1, 'smallest': 1, 'cityid': 2, 'len': 1, 'density_1': 1,
               'major': 1, 'longest': 1, 'population_1': 1, 'next_to_2': 1, 'largest_one': 1, 'answer': 1,
               'low_point_2': 1, 'lower_2': 1, 'low_point_1': 1}

# Extracted from the KB
NAMED_ENTITIES = ['aberdeen', 'abilene', 'abingdon', 'ak', 'akron', 'al', 'alabama', 'alameda', 'alaska', 'albany',
                  'albuquerque', 'alexandria', 'alhambra', 'allegheny', 'allentown', 'altoona', 'alverstone',
                  'amarillo', 'anaheim', 'anchorage', 'anderson', 'annapolis', 'ann arbor', 'antero', 'appleton', 'ar',
                  'arizona', 'arkansas', 'arlington', 'arlington heights', 'arvada', 'atlanta',
                  'atlantic ocean', 'auburn', 'augusta', 'aurora', 'austin', 'az', 'backbone mountain', 'bakersfield',
                  'baltimore', 'bangor', 'baton rouge', 'bayonne', 'bear', 'beaumont', 'beaver dam creek', 'becharof',
                  'belford',  'bellevue', 'bennington', 'berkeley', 'bethesda', 'bethlehem',
                  'bianca', 'bighorn', 'big stone lake', 'billings', 'biloxi', 'birmingham', 'bismarck', 'blackburn',
                  'black mesa', 'black mountain', 'bloomington', 'boise', 'bona', 'borah peak', 'boston', 'boulder',
                  'boundary peak', 'brasstown bald', 'bridgeport', 'bristol', 'bristol township', 'brockton',
                  'brookside', 'bross', 'browne tower', 'brownsville', 'buena park', 'buffalo', 'burbank', 'burlington',
                  'butte', 'ca', 'california', 'cambridge', 'camden', 'campbell hill', 'canadian', 'canton', 'carson',
                  'carson city', 'casper', 'castle', 'cedar rapids', 'centerville', 'champaign', 'champlain',
                  'charles mound', 'charleston', 'charlotte', 'chattahoochee', 'chattanooga', 'cheaha mountain',
                  'cheektowaga', 'cherry hill', 'chesapeake', 'cheyenne', 'chicago', 'chula vista', 'churchill',
                  'cicero', 'cimarron', 'cincinnati', 'citrus heights', 'clark fork', 'clearwater', 'cleveland',
                  'clifton', 'clingmans dome', 'clinton', 'co', 'colorado', 'colorado springs',
                  'columbia', 'columbus', 'compton', 'concord', 'connecticut', 'corpus christi', 'costa mesa',
                  'covington', 'cranston', 'crestone', 'crestone needle', 'ct', 'cumberland', 'dakota', 'dallas',
                  'daly city', 'danbury', 'davenport', 'dayton', 'dc', 'de', 'dearborn', 'dearborn heights',
                  'death valley', 'decatur', 'delaware', 'denver', 'des moines', 'detroit',
                  'district of columbia', 'dover', 'downey', 'driskill mountain', 'dubuque', 'duluth', 'dundalk',
                  'durham', 'duval circle', 'eagle mountain', 'east buttress', 'east los angeles', 'east orange',
                  'edison', 'elbert', 'el cajon', 'el diente', 'elgin', 'elizabeth', 'el monte', 'el paso', 'elyria',
                  'erie', 'escondido', 'essex', 'euclid', 'eugene', 'evans', 'evanston', 'evansville', 'ewa',
                  'fairbanks', 'fairfield', 'fairweather', 'fall river', 'fargo', 'farmington hills', 'fayetteville',
                  'fl', 'flathead', 'flint', 'florida', 'foraker', 'fort collins', 'fort lauderdale', 'fort smith',
                  'fort wayne', 'fort worth', 'framingham', 'frankfort', 'franklin township', 'fremont', 'fresno',
                  'fullerton', 'ga', 'gainesville', 'gannett peak', 'garden grove', 'garland', 'gary', 'georgetown',
                  'georgia', 'gila', 'glendale', 'grand forks', 'grand island', 'grand prairie', 'grand rapids',
                  'granite peak', 'grays', 'great falls', 'great salt lake', 'green', 'green bay', 'greensboro',
                  'greenville', 'greenwich', 'guadalupe peak', 'gulf of mexico', 'hamilton', 'hammond', 'hampton',
                  'harney peak', 'harrisburg', 'hartford', 'harvard', 'hattiesburg', 'hawaii', 'hayward', 'helena',
                  'hi', 'high point', 'hollywood', 'honolulu', 'houston', 'hubbard', 'hudson', 'humphreys peak',
                  'hunter', 'huntington', 'huntington beach', 'huntsville', 'huron', 'ia', 'id', 'idaho', 'idaho falls',
                  'il', 'iliamna', 'illinois', 'in', 'independence', 'indiana', 'indianapolis', 'inglewood', 'iowa',
                  'irondequoit', 'irvine', 'irving', 'irvington', 'jackson', 'jacksonville', 'jefferson city',
                  'jerimoth hill', 'jersey city', 'johnson township', 'joliet', 'juneau', 'kalamazoo', 'kansas',
                  'kansas city', 'kendall', 'kennedy', 'kenner', 'kenosha', 'kentucky', 'kettering', 'kings peak',
                  'kit carson', 'knoxville', 'koolaupoko', 'ks', 'ky', 'la', 'lafayette',
                  'lake champlain', 'lake charles', 'lake erie', 'lake michigan', 'lake of the woods', 'lake superior',
                  'lakewood', 'lansing', 'la plata', 'laramie', 'laredo', 'largo', 'las cruces', 'las vegas',
                  'lawrence', 'lawton', 'levittown', 'lewiston', 'lexington', 'lincoln', 'little missouri',
                   'little rock', 'livonia', 'long beach', 'long island sound', 'longs', 'longview',
                  'lorain', 'los angeles', 'louisiana', 'louisville', 'lowell', 'lower merion', 'lubbock', 'lynchburg',
                  'lynn', 'ma', 'macon', 'madison', 'magazine mountain', 'maine', 'manchester', 'maroon', 'maryland',
                  'massachusetts', 'massive', 'mauna kea', 'mcallen', 'mckinley', 'md', 'me', 'medford', 'memphis',
                  'meriden', 'meridian', 'mesa', 'mesquite', 'metairie', 'mi', 'miami', 'miami beach', 'michigan',
                  'middletown', 'midland', 'mille lacs', 'milwaukee', 'minneapolis', 'minnesota', 'minot',
                  'mississippi', 'missoula', 'missouri', 'mn', 'mo', 'mobile', 'modesto', 'monroe',
                  'montana', 'montgomery', 'montpelier', 'mountain view', 'mount curwood', 'mount davis',
                  'mount elbert', 'mount frissell', 'mount greylock', 'mount hood', 'mount katahdin', 'mount mansfield',
                  'mount marcy', 'mount mckinley', 'mount mitchell', 'mount rainier', 'mount rogers', 'mount sunflower',
                  'mount vernon', 'mount washington', 'mount whitney', 'ms', 'mt', 'muncie', 'naknek', 'nashua',
                  'nashville', 'nc', 'nd', 'ne', 'nebraska', 'neosho', 'nevada', 'newark', 'new bedford', 'new britain',
                  'new hampshire', 'new haven', 'new jersey', 'new mexico', 'new orleans', 'newport beach',
                  'newport news', 'new rochelle', 'newton', 'new york', 'nh', 'niagara falls', 'niobrara', 'nj', 'nm',
                  'norfolk', 'norman', 'north carolina', 'north charleston', 'north dakota', 'north little rock',
                  'north palisade', 'north platte', 'norwalk', 'nv', 'ny', 'oakland', 'oak lawn', 'oceanside',
                  'ocheyedan mound', 'odessa', 'ogden', 'oh', 'ohio',
                  # 'ohio river', 'delaware river', 'mississippi river', 'colorado river', 'arkansas river',
                  # 'kootenai river', 'little river', 'belle fourche river', 'ouachita river', 'potomac river',
                  # 'red river', 'snake river', 'verdigris river',
                  'ok', 'okeechobee', 'oklahoma',
                  'oklahoma city', 'olympia', 'omaha', 'ontario', 'or', 'orange', 'oregon', 'orlando', 'ouachita',
                   'overland park', 'owensboro', 'oxnard', 'pa', 'pacific ocean', 'parkersburg',
                  'parma', 'pasadena', 'paterson', 'pawtucket', 'pearl', 'pecos', 'penn hills', 'pennsylvania',
                  'pensacola', 'peoria', 'philadelphia', 'phoenix', 'pierre', 'pine bluff', 'pittsburgh', 'plano',
                  'pocatello', 'pomona', 'pontchartrain', 'pontiac', 'port arthur', 'portland', 'portsmouth', 'potomac',
                   'powder', 'princeton', 'providence', 'provo', 'pueblo', 'quandary', 'quincy',
                  'racine', 'rainier', 'rainy', 'raleigh', 'rapid city', 'reading', 'red', 'red bluff reservoir',
                  'redford', 'redondo beach', 'reno', 'republican', 'rhode island', 'ri', 'richardson',
                  'richmond', 'rio grande', 'riverside', 'roanoke', 'rochester', 'rock', 'rockford', 'rock springs',
                  'roswell', 'royal oak', 'rutland', 'sacramento', 'saginaw', 'salem', 'salinas', 'salt lake city',
                  'salton sea', 'san angelo', 'san antonio', 'san bernardino', 'san diego', 'sanford', 'san francisco',
                  'san jose', 'san juan', 'san leandro', 'san mateo', 'santa ana', 'santa barbara', 'santa clara',
                  'santa fe', 'santa monica', 'santa rosa', 'sassafras mountain', 'savannah', 'sc', 'schenectady',
                  'scottsdale', 'scotts valley', 'scranton', 'sd', 'seattle', 'shasta', 'shavano', 'shreveport', 'sill',
                  'silver spring', 'simi valley', 'sioux city', 'sioux falls', 'sitka', 'skokie', 'smoky hill', 'snake',
                   'somerville', 'south bend', 'south buttress', 'south carolina', 'south dakota',
                  'southeast corner', 'southfield', 'south gate', 'south platte', 'sparks', 'spokane', 'springfield',
                  'spruce knob', 'stamford', 'st. clair', 'st. clair shores', 'st. elias', 'sterling heights',
                  'st. francis', 'st. francis river', 'st. joseph', 'st. louis', 'stockton', 'st. paul',
                  'st. petersburg', 'sunnyvale', 'sunrise manor', 'superior', 'syracuse', 'tacoma', 'tahoe',
                  'tallahassee', 'tampa', 'taum sauk mountain', 'taylor', 'tempe', 'tenleytown', 'tennessee',
                  'terre haute', 'teshekpuk', 'texas', 'thousand oaks', 'timms hill', 'tn', 'toledo', 'tombigbee',
                  'topeka', 'torrance', 'torreys', 'trenton', 'troy', 'tucson', 'tulsa', 'tuscaloosa', 'tx', 'tyler',
                  'uncompahgre', 'upper darby', 'ut', 'utah', 'utica', 'va', 'vallejo', 'vancouver', 'ventura',
                   'vermont', 'virginia', 'virginia beach', 'vt', 'wa', 'wabash', 'waco', 'wahiawa',
                  'waltham', 'walton county', 'warren', 'warwick', 'washington', 'washita', 'waterbury',
                  'wateree catawba', 'waterford', 'waterloo', 'watertown', 'waukegan', 'west allis', 'west covina',
                  'west hartford', 'westland', 'westminster', 'west palm beach', 'west valley', 'west virginia',
                  'wheeler peak', 'wheeling', 'white', 'white butte', 'whitney', 'whittier', 'wi', 'wichita',
                  'wichita falls', 'williamson', 'wilmington', 'wilson', 'winnebago', 'winston-salem', 'wisconsin',
                  'woodall mountain', 'woodbridge', 'worcester', 'wrangell', 'wv', 'wy', 'wyoming', 'yale',
                  'yellowstone', 'yonkers', 'youngstown']


# from utils.executor import Executor
s = re.compile("([,() ])")

quotes = re.compile("(')")

NAMED_ENTITY_TRIE = dict()
for n in NAMED_ENTITIES:
    parts = n.split(" ")
    for i in range(len(parts)):
        path = tuple(parts[:i])
        NAMED_ENTITY_TRIE[path] = NAMED_ENTITY_TRIE.get(path, set()) | {tuple(parts[:i+1])}

GEO_PREDS = set(GEO_ARITIES.keys())


def split_tokens(x):
    return [x for x in s.split(x.strip()) if x and x.strip(" ")]


def to_lisp(toks):
    r = []
    for t in toks:
        if t == "(":
            r = r[:-1] + ["("] + [r[-1]]
        elif t == ",":
            r.append(" ")
        else:
            r.append(t)
    return r


def get_tree(s):
    s = split_tokens(s)
    return Tree.fromstring(" ".join(to_lisp(s)))

class QuoteHandling(Enum):
    NOOP = 0
    SEPARATE = 1
    DELETE = 2


def preorder_wo_brackets(t: Union[str, Tree], quote_handling: QuoteHandling) -> List[str]:
    if isinstance(t, str):
        if quote_handling == QuoteHandling.SEPARATE:
            return [x for x in quotes.split(t) if x]
        elif quote_handling == QuoteHandling.DELETE:
            return [t.replace("'", "")]
        else:
            return [t]
    children = list(t)
    r = [t.label()]
    for c in children:
        r.extend(preorder_wo_brackets(c, quote_handling))
    return r


def reconstruct_tree_without_brackets(s: List[str], arities: Dict[str, int]) -> Tree:
    """
    Reconstruct a tree from a linearized representation without brackets.
    :param s:
    :param arities:
    :param add_quotes:
    :param joiner:
    :return:
    """
    position = 0
    # print(s)

    def read_tree():
        nonlocal position
        # print(s)
        head = s[position]
        position += 1
        # print(head)
        # print(position)
        if head in arities:
            return Tree(head, children=[read_tree() for _ in range(arities[head])])
        else:
            return head  # assume arity 0
    try:
        t = read_tree()
    except IndexError:
        t = None
    # print(position, t)
    # comment this assertion because pred mr sometimes contain unseen arities.
    # assert position == length(s)
    # ~ print(position, length(s))
    return t

def restore_quotes(s: List[str]):
    r = []
    i = 0
    while i < len(s):
        match = get_longest_match(s[i:], NAMED_ENTITY_TRIE)  # O(n^2) but whatever
        if match is not None:
            r.append("'" + " ".join(s[i:i+match+1]) + "'")
            i += match+1
        else:
            r.append(s[i])
            i += 1
    return r

def get_longest_match(toks, trie):
    """
    If there is a match at the beginning of toks, it returns the last index where it matches.
    It doesn't backtrack if there is a continuation that turns out to be a dead end.
    Looks OK for our purpose.
    :param toks:
    :param trie:
    :return:
    """
    state = ()
    index = -1
    for i, tok in enumerate(toks):
        next_state = state + (tok,)
        if state not in trie:
            break
        if next_state in trie[state]:
            state = next_state
            index += 1
        else:
            break
    if index < 0 or state in trie:
        return None
    return index


def geo_reconstruct_tree(s: List[str], add_quotes: bool):
    if add_quotes:
        s = restore_quotes(s)
    return reconstruct_tree_without_brackets(s, GEO_ARITIES)

def tree2funql(t):
    if isinstance(t, str):
        return t
    return t.label() + "(" + ",".join(tree2funql(c) for c in t) + ")"

def postprocess(program):
    # tree = get_tree(program)
    # toks = preorder_wo_brackets(tree, QuoteHandling.DELETE)
    # print(toks)
    # Reconstruct tree
    program_tokens = program.split()
    t = geo_reconstruct_tree(program_tokens, True)
    if t is not None:
        funql_rep = tree2funql(t)
    else:
        funql_rep = t

    for sym in ["(", ")", ","]:
        funql_rep = funql_rep.replace(sym, " " + sym + " ")
    funql_rep = funql_rep.replace("  ", " ")
    funql_rep = funql_rep.replace('\'', '')

    return funql_rep

def postprocess2(program):
    program_tokens = program.split()
    t = geo_reconstruct_tree(program_tokens, True)
    if t is not None:
        funql_rep = tree2funql(t)
    else:
        funql_rep = t

    for sym in ["(", ")", ","]:
        funql_rep = funql_rep.replace(sym, " " + sym + " ")
    funql_rep = funql_rep.replace("  ", " ")
    return funql_rep

def remove_special_symbols(sent):
    special_symbols = ["(", ")", ","]
    tokens = sent.split()
    output = []
    for tok in tokens:
        if tok not in special_symbols:
            output.append(tok)
    return " ".join(output)

def remove_duplicates(sent):
    output = []
    tokens = sent.split()
    for i in range(len(tokens) - 1):
        if tokens[i] != tokens[i + 1] or tokens[i] == "exclude":
            output.append(tokens[i])
    output.append(tokens[-1])
    return " ".join(output)
