from bidag import *

# letters are variables
# numbers are jobs

def test_reverse_dict():
    d = {'a': (1, 2), 'b': (2, 3)}
    assert reverse_dict(d) ==  {1: ('a',), 2: ('a', 'b'), 3: ('b',)}

def test_bidag_to_unidag_simple():
    usedby = {'a': (1,), 'b': (2,), 'c':(3, )}
    outputsof = {1: ('b',) , 2: ('c', ), 3: ('d',)}
    # a -> 1 -> b -> 2 -> c -> 3 -> d

    unidag = bidag_to_unidag(usedby, outputsof)
    assert unidag == {1: (2, ), 2: (3,), 3: ()}

def test_bidag_to_unidag_less_simple():
    usedby = {'a': (1,), 'b': (2,), 'c':(3, )}
    outputsof = {1: ('b', 'c') , 2: ('d', ), 3: ('e',)}
    # a -> 1 -> b -> 2 -> d
    #        -> c -> 3 -> e

    unidag = bidag_to_unidag(usedby, outputsof)
    assert unidag == {1: (2, 3), 2: (), 3: ()}

def test_unidag_to_subbidag():
    usedby = {'a': (1,), 'b': (2,), 'c':(3, )}
    outputsof = {1: ('b',) , 2: ('c', ), 3: ('d',)}
    # a -> 1 -> b -> 2 -> c -> 3 -> d

    subdag = {1: (2,), 2:(send('A', 'B', 2, 3),), send('A', 'B', 2, 3): ()}
    # 1 -> 2 -> send(A, B, 2, 3)
    sm_usedby, sm_outputsof = unidag_to_subbidag((usedby, outputsof), subdag)
    assert sm_usedby    == {'a': (1,), 'b': (2,), 'c':(send('A', 'B'),)}
    assert sm_outputsof == {1: ('b',), 2: ('c',), send('A', 'B'): ()}

    subdag2 = {recv('A', 'B', 2, 3): (3,), 3: ()}
    sm_usedby, sm_outputsof = unidag_to_subbidag((usedby, outputsof), subdag2)

    print sm_usedby
    print sm_outputsof
    assert sm_usedby    == {'c': (3,)}
    assert sm_outputsof == {recv('A', 'B'): ('c',), 3: ('d',)}

def test_cycle():
    usedby = {'a': (1,), 'b': (2,), 'c':(3, )}
    outputsof = {1: ('b', 'c') , 2: ('d', ), 3: ('e',)}

    unidag = bidag_to_unidag(usedby, outputsof)
    usedby2, outputsof2 = unidag_to_subbidag((usedby, outputsof), unidag)

    assert usedby == usedby2
    assert outputsof == outputsof2
