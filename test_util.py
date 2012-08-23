from util import *

def test_iterable():
    assert iterable((1,2))
    assert iterable([3])
    assert not iterable(3)

def test_dictify():
    f = lambda a,b: a+b
    g = dictify(f)
    assert g[1,2] == 3

def test_reverse_dict():
    d = {'a': (1, 2), 'b': (2, 3), 'c':()}
    assert reverse_dict(d) ==  {1: ('a',), 2: ('a', 'b'), 3: ('b',)}

def test_merge():
    d = {1:2, 3:4}
    e = {4:5}
    assert merge(d, e) == {1:2, 3:4, 4:5}
