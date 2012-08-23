from dag_schedule import manydags, unidag_to_P, send, recv, schedule

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

def test_simple_split_problem_integrative():
    from simple_split_problem import (unidag, agents, computation_cost,
            communication_cost, R, B, M)
    dags, sched, makespan = schedule(unidag, agents, computation_cost,
                                     communication_cost, R, B, M)
    assert dags == (
            {'A': {1: (('send', 'A', 'B', 1, 2), ('send', 'A', 'C', 1, 3))},
             'B': {2: (), ('recv', 'A', 'B', 1, 2): (2,)},
             'C': {3: (), ('recv', 'A', 'C', 1, 3): (3,)}})

    assert sched == [(1, 0.0, 'A'), (2, 1.0, 'B'), (3, 1.0, 'C')]

    assert makespan == 1
