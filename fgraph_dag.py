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


index = '_index'

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

def tuple_dag_to_index_dag(tdag):

    gets = {out:
            {'fn' : index,
             'args' : (outs, i)}
            for outs in tdag if isinstance(outs, tuple)
            for i, out in enumerate(outs)}

    return merge(tdag, gets)

def remove_singleton_indices(dag):
    """

    merges two operations that look like this
    {(out,) : {'fn': op,  'args': args}
     out    : {'fn': index, 'args': ((out,) 0)}}
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

def insert_single_indices(dag):
    """ Add in all index operations from tuples, even singletons

    Reverses remove_singleton_indices
    """

    return merge(*[
            {out: dag[out]}
            if isinstance(out, tuple) or dag[out]['fn'] == index else
            {(out,) : dag[out],
              out   : {'fn': index, 'args':((out,), 0)}}
            for out in dag])

def remove_index_entries(dag):
    """ Remove naked variables - only tuples as outputs """
    return {k:v for k,v in dag.items() if isinstance(k, tuple)}

def tuple_dag_to_fgraph(dag, inputs, outputs):
    input_set = {}

    def is_input(var):
        return var in inputs
    subvar = {out:outs for outs in dag for out in outs}

    @memodict
    def _build_var(var):
        if is_input(var):
            newvar = clone(var)
            input_set[str(var)] = newvar
            return newvar
        # In which tuple do I live?
        outs = subvar[var]
        idx  = outs.index(var)
        fn   = dag[outs]['fn']
        args = dag[outs]['args']
        # Compute result of the associated function
        # Get the variables for the inputs recursively
        return fn.make_node(*map(_build_var, args)).outputs[idx]

    fgraph_outputs = map(_build_var, outputs)
    fgraph_inputs  = map(input_set.__getitem__, map(str, inputs))

    return theano.FunctionGraph(fgraph_inputs, fgraph_outputs)

# Composite functions
def fgraph_to_dag(fgraph):
    tdag, inputs, outputs = fgraph_to_tuple_dag(fgraph)
    dag = remove_singleton_indices(tuple_dag_to_index_dag(tdag))
    return dag, inputs, outputs

def dag_to_fgraph(dag, inputs, outputs):
    tdag = remove_index_entries(insert_single_indices(dag))
    return tuple_dag_to_fgraph(tdag, inputs, outputs)
