from tompkins import schedule, PtoQ, jobs_when_where
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

