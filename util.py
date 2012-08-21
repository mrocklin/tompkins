
def iterable(x):
    try:
        iter(x)
        return True
    except TypeError:
        return False
class fakedict(object):
    def __init__(self, fn):
        self.fn = fn
    def __getitem__(self, item):
        if iterable(item):
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
