from tompkins.dag import (manydags, unidag_to_P, send, recv, schedule, issend,
        isrecv, replace_send_recv)
from tompkins.examples.simple_split_problem import (unidag, agents,
        computation_cost, communication_cost, R, B, M, solution)

def test_jobs_where():
    pass

def test_unidag_to_P():
    d = unidag_to_P({1: (2, 3)})
    assert d[1,2] == 1 and d[1,3] == 1 and d[2,3] == 0
    assert unidag_to_P({1: (2, 3), 3: (4,)}) == {(1,2): 1, (1,3): 1, (3,4): 1}

def test_manydags_simple():
    # 1 -> 2 -> 3
    dag = {1: (2,), 2: (3, ), 3:()}
    jobson = {'A': (1, 2), 'B': (3, )}

    dags = manydags(dag, jobson)
    assert dags['A'] == {1: (2, ),
                         2: (send('A', 'B', 2, 3), ),
                         send('A', 'B', 2, 3): ()}
    assert dags['B'] == {recv('A', 'B', 2, 3): (3, ), 3:()}

def test_manydags_less_simple():
    # 1 -> 2
    #   -> 3

    dag = {1: (2, 3), 2: (), 3:()}
    jobson = {'A': (1,), 'B': (2, ), 'C':(3,)}

    dags = manydags(dag, jobson)
    assert dags['A'] == {1: (send('A', 'B', 1, 2), send('A', 'C', 1, 3)),
                         send('A', 'B', 1, 2): (),
                         send('A', 'C', 1, 3): ()}
    assert dags['B'] == {recv('A', 'B', 1, 2): (2, ), 2: ()}
    assert dags['C'] == {recv('A', 'C', 1, 3): (3, ), 3: ()}

def test_simple_split_problem_integrative():
    dags, sched, makespan = schedule(unidag, agents, computation_cost,
                                     communication_cost, R, B, M)

    assert dags == solution['dags']

    assert sched == solution['sched']

    assert makespan == solution['makespan']

def test_issend():
    assert issend(send(1,2,3,4))
    assert not issend(recv(1,2,3,4))
def test_isrecv():
    assert isrecv(recv(1,2,3,4))
    assert not isrecv(send(1,2,3,4))

def test_replace_send_recv():
    dag = {1: (2, send(1,2,3,4)), 2: (), send(1,2,3,4): (), recv(1,2,3,4): (1,)}
    o = replace_send_recv(dag, lambda a,b,c,d: a+b+c+d, lambda a,b,c,d: a*b*c*d)

    assert o == {1: (2, 1+2+3+4), 2: (), 1+2+3+4: (), 1*2*3*4: (1,)}
