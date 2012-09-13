from theano_dag import *
import theano


def info(var):
    return var.name, var.dtype, var.broadcastable, var.type
def namify_dict(d):
    return {k.name: v for k,v in d.items()}

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
