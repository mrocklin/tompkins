# The Tompkins algorithm works on dags where each node represents a job.
# Computations are often represented as bipartite dags with two node types
# * Jobs
# * Variables
#
# This file contains utilities to manage this transformation back and forth

# We expect incoming bipartite dags as two dependency dicts

from util import reverse_dict, intersection

def send(*args):
    return ("send",) + args
def issend(x):
    return isinstance(x, tuple) and x[0] == 'send'
def recv(*args):
    return ("recv",) + args
def isrecv(x):
    return isinstance(x, tuple) and x[0] == 'recv'

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


def unidag_to_subbidag((usedby, outputsof), unidag):
    """ Converts a full bivariate DAG and a small unidag part to a small bidag

    inputs:
        usedby      - dict mapping variables to jobs that use them - full graph
        outputsof   - dict mapping jobs to variables they produce  - full graph
        unidag      - a subset of the full unipartite dag

    outputs:
        small_usedby    - dict for the bivariate subdag
        small_outputsof - dict for the bivariate subdag

    >>> # 'a' -> 1 -> 'b' -> 2 -> c
    >>> usedby      = {'a': (1,), 'b': (2,), 'c': ()}
    >>> outputsof   = {1: ('b',) , 2: ('c', )}
    >>> subdag      = {1: (send('A', 'B', 1, 2), ),
                       send('A', 'B', 1, 2): ()}
    >>> unidag_to_subbidag((usedby, outputsof), subdag)
    ({'a': (1,), 'b': (send('A', 'B'),)},
     {1: ('b',), send('A', 'B'): ()})
    """
    inputsof = reverse_dict(usedby)
    jobs = unidag.keys()
    sends = filter(issend, jobs)
    recvs = filter(isrecv, jobs)
    # The subset of usedby that is relevant for the sub unidag
    small_usedby = {var: intersection(usedby[var], jobs)
                    for job in jobs
                    for var in
                        inputsof.get(job, ()) + outputsof.get(job, ())}

    # The subset of outputsof that is relevant for the sub unidag
    small_outputsof = {job: outputsof[job]
                       for job in intersection(outputsof, jobs)}

    # For each send hook up all of the new usedby
    # Add empty entries in outputsof for sends
    for (_, from_machine, to_machine, from_job, to_job) in sends:
        for var in intersection(outputsof[from_job], inputsof[to_job]):
            small_usedby[var] = small_usedby.get(var, ()) + (send(from_machine, to_machine),)
        small_outputsof[send(from_machine, to_machine)] = ()

    # For each receive hookup all of the new outputsof
    for (_, from_machine, to_machine, from_job, to_job) in recvs:
        small_outputsof[recv(from_machine, to_machine)] = (
                intersection(outputsof[from_job], inputsof[to_job]))

    return small_usedby, small_outputsof

def communication_conversion(usedby, outputsof, commcost):
    """ Convert a communication cost function from variables to jobs

    inputs:
        usedby      - dict mapping variables to jobs that use them
        outputsof   - dict mapping jobs to variables that they produce
        commcost    - function mapping      (var, machine, machine) -> time
                      to               (job, job, machine, machine) -> time

    """
    if commcost.func_code.co_argcount != 3:
        raise ValueError("Expected function (var, machine, machine) -> time")

    def job_commcost(j, m1, m2):
        # variables = set(outputsof[j1]).intersection(set(inputsof[j2]))
        variables = outputsof[j]
        return sum(commcost(var, m1, m2) for var in variables)
    return job_commcost
