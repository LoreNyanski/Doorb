import re
import random

CHANCE_AMOGUS = 15
CHANCE_DAD = 15
CHANCE_FUCKING = 15
CHANCE_SALUTE = 2
CHANCE_HIVEMIND = 1 # it already basically never happens
CHANCE_67 = 1

hivemind_buffer = ['', '', '']

def rndm(chance) -> bool:
    """returns true with 1/chance odds"""
    if chance < 1: return False
    return random.randint(1,chance) == 1

def amogus_check(message: str) -> bool:
    return rndm(CHANCE_AMOGUS) and re.search(r'.*a.*m.*o.*g.*u.*s.*', message, re.IGNORECASE) and not re.search(r'.*amogus.*', message, re.IGNORECASE)

def dad_check(message: str) -> bool:
    return rndm(CHANCE_DAD) and re.search(r"^I('| a)?m ", message, re.IGNORECASE)

def fucking_check(message: str) -> bool:
    return rndm(CHANCE_FUCKING) and re.search(r"\S+ fucking? \S+", message, re.IGNORECASE)

def salute_check(message: str) -> bool:
    return rndm(CHANCE_SALUTE) and re.search(r"(general|major|lieutenant|captain|colonel) \S+", message, re.IGNORECASE)

def hivemind_check(message: str) -> bool:
    global hivemind_buffer
    hivemind_buffer.append(message)
    hivemind_buffer.pop(0)
    if all(item == hivemind_buffer[0] for item in hivemind_buffer):
        hivemind_buffer = ['', '', '']
        return rndm(CHANCE_HIVEMIND)
    else:
        return False
    
def s67_check(message: str) -> bool:
    return rndm(CHANCE_67) and re.search(r'.*(6|s+i+x+).*(7|s+e+v+e+n+).*', message, re.IGNORECASE)