from Tompkins import schedule
from collections import defaultdict
from pulp import value
"""
A sample problem
>>> x = matrix('x')
>>> y = x*x
>>> z = y.sum()
>>> f = function([x], z)

Architecture
CPU --- GPU

Data starts and must end on the CPU
"""

# 4.2.1 problem Variables
# Input Parameters - Sets
Jobs = ['start', 'gemm', 'sum', 'end']
Agents = ['cpu', 'gpu'] # workers
n = len(Jobs)
m = len(Agents)

# Indicator Variables
# Immediate job precedence graph - specifies DAG
# P[job1, job2] == 1 if job1 directly precedes job2
P = defaultdict(lambda:0)
P['start','gemm'] = 1
P['gemm','sum'] = 1
P['sum','end'] = 1

# Agent ability matrix
# B[job, agent] == 1 if job can be performed by agent
B = defaultdict(lambda:1)
for agent in Agents:
    if agent != 'cpu':
        B['start', agent] = 0 # must start on cpu
        B['end', agent] = 0 # must start on cpu

# DATA Values
# Execution Delay Matrix - Time cost of performing Jobs[i] on Agent[j]
D = defaultdict(lambda:0)
D['gemm','cpu'] = 10 # gemm on cpu
D['gemm','gpu'] = 3 # gemm on gpu
D['sum','cpu'] = 5 # sum on cpu
D['sum','gpu'] = 9 # sum on gpu

# Communication Delay matrix - Cost of sending results of job from
# agent to agent
C = defaultdict(lambda:0)
for a,b in [('cpu', 'gpu'), ('gpu', 'cpu')]:
    # cost to communicate matrices is 3 (symmetric)
    C['start', a,b] = 3
    C['gemm', a,b] = 3
    # cost to communicate scalar is .01 (symmetric)
    C['sum', a,b] = .01

# Job Release Times - Additional constraints on availablility of Jobs
# R = np.zeros(n)
R = defaultdict(lambda:0)

# Maximum makespan
M = 100

# Set up the Mixed Integer Linear Program
prob, X, S, Cmax = schedule(Jobs, Agents, D, C, R, B, P, M)

prob.solve()

print "Makespan: ", value(Cmax)
def runs_on(job, X):
    return [k for k,v in X[job].items() if value(v)==1][0]

sched = [(job,(value(time), runs_on(job,X))) for job, time in S.items()]
sched.sort(key=lambda x:x[1])
print "Schedule: ", sched

