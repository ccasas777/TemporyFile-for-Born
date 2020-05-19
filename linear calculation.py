# ######################################################################
# ######################################################################
# ######################################################################

from matrix import *
"""
For the following example, you would call doit(-3, 5, 3):
3 robot positions
  initially: -3
  moves by 5
  moves by 3



which should return a mu of:
[[-3.0],
 [2.0],
 [5.0]]
"""


def doit(initial_pos, move1, move2, dL_1, dL_2, dL_3):
    #
    x = matrix([[initial_pos - move1 - dL_1], [move1 - move2 - dL_2], [move2 - dL_3], [dL_1 + dL_3 + dL_2]])
    omega = matrix([[3, -1, 0, -1],
                    [-1, 3, -1, -1],
                    [0, -1, 2, -1],
                    [-1,-1 , -1, 3]])
    mu = omega.inverse() * x
    #
    return mu


print(doit(-3, 5, 3, 10, 5, 3))
