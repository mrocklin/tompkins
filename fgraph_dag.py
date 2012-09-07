import theano

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

def fgraph_to_dag(fgraph):
    fgraph = fgraph_with_names(fgraph)

    # Make unconnected copies of variables
    newvars = {var: clone(var) for var in fgraph.variables}

    dag = {newvars[var]:
                   {'fn'  : var.owner.op,
                    'args': tuple(map(newvars.__getitem__, var.owner.inputs))}
                    if var.owner else
                   {'fn': None, 'args': ()}
            for var in fgraph.variables}

    inputs  = tuple(map(newvars.__getitem__, fgraph.inputs))
    outputs = tuple(map(newvars.__getitem__, fgraph.outputs))

    return dag, inputs, outputs

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
