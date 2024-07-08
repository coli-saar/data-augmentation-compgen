
# from nltk import PCFG
import numpy as np
import random
from pcfg import PCFG
from scripts.utils.io import read_file, write_file
from tqdm import tqdm
import json



grammar_str = """
S -> Command [0.5] | Command Command [0.5]
Command -> walk_command [0.2] | look_command [0.2] | jump_command [0.2] | run_command [0.2] | turn_command [0.2]
walk_command -> walk_actions [0.33] | walk_actions_twice [0.33] | walk_actions_thrice [0.34]
walk_actions -> walk [0.143] | lwalk [0.143] | rwalk [0.143] | olwalk [0.143] | orwalk [0.143] | alwalk [0.143] | arwalk [0.142]
walk_actions_twice -> walk walk [0.143] | lwalk lwalk [0.143] | rwalk rwalk [0.143] | olwalk olwalk [0.143] | orwalk orwalk [0.143] | alwalk alwalk [0.143] | arwalk arwalk [0.142]
walk_actions_thrice -> walk walk walk [0.143] | lwalk lwalk lwalk [0.143] | rwalk rwalk rwalk [0.143] | olwalk olwalk olwalk [0.143] | orwalk orwalk orwalk [0.143] | alwalk alwalk alwalk [0.143] | arwalk arwalk arwalk [0.142]      
walk -> "I_WALK" [1.0]
turn_left -> "I_TURN_LEFT" [1.0]
turn_right -> "I_TURN_RIGHT" [1.0]
lwalk -> turn_left walk [1.0]
rwalk -> turn_right walk [1.0]
olwalk -> turn_left turn_left walk [1.0]
orwalk -> turn_right turn_right walk [1.0]
alwalk -> turn_left walk turn_left walk turn_left walk turn_left walk [1.0]
arwalk -> turn_right walk turn_right walk turn_right walk turn_right walk [1.0]
look_command -> look_actions [0.33] | look_actions_twice [0.33] | look_actions_thrice [0.34]
look_actions -> look [0.143] | llook [0.143] | rlook [0.143] | ollook [0.143] | orlook [0.143] | allook [0.143] | arlook [0.142]
look_actions_twice -> look look [0.143] | llook llook [0.143] | rlook rlook [0.143] | ollook ollook [0.143] | orlook orlook [0.143] | allook allook [0.143] | arlook arlook [0.142]
look_actions_thrice -> look look look [0.143] | llook llook llook [0.143] | rlook rlook rlook [0.143] | ollook ollook ollook [0.143] | orlook orlook orlook [0.143] | allook allook allook [0.143] | arlook arlook arlook [0.142]
look -> "I_LOOK" [1.0]
llook -> turn_left look [1.0]
rlook -> turn_right look [1.0]
ollook -> turn_left turn_left look [1.0]
orlook -> turn_right turn_right look [1.0]
allook -> turn_left look turn_left look turn_left look turn_left look [1.0]
arlook -> turn_right look turn_right look turn_right look turn_right look [1.0]
jump_command -> jump_actions [0.33] | jump_actions_twice [0.33] | jump_actions_thrice [0.34]
jump_actions -> jump [0.143] | ljump [0.143] | rjump [0.143] | oljump [0.143] | orjump [0.143] | aljump [0.143] | arjump [0.142]
jump_actions_twice -> jump jump [0.143] | ljump ljump [0.143] | rjump rjump [0.143] | oljump oljump [0.143] | orjump orjump [0.143] | aljump aljump [0.143] | arjump arjump [0.142]
jump_actions_thrice -> jump jump jump [0.143] | ljump ljump ljump [0.143] | rjump rjump rjump [0.143] | oljump oljump oljump [0.143] | orjump orjump orjump [0.143] | aljump aljump aljump [0.143] | arjump arjump arjump [0.142]
jump -> "I_JUMP" [1.0]
ljump -> turn_left jump [1.0]
rjump -> turn_right jump [1.0]
oljump -> turn_left turn_left jump [1.0]
orjump -> turn_right turn_right jump [1.0]
aljump -> turn_left jump turn_left jump turn_left jump turn_left jump [1.0]
arjump -> turn_right jump turn_right jump turn_right jump turn_right jump [1.0]
run_command -> run_actions [0.33] | run_actions_twice [0.33] | run_actions_thrice [0.34]
run_actions -> run [0.143] | lrun [0.143] | rrun [0.143] | olrun [0.143] | orrun [0.143] | alrun [0.143] | arrun [0.142]
run_actions_twice -> run run [0.143] | lrun lrun [0.143] | rrun rrun [0.143] | olrun olrun [0.143] | orrun orrun [0.143] | alrun alrun [0.143] | arrun arrun [0.142]
run_actions_thrice -> run run run [0.143] | lrun lrun lrun [0.143] | rrun rrun rrun [0.143] | olrun olrun olrun [0.143] | orrun orrun orrun [0.143] | alrun alrun alrun [0.143] | arrun arrun arrun [0.142]     
run -> "I_RUN" [1.0]
lrun -> turn_left run [1.0]
rrun -> turn_right run [1.0]
olrun -> turn_left turn_left run [1.0]
orrun -> turn_right turn_right run [1.0]
alrun -> turn_left run turn_left run turn_left run turn_left run [1.0]
arrun -> turn_right run turn_right run turn_right run turn_right run [1.0]
turn_command -> turn_actions [0.33] | turn_actions_twice [0.33] | turn_actions_thrice [0.34]
turn_actions -> lturn [0.167] | rturn [0.167] | olturn [0.167] | orturn [0.167] | alturn [0.167] | arturn [0.165]
lturn -> turn_left [1.0]
rturn -> turn_right [1.0]
olturn -> turn_left turn_left [1.0]
orturn -> turn_right turn_right [1.0]
alturn -> turn_left turn_left turn_left turn_left [1.0]
arturn -> turn_right turn_right turn_right turn_right [1.0]
turn_actions_twice -> lturn lturn [0.167] | rturn rturn [0.167] | olturn olturn [0.167] | orturn orturn [0.167] | alturn alturn [0.167] | arturn arturn [0.165]
turn_actions_thrice -> lturn lturn lturn [0.167] | rturn rturn rturn [0.167] | olturn olturn olturn [0.167] | orturn orturn orturn [0.167] | alturn alturn alturn [0.167] | arturn arturn arturn [0.165]
"""

if __name__ == "__main__":
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