# a -> 1 -> b -> 2 -> d
#        -> c -> 3 -> e

from bidag import bidag_to_unidag
a,b,c,d,e = 'abcde'
A,B,C = 'ABC'
usedby = {a: (1,), b: (2,), c: (3,)}
outputsof = {1: (b, c), 2: (d,), 3: (e, )}

unidag = bidag_to_unidag(usedby, outputsof)

def computation_cost(job, agent):
    if (job, agent) in [(1,'A'), (2, 'B'), (3, 'C')]:
        return 0
    else:
        return 2

def communication_cost(job, agent1, agent2):
    if agent1 == agent2:
        return 0
    return 1

def R(job):
    return 0

def B(job, agent):
    return 1
