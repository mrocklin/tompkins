import theano
from util import merge

## {{{ http://code.activestate.com/recipes/578231/ (r1)
def memodict(f):
    """ Memoization decorator for a function taking a single argument """
    class memodict(dict):
        def __missing__(self, key):
            ret = self[key] = f(key)
            return ret
    return memodict().__getitem__
## end of http://code.activestate.com/recipes/578231/ }}}

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

    fgraph = theano.FunctionGraph(ins, outs)

    for i, var in enumerate(filter(bad_var, fgraph.variables)):
        var.name = (var.name or "") + "_%d"%i

    if not unique(map(str, fgraph.variables)):
        raise ValueError("Not all variables have unique names."
                         "Maybe you've named some of the variables identically")

    return fgraph

def clone(x):
    return x.clone()

def dag_unpack_singleton_tuples(dag):
    """

    merges two operations that look like this
    {(out,) : {'fn': op,  'args': args}
     out    : {'fn': index, 'args': (out, 0)}}
    into just one that looks like this
    {out    : {'fn': op,  'args': args}}
    i.e. it unpacks singleton tuples
    """

    # dict of shortcuts
    quick_outs = {out: dag[(out,)] for out in dag if (out,) in dag}

    def badkey(out):
        return (out in quick_outs
             or (    isinstance(out, tuple)
                 and len(out) == 1
                 and out[0] in quick_outs))
    clean_dag =  {out : dag[out] for out in dag
                                 if not badkey(out)}

    return merge(clean_dag, quick_outs)

index = 'index'
def fgraph_to_dag(fgraph):
    fgraph = fgraph_with_names(fgraph)
    newvars = {var: clone(var) for var in fgraph.variables}

    # Produces dag with inputs and outputs as tuples
    dag = {tuple(map(newvars.__getitem__, node.outputs)):
            {'fn'  : node.op,
             'args': tuple(map(newvars.__getitem__, node.inputs))}
             for node in fgraph.nodes}
    # lots of things like {'a' : {'fn': 'index', (('a', 'b'), 0)}}
    # indexing into the tuples
    gets = {out:
            {'fn' : index,
             'args' : (outs, i)}
            for outs in dag if isinstance(outs, tuple)
            for i, out in enumerate(outs)}

    full_dag = merge(dag, gets)

    # Lets clear away the trivial tuple indexing (indexing by 0)
    clean_dag = dag_unpack_singleton_tuples(full_dag)

    # don't forget that we need to include inputs
    input_dag = {newvars[inp] : {'fn': None, 'args': ()}
            for inp in fgraph.inputs}

    final_dag = merge(clean_dag, input_dag)

    inputs  = tuple(map(newvars.__getitem__, fgraph.inputs))
    outputs = tuple(map(newvars.__getitem__, fgraph.outputs))

    return final_dag, inputs, outputs


def dag_to_fgraph(dag, inputs, outputs):
    input_set = {}

    @memodict
    def _build_var(var):
        if not dag[var]['fn']:
            newvar = clone(var)
            input_set[var.name] = newvar
            return newvar
        return dag[var]['fn'].make_node(
                *map(_build_var, dag[var]['args'])).outputs[0]

    fgraph_outputs = map(_build_var, outputs)
    fgraph_inputs  = map(input_set.__getitem__, map(str, inputs))

    return theano.FunctionGraph(fgraph_inputs, fgraph_outputs)
