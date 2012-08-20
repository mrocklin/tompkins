Static Scheduling with Integer Programming
==========================================

This module describes a highly flexible scheduling problem by encoding it as a
Mixed Integer Linear Program (MILP) using the 
[pulp framework](http://code.google.com/p/pulp-or/)
This framework can then call any of several external codes[2] to solve

This formulation of the MILP was specified in chapters 4.1, 4.2 in the
following masters thesis. Section and equation numbers are cited.

["Optimization Techniques for Task Allocation and Scheduling in Distributed Multi-Agent Operations"](http://dspace.mit.edu/bitstream/handle/1721.1/16974/53816027.pdf?sequence=1)

by

Mark F. Tompkins, June 2003, Masters thesis for MIT Dept EECS

[1] sudo easy_install pulp

[2] On ubuntu we used "sudo apt-get install glpk"
