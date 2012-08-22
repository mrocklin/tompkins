# The Tompkins algorithm works on dags where each node represents a job.
# Computations are often represented as bipartite dags with two node types
# * Jobs
# * Variables
#
# This file contains utilities to manage this transformation back and forth

# We expect incoming bipartite dags as two dependency dicts

def reverse_dict(d):
    """ Reverses direction of dependence dict

    >>> d = {'a': (1, 2), 'b': (2, 3)}
    >>> reverse_dict(d)
    {1: ('a',), 2: ('a', 'b'), 3: ('b',)}
    """
    result = {}
    for key in d:
        for val in d[key]:
            result[val] = result.get(val, tuple()) + (key, )
    return result

def bidag_to_unidag(usedby, outputsof):
    """ Converts a bivariate DAG of jobs+variables to a dag of jobs

    inputs:
        usedby      - dict mapping variables to jobs that use them
        outputsof   - dict mapping jobs to variables that they produce

    >>> # 'a' -> 1 -> 'b' -> 2 -> c
    >>> bidag_to_unidag({'a': (1,), 'b': (2,)}, {1: ('b',) , 2: ('c', )})
    {1: (2, ), 2: tuple()}
    """
    result = {}
    return {job: tuple(sum([usedby[output] for output in outputsof[job]
                                           if output in usedby], tuple()))
               for job in outputsof.keys()}

def communication_conversion(usedby, outputsof, commcost):
    """ Convert a communication cost function from variables to jobs

    inputs:
        usedby      - dict mapping variables to jobs that use them
        outputsof   - dict mapping jobs to variables that they produce
        commcost    - function mapping      (var, machine, machine) -> time
                      to               (job, job, machine, machine) -> time

    """
    if not commcost.func_code.co_argcount != 3:
        raise ValueError("Expected function (var, machine, machine) -> time")

    inputsof = reverse_dict(usedby)

    def job_to_job_commcost(j1, j2, m1, m2):
        variables = set(outputsof[j1]).intersection(set(inputsof[j2]))
        return sum(commcost(var, m1, m2) for var in variables)
    return job_to_job_commcost
