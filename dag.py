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


def clone(x):
    return x

index = '_index'

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


def tuple_dag_to_graph(dag, inputs, outputs, ith_output):
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
        inputs = map(_build_var, args)
        return ith_output(fn, inputs, idx)


    graph_outputs = map(_build_var, outputs)
    graph_inputs  = map(input_set.__getitem__, map(str, inputs))

    return graph_inputs, graph_outputs
