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

def test_manydags_send_recv():
    # 1 -> 2 -> 3
    dag = {1: (2,), 2: (3, ), 3:()}
    jobson = {'A': (1, 2), 'B': (3, )}

    class Send(object):
        def __init__(self, *args):
            self.args = args
        def __eq__(self, other):
            return type(self) == type(other) and self.args == other.args
        def __hash__(self):
            return hash((type(self), self.args))
    class Recv(Send): pass

    dags = manydags(dag, jobson, send=Send, recv=Recv)
    assert dags['A'] == {1: (2, ),
                         2: (Send('A', 'B', 2, 3), ),
                         Send('A', 'B', 2, 3): ()}
    assert dags['B'] == {Recv('A', 'B', 2, 3): (3, ), 3:()}

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

def test_manydags_multivar():
    # 1 -> 2 -> 6
    #   -> 3 ->
    #   -> 4 ->
    #   -> 5 ->
    dag = {1: (2, 3, 4, 5), 2: (6,), 3: (6,), 4: (6,), 5: (6,), 6: ()}
    jobson = {'A': (1, 2, 6), 'B': (3, ), 'C':(4,), 'D': (5,)}
    dags = manydags(dag, jobson)
    assert dags == {'A': {1: (2, ('send', 'A', 'B', 1, 3),
                                 ('send', 'A', 'C', 1, 4),
                                 ('send', 'A', 'D', 1, 5)),
                          2: (6,),
                          6: (),
                          ('recv', 'B', 'A', 3, 6): (6,),
                          ('recv', 'C', 'A', 4, 6): (6,),
                          ('recv', 'D', 'A', 5, 6): (6,),
                          ('send', 'A', 'B', 1, 3): (),
                          ('send', 'A', 'C', 1, 4): (),
                          ('send', 'A', 'D', 1, 5): ()},
                    'B': {3: (('send', 'B', 'A', 3, 6),),
                          ('recv', 'A', 'B', 1, 3): (3,),
                          ('send', 'B', 'A', 3, 6): ()},
                    'C': {4: (('send', 'C', 'A', 4, 6),),
                          ('recv', 'A', 'C', 1, 4): (4,),
                          ('send', 'C', 'A', 4, 6): ()},
                    'D': {5: (('send', 'D', 'A', 5, 6),),
                          ('recv', 'A', 'D', 1, 5): (5,),
                          ('send', 'D', 'A', 5, 6): ()}}

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
