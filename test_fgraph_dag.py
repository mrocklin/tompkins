from fgraph_dag import *
import theano


def info(var):
    return var.name, var.dtype, var.broadcastable, var.type
def namify_dict(d):
    return {k.name: v for k,v in d.items()}

def test_simple_add():
    x = theano.tensor.matrix('x')
    y = theano.tensor.matrix('y')
    z = x + y
    fgraph = theano.FunctionGraph((x,y), (z,))
    _test_fgraph_dag_equivalence(fgraph)
    _test_roundtrip(fgraph)

def test_complex():
    x = theano.tensor.matrix('x')
    y = theano.tensor.matrix('y')
    z = theano.tensor.matrix('z')
    a = x + y * z
    b = theano.tensor.dot(a, z)
    c = a + a + b
    d = x[:2] + y + c

    fgraph = theano.FunctionGraph((x,y, z), (d, c, x))
    _test_fgraph_dag_equivalence(fgraph)
    _test_roundtrip(fgraph)

def _test_fgraph_dag_equivalence(fgraph):
    fgraph = fgraph_with_names(fgraph)
    dag, inputs, outputs = fgraph_to_dag(fgraph)
    assert set(map(info, fgraph.variables)) == set(map(info, dag.keys()))

    dag = namify_dict(dag)
    assert all(type(dag[var.name]['fn']) == type(var.owner.op
                                                 if var.owner else None)
               for var in fgraph.variables)
    assert all(map(info, dag[var.name]['args']) == map(info,
                                                       var.owner.inputs
                                                       if var.owner else ())
               for var in fgraph.variables)

def _test_roundtrip(fgraph):
    fgraph2 = dag_to_fgraph(*fgraph_to_dag(fgraph))
    assert (theano.printing.debugprint(fgraph,  file='str') ==
            theano.printing.debugprint(fgraph2, file='str'))
