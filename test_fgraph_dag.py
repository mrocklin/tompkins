from fgraph_dag import *
import theano


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

def simple_example():
    x = theano.tensor.matrix('x')
    y = theano.tensor.matrix('y')
    z = x + y
    return (x, y), (z,)

def complex_example():
    x = theano.tensor.matrix('x')
    y = theano.tensor.matrix('y')
    z = theano.tensor.matrix('z')
    a = x + y * z
    b = theano.tensor.dot(a, z)
    c = a + a + b
    d = x[:2] + y + c

    return (x, y, z), (d, c, x)

def _test_fgraph_dag_equivalence(fgraph):
    fgraph = fgraph_with_names(fgraph)
    dag, inputs, outputs = fgraph_to_dag(fgraph)
    assert set(map(info, fgraph.variables)) == set(map(info, tuple(dag.keys())+inputs))

    dag = namify_dict(dag)
    assert all(type(dag[var.name]['fn']) == type(var.owner.op
                                                 if var.owner else None)
               for var in fgraph.variables
               if var.name not in map(str, inputs))
    assert all(map(info, dag[var.name]['args']) == map(info,
                                                       var.owner.inputs
                                                       if var.owner else ())
               for var in fgraph.variables
               if var.name not in map(str, inputs))

def _test_roundtrip(fgraph):
    fgraph2 = dag_to_fgraph(*fgraph_to_dag(fgraph))
    assert (theano.printing.debugprint(fgraph,  file='str') ==
            theano.printing.debugprint(fgraph2, file='str'))

def _test_example(example):
    inputs, outputs = example()
    fgraph = theano.FunctionGraph(inputs, outputs)
    _test_fgraph_dag_equivalence(fgraph)
    _test_roundtrip(fgraph)

def test_simple():
    _test_example(simple_example)
def test_complex():
    _test_example(complex_example)
