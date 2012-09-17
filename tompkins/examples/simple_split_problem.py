# a -> 1 -> b -> 2 -> d
#        -> c -> 3 -> e

from tompkins.dag_schedule import send, recv

a,b,c,d,e = 'abcde'
A,B,C = 'ABC'
usedby = {a: (1,), b: (2,), c: (3,), d:(), e:()}
outputsof = {1: (b, c), 2: (d,), 3: (e, )}

# unidag = bidag_to_unidag(usedby, outputsof)
unidag = {1: (2, 3), 2: (), 3: ()}
agents = (A, B, C)

def computation_cost(job, agent):
    if (job, agent) in [(1,'A'), (2, 'B'), (3, 'C')]:
        return 0
    else:
        return 3

def communication_cost(job, agent1, agent2):
    if agent1 == agent2:
        return 0
    return 1
def bicommunication_cost(var, agent1, agent2):
    if agent1 == agent2:
        return 0
    return 1

def R(job):
    return 0

def B(job, agent):
    return 1

M = 10

solution = {
        'dags':
            {'A': {1: (send('A', 'B', 1, 2), send('A', 'C', 1, 3)),
                   send('A', 'B', 1, 2): (),
                   send('A', 'C', 1, 3): ()},
             'B': {2: (), ('recv', 'A', 'B', 1, 2): (2,)},
             'C': {3: (), ('recv', 'A', 'C', 1, 3): (3,)}},
        'makespan': 1,
        'sched': [(1, 0.0, 'A'), (2, 1.0, 'B'), (3, 1.0, 'C')],
#        'bidags':
#            {'A': ({a: (1,), b: (send('A', 'B'), ), c: (send('A', 'C'),)},
#                   {1: (b, c), send('A', 'B'): (), send('A', 'C'): ()}),
#             'B': ({b: (2,), d: ()},
#                 {recv('A', 'B'): (b,), 2: (d,)}),
#             'C': ({c: (3,), e: ()},
#                 {recv('A', 'C'): (c,), 3: (e,)})}
            }
