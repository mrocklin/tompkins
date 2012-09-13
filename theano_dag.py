import theano
from theano import FunctionGraph
import dag
def clone(x):
    return x.clone()
dag.clone = clone
from dag import *

def unique(x):
    return len(set(x)) == len(x)

def hist(coll):
    counts = {}
    for elem in coll:
        counts[elem] = counts.get(elem, 0) + 1
    return counts
def fgraph_with_names(fgraph):
    """ Gives unique names to all variable within a FunctionGraph """
    ins, outs  = theano.gof.graph.clone(fgraph.inputs, fgraph.outputs)

    names = map(lambda var: var.name, fgraph.variables)
    h = hist(names)
    bad_var = lambda var: h[var.name] > 1

    fgraph = FunctionGraph(ins, outs)

    for i, var in enumerate(filter(bad_var, fgraph.variables)):
        var.name = (var.name or "") + "_%d"%i

    if not unique(map(str, fgraph.variables)):
        raise ValueError("Not all variables have unique names."
                         "Maybe you've named some of the variables identically")

    return fgraph


def fgraph_to_tuple_dag(fgraph):
    fgraph = fgraph_with_names(fgraph)
    newvars = {var: clone(var) for var in fgraph.variables}

    # Produces dag with inputs and outputs as tuples
    dag = {tuple(map(newvars.__getitem__, node.outputs)):
            {'fn'  : node.op,
             'args': tuple(map(newvars.__getitem__, node.inputs))}
             for node in fgraph.nodes}

    inputs  = tuple(map(newvars.__getitem__, fgraph.inputs))
    outputs = tuple(map(newvars.__getitem__, fgraph.outputs))

    return dag, inputs, outputs

def tuple_dag_to_fgraph(dag, inputs, outputs):
    def ith_output(fn, inputs, idx):
        return fn.make_node(*inputs).outputs[idx]

    return FunctionGraph(*tuple_dag_to_graph(dag, inputs, outputs, ith_output))

# Composite functions
def fgraph_to_dag(fgraph):
    tdag, inputs, outputs = fgraph_to_tuple_dag(fgraph)
    dag = remove_singleton_indices(tuple_dag_to_index_dag(tdag))
    return dag, inputs, outputs

def dag_to_fgraph(dag, inputs, outputs):
    tdag = remove_index_entries(insert_single_indices(dag))
    return tuple_dag_to_fgraph(tdag, inputs, outputs)
