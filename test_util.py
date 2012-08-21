from util import *

def test_iterable():
    assert iterable((1,2))
    assert iterable([3])
    assert not iterable(3)

def test_dictify():
    f = lambda a,b: a+b
    g = dictify(f)
    assert g[1,2] == 3
