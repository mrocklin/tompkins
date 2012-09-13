from dag import *

def info(var):
    return var.name, var.dtype, var.broadcastable, var.type
def namify_dict(d):
    return {k.name: v for k,v in d.items()}

tuple_dag = {('a',)    : {'fn': 1, 'args': ('b', 'c')},
             ('b', 'c'): {'fn': 2, 'args': ()}}
index_dag = {('a',)    : {'fn': 1, 'args': ('b', 'c')},
             ('b', 'c'): {'fn': 2, 'args': ()},
             'a'       : {'fn': index, 'args': (('a',), 0)},
             'b'       : {'fn': index, 'args': (('b', 'c'), 0)},
             'c'       : {'fn': index, 'args': (('b', 'c'), 1)}}
redin_dag = {'a'       : {'fn': 1, 'args': ('b', 'c')},
             ('b', 'c'): {'fn': 2, 'args': ()},
             'b'       : {'fn': index, 'args': (('b', 'c'), 0)},
             'c'       : {'fn': index, 'args': (('b', 'c'), 1)}}

def test_tuple_dag_to_index_dag():
    assert tuple_dag_to_index_dag(tuple_dag) == index_dag

def test_remove_singleton_indices():
    assert remove_singleton_indices(index_dag) == redin_dag

def test_insert_single_indices():
    assert insert_single_indices(redin_dag) == index_dag

def test_remove_index_entries():
    assert remove_index_entries(index_dag) == tuple_dag

def test_all():
    assert (remove_index_entries(
                insert_single_indices(
                    remove_singleton_indices(
                        tuple_dag_to_index_dag(tuple_dag))))
            == tuple_dag)

def test_remove_singleton_indices():
    indag = {'a':   {'fn': index, 'args':(('a',), 0)},
            ('a',): {'fn': 'stuff', 'args': (1,2,3)},
             'b':   {'fn': 'blah', 'args': ()}}

    assert remove_singleton_indices(indag) == {
        'a': {'fn': 'stuff', 'args': (1,2,3)},
        'b': {'fn': 'blah',  'args': ()}}

