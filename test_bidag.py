from bidag import *

# letters are variables
# numbers are jobs

def test_reverse_dict():
    d = {'a': (1, 2), 'b': (2, 3)}
    assert reverse_dict(d) ==  {1: ('a',), 2: ('a', 'b'), 3: ('b',)}

def test_bidag_to_unidag():
    usedby = {'a': (1,), 'b': (2,)}
    outputsof = {1: ('b',) , 2: ('c', )}
    inputs = ('a', )
    outputs = ('c', )
    # 'a' -> 1 -> 'b' -> 2 -> c

    unidag = bidag_to_unidag(usedby, outputsof)
    assert unidag == {1: (2, ), 2: tuple()}

