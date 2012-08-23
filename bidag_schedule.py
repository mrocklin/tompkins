from bidag import unidag_to_subbidag, bidag_to_unidag, communication_conversion
from dag_schedule import schedule as unidag_schedule

def schedule((usedby, outputsof), agents, compcost, bicommcost, R, B, M):
    unidag = bidag_to_unidag(usedby, outputsof)
    unicommcost = communication_conversion(usedby, outputsof, bicommcost)
    dags, sched, makespan = unidag_schedule(
                                unidag, agents, compcost, unicommcost, R, B, M)
    bidags = {agent: unidag_to_subbidag((usedby, outputsof), dags[agent])
                        for agent in dags}
    return bidags, sched, makespan
