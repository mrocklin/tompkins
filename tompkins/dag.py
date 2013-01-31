from tompkins.ilp import schedule as schedule_tompkins
from tompkins.ilp import jobs_when_where
from tompkins.util import reverse_dict, dictify, intersection, merge, unique
from collections import defaultdict


def precedes_to_dag(jobs, precedes):
    return {a: [b for b in jobs if precedes(a, b)] for a in jobs}

def transform_args(dag, agents, compcost, commcost, R, B, M):
    """ Transform arguments given to dag.schedule to those expected by tompkins

    inputs:
        dag - unipartite dag of the form {1: (2, 3)} if job 1 precedes 2 and 3
        agents - a list of machines on which we can run each job
        compcost - a function (job, agent) -> runtime
        commcost - a function (job, agent, agent) -> communication time
        R - a function (job) -> start time (usually lambda j: 0)
        B - a function (job, agent) -> 1/0 - 1 if job can be run on agent
        M - a maximum makespan
    outputs:
        see tompkins.schedule's inputs
    """
    P = unidag_to_P(dag)
    D = dictify(compcost)
    C = dictify(commcost)
    R = dictify(R)
    B = dictify(B)
    jobs = dag.keys()
    return jobs, agents, D, C, R, B, P, M

def schedule(dag, agents, compcost, commcost, R, B, M):
    """ Statically Schedule a DAG of jobs on a set of machines

    This function wraps tompkins.ilp.schedule

    inputs:
        dag - unipartite dag of the form {1: (2, 3)} if job 1 precedes 2 and 3
        agents - a list of machines on which we can run each job
        compcost - a function (job, agent) -> runtime
        commcost - a function (job, agent, agent) -> communication time
        R - a function (job) -> start time (usually lambda job: 0)
        B - a function (job, agent) -> 1/0 - 1 if job can be run on agent
        M - a maximum makespan

    outputs:
        dags     - a dict mapping machine to local dag
        sched    - a list of (job, start_time, machine)
        makespan - the total runtime of the computation
    """
    args = schedule_tompkins(
                    *transform_args(dag, agents, compcost, commcost, R, B, M))
    prob, X, S, Cmax = args
    sched = jobs_when_where(*args)
    jobson = compute_jobson(sched)
    dags = manydags(dag, jobson)
    return dags, sched, Cmax.value()

def unidag_to_P(dag):
    """ Converts a dag dict into one suitable for the tompkins algorithm

    input   like {1: (2, 3)}
    output  like {(1,2): 1, (1, 3): 1}
    """
    d = defaultdict(lambda : 0)
    for k, v in {(a,b): 1 for a in dag for b in dag[a]}.items():
        d[k] = v
    return d

def compute_jobson(sched):
    """
    Given the output of jobs_when_where produce a dict mapping machine to jobs
    {machine: [jobs]}
    """
    result = {}
    for job, _, agent in sched:
        result[agent] = result.get(agent, ()) + (job,)
    return result

def send(from_machine, to_machine, from_job, to_job):
    return ("send", from_machine, to_machine, from_job, to_job)
def recv(from_machine, to_machine, from_job, to_job):
    return ("recv", from_machine, to_machine, from_job, to_job)

def issend(x):
    return isinstance(x, tuple) and x[0] == "send"
def isrecv(x):
    return isinstance(x, tuple) and x[0] == "recv"

def replace_send_recv(dag, fn_send, fn_recv):
    """ Replaces all instances of tompkins send with a user defined send

    inputs functions like:
        fn_send - (from_machine, to_machine, from_job, to_job) -> a send
        fn_recv - (from_machine, to_machine, from_job, to_job) -> a recv
    """
    def convert(x):
        if issend(x): return fn_send(*x[1:])
        if isrecv(x): return fn_recv(*x[1:])
        return x
    return {convert(key): tuple(map(convert, values))
                            for key, values in dag.items()}

def manydags(dag, jobson, send=send, recv=recv):
    """ Given a dag and a schedule return many dags with sends/receives

    inputs:
    dag - Dictionary containing precedence constraints - specifies DAG:
        dag[job1] == (job2, job3) 1 if job1 immediately precedes job2 and job3
    jobson - Dictionary mapping machine to list of jobs

    returns:
    dags - a dict of dags mapping machine to dag {machine: dag}
        Each dag is represented like dag (see above)
        New send and receive jobs have been added
    """

    onmachine = {value:key  for key, values in jobson.items()
                            for value in values}
    revdag = reverse_dict(dag)
    assert unique(sum(jobson.values(), ()))

    return {machine:
             merge(
               # Standard local dag
               {fromjob: tuple(
                 tojob if tojob in jobson[machine]
                       else send(machine, onmachine[tojob], fromjob, tojob)
                       for tojob in dag[fromjob])
                 for fromjob in jobson[machine]}
               ,
               # Add in all of the receives
               {recv(onmachine[fromjob], machine, fromjob, tojob):
                intersection(dag[fromjob], jobson[machine])
                    for tojob in jobson[machine]
                    for fromjob in revdag.get(tojob, ()) # might not have parent
                    if fromjob not in jobson[machine]}
               ,
               # Add in all of the sends
               {send(machine, onmachine[tojob], fromjob, tojob): ()
                   for fromjob in jobson[machine]
                   for tojob in dag.get(fromjob, ())
                   if onmachine[tojob] != machine
                   }
             )
             for machine in jobson.keys()}
