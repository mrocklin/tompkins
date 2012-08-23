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
    """ Converts a bivariate DAG of jobs+variables to a dag of jobs

    inputs:
        usedby      - dict mapping variables to jobs that use them
        outputsof   - dict mapping jobs to variables that they produce

    >>> # 'a' -> 1 -> 'b' -> 2 -> c
    >>> unidag_to_bidag({1: (2,)}, {'a': (1, ), 'b':(2, )},)
    {1: (2, ), 2: tuple()}
    """
    inputsof = reverse_dict(usedby)
    jobs = unidag.keys()
    sends = filter(issend, jobs)
    recvs = filter(isrecv, jobs)
    small_usedby = {var: intersection(usedby[var], jobs)
        for job in jobs
        for var in inputsof.get(job, ())}
    small_outputsof = {job: outputsof[job] for job in intersection(outputsof, jobs)}
    print "inside unidag_to_subdiag"
    print small_usedby
    print small_outputsof

    for (_, from_machine, to_machine, from_job, to_job) in sends:
        for var in intersection(outputsof[from_job], inputsof[to_job]):
            small_usedby[var] = small_usedby.get(var, ()) + (send(from_machine, to_machine),)
        small_outputsof[send(from_machine, to_machine)] = ()

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
    if not commcost.func_code.co_argcount != 3:
        raise ValueError("Expected function (var, machine, machine) -> time")

    inputsof = reverse_dict(usedby)

    def job_to_job_commcost(j1, j2, m1, m2):
        variables = set(outputsof[j1]).intersection(set(inputsof[j2]))
        return sum(commcost(var, m1, m2) for var in variables)
    return job_to_job_commcost
