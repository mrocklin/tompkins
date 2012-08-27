from bidag_schedule import schedule


def test_simple_split_problem_integrative():
    from simple_split_problem import (usedby, outputsof, agents,
            computation_cost, bicommunication_cost, R, B, M)
    bidags, sched, makespan = schedule((usedby, outputsof), agents,
                            computation_cost, bicommunication_cost, R, B, M)

    from simple_split_problem import solution
    print bidags
    print solution['bidags']
    assert bidags == solution['bidags']

    assert sched == solution['sched']

    assert makespan == solution['makespan']
