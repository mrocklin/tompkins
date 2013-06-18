
def iterable(x):
    try:
        iter(x)
        return True
    except TypeError:
        return False

class fakedict(object):
    def __init__(self, fn):
        self.fn = fn
        try:
            self.multi_input = fn.func_code.co_argcount > 1
        except AttributeError:
            self.multi_input = True
    def __getitem__(self, item):
        if self.multi_input:
            return self.fn(*item)
        else:
            return self.fn(item)

def dictify(f):
    """
    Turns a function into something that looks like a dict

    >>> f = lambda a,b : a+b
    >>> g = dictify(f)
    >>> g[1,2]
    3
    """
    return fakedict(f)

def reverse_dict(d):
    """ Reverses direction of dependence dict

    >>> d = {'a': (1, 2), 'b': (2, 3), 'c':()}
    >>> reverse_dict(d)
    {1: ('a',), 2: ('a', 'b'), 3: ('b',)}
    """
    result = {}
    for key in d:
        for val in d[key]:
            result[val] = result.get(val, tuple()) + (key, )
    return result

def merge(*args):
    return dict(sum([arg.items() for arg in args], []))

def intersection(t1, t2):
    return tuple(set(t1).intersection(set(t2)))

def unique(coll):
    return len(coll) == len(set(coll))

def groupby(f, coll):
    """ Group a collection by a key function

    >>> from tompkins.util import groupby
    >>> names = ['Alice', 'Bob', 'Charlie', 'Dan', 'Edith', 'Frank']
    >>> groupby(len, names)
    {3: ['Bob', 'Dan'], 5: ['Alice', 'Edith', 'Frank'], 7: ['Charlie']}
    """
    d = dict()
    for item in coll:
        key = f(item)
        if key not in d:
            d[key] = []
        d[key].append(item)
    return d
