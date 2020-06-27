# ----------
# User Instructions:
#
# Define a function, search() that returns a list
# in the form of [optimal path length, row, col]. For
# the grid shown below, your function should output
# [11, 4, 5].
#
# If there is no valid path from the start point
# to the goal, your function should return the string
# 'fail'
# ----------

# Grid format:t
#   0 = Navigable space
#   1 = Occupied space


grid = [[1, 1, 1, 0, 0, 0],
        [1, 1, 1, 0, 1, 0],
        [0, 0, 0, 0, 0, 0],
        [1, 1, 1, 0, 1, 1],
        [1, 1, 1, 0, 1, 1]]

value = [[9, 8, 7, 6, 5, 4],
         [8, 7, 6, 5, 4, 3],
         [7, 6, 5, 4, 3, 2],
         [6, 5, 4, 3, 2, 1],
         [5, 4, 3, 2, 1, 0]]

#value generation:
#f(x,y) = fmin(x',y') +1

init = [4, 3]
goal = [2, 0]
cost = 1

delta = [[-1, 0],  # go up
         [0, -1],  # go left
         [1, 0],  # go down
         [0, 1]]  # go right

delta_name = ['^', '<', 'v', '>']


def search():
    # ----------------------------------------
    # insert code here
    # ----------------------------------------
    closed = [[0 for row in range(len(grid[0]))] for col in range(len(grid))]
    expand = [[-1 for row in range(len(grid[0]))] for col in range(len(grid))]
    policy = [['' for row in range(len(grid[0]))] for col in range(len(grid))]
    closed[init[0]][init[1]] = 1
    x = init[0]
    y = init[1]
    g = 0
    policy[x][y] = '#'
    open = [[g, x, y]]
    print('initial open list')
    for i in range(len(open)):
        print(open)
        print('-----------')
    found = False
    resign = False
    s = 0
    while found is False and resign is False:
        if len(open) == 0:
            resign = True
            print('fail')
        else:
            open.sort()
            print('current open list:')
            print(open)
            print('---------')
            open.reverse()
            next = open.pop()
            x = next[1]
            y = next[2]
            g = next[0]
            s += 1
            expand[x][y] = s #record occupied path
            
            print('take the item:')
            print(next)
            print('------------')
            if x == goal[0] and y == goal[1]:
                found = True
                path = next
                policy[x][y] = '*'
                print('found')
            else:
                for i in range(len(delta)): #try all directions
                    x2 = x + delta[i][0]
                    y2 = y + delta[i][1]
                    if x2 >= 0 and x2 < len(grid) and y2 >= 0 and y2 < len(grid[0]):
                        if closed[x2][y2] == 0 and grid[x2][y2] == 0:
                            g2 = g + cost + value[x2][y2]
                            open.append([g2, x2, y2])
                            closed[x2][y2] = 1
                            policy[x2][y2] = delta_name[i]

    return policy


expand = search()
for i in range(len(expand)):
    print(expand[i])