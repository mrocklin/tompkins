from tompkins import (schedule, PtoQ, jobs_when_where, manydags, send, recv,
        unidag_to_P)
from collections import defaultdict

def test_schedule():
    from simple_scheduling_problem import Jobs, Agents, D, C, R, B, P, M
    prob, X, S, Cmax = schedule(Jobs, Agents, D, C, R, B, P, M)
    prob.solve()
    assert Cmax.value() == 14
    assert S['start'].value() == 0
    assert S['end'].value() == Cmax.value()

def test_PtoQ():
    P = defaultdict(lambda : 0)
    P['a', 'b'] = 1
    P['b', 'c'] = 1
    Q = PtoQ(P)
    assert Q['a','b'] and Q['b', 'c'] and Q['a', 'c']

def test_jobs_when_where():
    from simple_scheduling_problem import Jobs, Agents, D, C, R, B, P, M
    prob, X, S, Cmax = schedule(Jobs, Agents, D, C, R, B, P, M)
    result = jobs_when_where(prob, X, S, Cmax)
    assert isinstance(result, list)
    assert len(result) == len(S)
    job, time, machine = result[0]
    assert job == 'start'
    assert time == 0
    assert machine in Agents

def test_jobs_where():
    pass

def test_unidag_to_P():
    assert unidag_to_P({1: (2, 3)}) == {(1,2): 1, (1,3): 1}
    assert unidag_to_P({1: (2, 3), 3: (4,)}) == {(1,2): 1, (1,3): 1, (3,4): 1}

def test_manydags_simple():
    # 1 -> 2 -> 3
    dag = {1: (2,), 2: (3, ), 3:()}
    jobson = {'A': (1, 2), 'B': (3, )}

    dags = manydags(dag, jobson)
    assert dags['A'] == {1: (2, ), 2: (send('A', 'B', 2, 3), )}
    assert dags['B'] == {recv('A', 'B', 2, 3): (3, ), 3:()}

def test_manydags_less_simple():
    # 1 -> 2
    #   -> 3

    dag = {1: (2, 3), 2: (), 3:()}
    jobson = {'A': (1,), 'B': (2, ), 'C':(3,)}

    dags = manydags(dag, jobson)
    assert dags['A'] == {1: (send('A', 'B', 1, 2), send('A', 'C', 1, 3))}
    assert dags['B'] == {recv('A', 'B', 1, 2): (2, ), 2: ()}
    assert dags['C'] == {recv('A', 'C', 1, 3): (3, ), 3: ()}
