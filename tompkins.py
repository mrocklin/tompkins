"""
This module describes a highly flexible scheduling problem by encoding it as a
Mixed Integer Linear Program (MILP) using the pulp framework[1].
This framework can then call any of several external codes[2] to solve

This formulation of the MILP was specified in chapters 4.1, 4.2 in the
following masters thesis. Section and equation numbers are cited.

"Optimization Techniques for Task Allocation and Scheduling in Distributed Multi-Agent Operations"
by
Mark F. Tompkins, June 2003, Masters thesis for MIT Dept EECS[3]

[1] http://code.google.com/p/pulp-or/ -- "sudo easy_install pulp"
[2] On ubuntu we used "sudo apt-get install glpk"
[3] http://dspace.mit.edu/bitstream/handle/1721.1/16974/53816027.pdf?sequence=1
"""

from pulp import *
from collections import defaultdict

def schedule(Jobs, Agents, D, C, R, B, P, M):
    """
    Finds the optimal scheduling of Jobs to Agents (workers) given
    Jobs - a set of Jobs (an iterable of hashable objects)
    Agents - a set of Agents/workers (an iterable of hashable objects)
    D - Dictionary detailing execution cost of running jobs on agents :
        D[job, agent] = time to run job on agent
    C - Dictionary detailing Communication cost sending results  of jobs
        between  agents :
        C[job, a1, a2] = time to comm results of job on from a1 to a2
    R - Additional constraint on start time of jobs, usually defaultdict(0)
    B - Dict saying which jobs can run on which agents:
        B[job, agent] == 1 if job can run on agent
    P - Dictionary containing precedence constraints - specifies DAG:
        P[job1, job2] == 1 if job1 immediately precedes job2
    M - Upper bound on makespan

    Returns
    prob - the pulp problem instance
    X - Dictionary detailing which jobs were run on which agents:
        X[job][agent] == 1 iff job was run on agent
    S - Starting time of each job
    Cmax - Optimal makespan

    """

    # Set up global precedence matrix
    Q = PtoQ(P)


    # PULP SETUP
    # The prob variable is created to contain the problem data
    prob = LpProblem("Scheduling Problem - Tompkins Formulation", LpMinimize)

    # The problem variables are created
    # X - 1 if job is scheduled to be completed by agent
    X = LpVariable.dicts("X", (Jobs, Agents), 0, 1, LpInteger)
    # S - Scheduled start time of job
    S = LpVariable.dicts("S", Jobs, 0, M, LpContinuous)

    # Theta - Whether two jobs overlap
    Theta = LpVariable.dicts("Theta", (Jobs, Jobs), 0, 1, LpInteger)
    # Makespan
    Cmax = LpVariable("C_max", 0, M, LpContinuous)

    #####################
    # 4.2.2 CONSTRAINTS #
    #####################

    # Objective function
    prob += Cmax

    # Subject to:

    # 4-1 Cmax is greater than the ending schedule time of all jobs
    for job in Jobs:
        prob += Cmax >= S[job] + lpSum([D[job, agent] * X[job][agent]
            for agent in Agents if B[job, agent]>0])

    # 4-2 an agent cannot be assigned a job unless it provides the services
    # necessary to complete that job
    for job in Jobs:
        for agent in Agents:
            if B[job, agent] == 0:
                prob += X[job][agent] == 0

    # 4-3 specifies that each job must be assigned once to exactly one agent
    for job in Jobs:
        prob += lpSum([X[job][agent] for agent in Agents]) == 1

    # 4-4 a job cannot start until its predecessors are completed and data has
    # been communicated to it if the preceding jobs were executed on a
    # different agent
    for (j,k), prec in P.items():
        if prec>0: # if j precedes k in the DAG
            prob += S[k]>=S[j]
            for a in Agents:
                for b in Agents:
                    if B[j,a] and B[k,b]: # a is capable of j and b capable of k
                        prob += S[k] >= (S[j] +
                                (D[j,a] + C[j,a,b]) * (X[j][a] + X[k][b] -1))

    # 4-5 a job cannot start until after its release time
    for job in Jobs:
        if R[job]>0:
            prob += S[job] >= R[job]

    # Collectively, (4-6) and (4-7) specify that an agent may process at most
    # one job at a time

    # 4-6
    for j in Jobs:
        for k in Jobs:
            if j==k or Q[j,k]!=0:
                continue
            prob += S[k] - lpSum([D[j,a]*X[j][a] for a in Agents]) - S[j] >= (
                    -M*Theta[j][k])
            # The following line had a < in the paper. We've switched to <=
            # Uncertain if this is a good idea
            prob += S[k] - lpSum([D[j,a]*X[j][a] for a in Agents]) - S[j] <= (
                    M*(1-Theta[j][k]))
    # 4-7 if two jobs j and k are assigned to the same agent, their execution
    # times may not overlap
    for j in Jobs:
        for k in Jobs:
            for a in Agents:
                prob += X[j][a] + X[k][a] + Theta[j][k] + Theta[k][j] <= 3

    return prob, X, S, Cmax

def PtoQ(P):
    """
    Construct full job precedence graph from immediate precedence graph

    Inputs:
    P - Dictionary encoding the immediate precedence graph:
        P[job1, job2] == 1 iff job1 immediately precedes job2

    Outputs:
    Q - Dictionary encoding full precedence graph:
        Q[job1, job2] == 1 if job1 comes anytime before job2
    """
    Q = defaultdict(lambda:0)
    # Add one-time-step knowledge
    for (i,j), prec in P.items():
        Q[i,j] = prec

    changed = True
    while(changed):
        changed = False
        for (i,j), prec in P.items(): # i comes immediately before j
            if not prec:
                continue
            for (jj, k), prec in Q.items(): # j comes sometime before k
                if jj != j or not prec:
                    continue
                if not Q[i,k]: # Didn't know i comes sometime before k?
                    changed = True # We changed Q
                    Q[i,k] = 1 # Now we do.
    return Q
