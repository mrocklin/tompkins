from tompkins import schedule, PtoQ
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
