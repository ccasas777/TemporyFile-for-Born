# ------------
# User Instructions
#
# In this problem you will implement SLAM in a 2 dimensional
# world. Please define a function, slam, which takes five
# parameters as input and returns the vector mu. This vector
# should have x, y coordinates interlaced, so for example,
# if there were 2 poses and 2 landmarks, mu would look like:
#
#  mu =  matrix([[Px0],
#                [Py0],
#                [Px1],
#                [Py1],
#                [Lx0],
#                [Ly0],
#                [Lx1],
#                [Ly1]])
#
# data - This is the data that is generated with the included
#        make_data function. You can also use test_data to
#        make sure your function gives the correct result.
#
# N -    The number of time steps.
#
# num_landmarks - The number of landmarks.
#
# motion_noise - The noise associated with motion. The update
#                strength for motion should be 1.0 / motion_noise.
#
# measurement_noise - The noise associated with measurement.
#                     The update strength for measurement should be
#                     1.0 / measurement_noise.
#
#

from math import *
import random


# ===============================================================
#
# SLAM in a rectolinear world (we avoid non-linearities)
#
#
# ===============================================================

class matrix:

    # implements basic operations of a matrix class

    # ------------
    #
    # initialization - can be called with an initial matrix
    #

    def __init__(self, value=[[]]):
        self.value = value
        self.dimx = len(value)
        self.dimy = len(value[0])
        if value == [[]]:
            self.dimx = 0

    # ------------
    #
    # makes matrix of a certain size and sets each element to zero
    #

    def zero(self, dimx, dimy):
        if dimy == 0:
            dimy = dimx
        # check if valid dimensions
        if dimx < 1 or dimy < 1:
            raise (ValueError, "Invalid size of matrix")
        else:
            self.dimx = dimx
            self.dimy = dimy
            self.value = [[0.0 for row in range(dimy)] for col in range(dimx)]

    # ------------
    #
    # makes matrix of a certain (square) size and turns matrix into identity matrix
    #

    def identity(self, dim):
        # check if valid dimension
        if dim < 1:
            raise (ValueError, "Invalid size of matrix")
        else:
            self.dimx = dim
            self.dimy = dim
            self.value = [[0.0 for row in range(dim)] for col in range(dim)]
            for i in range(dim):
                self.value[i][i] = 1.0

    # ------------
    #
    # prints out values of matrix
    #

    def show(self, txt=''):
        for i in range(len(self.value)):
            print(txt + '[' + ', '.join('%.3f' % x for x in self.value[i]) + ']')
        print(' ')

    # ------------
    #
    # defines elmement-wise matrix addition. Both matrices must be of equal dimensions
    #

    def __add__(self, other):
        # check if correct dimensions
        if self.dimx != other.dimx or self.dimy != other.dimy:
            raise (ValueError, "Matrices must be of equal dimension to add")
        else:
            # add if correct dimensions
            res = matrix()
            res.zero(self.dimx, self.dimy)
            for i in range(self.dimx):
                for j in range(self.dimy):
                    res.value[i][j] = self.value[i][j] + other.value[i][j]
            return res

    # ------------
    #
    # defines elmement-wise matrix subtraction. Both matrices must be of equal dimensions
    #

    def __sub__(self, other):
        # check if correct dimensions
        if self.dimx != other.dimx or self.dimy != other.dimy:
            raise (ValueError, "Matrices must be of equal dimension to subtract")
        else:
            # subtract if correct dimensions
            res = matrix()
            res.zero(self.dimx, self.dimy)
            for i in range(self.dimx):
                for j in range(self.dimy):
                    res.value[i][j] = self.value[i][j] - other.value[i][j]
            return res

    # ------------
    #
    # defines multiplication. Both matrices must be of fitting dimensions
    #

    def __mul__(self, other):
        # check if correct dimensions
        if self.dimy != other.dimx:
            raise (ValueError, "Matrices must be m*n and n*p to multiply")
        else:
            # multiply if correct dimensions
            res = matrix()
            res.zero(self.dimx, other.dimy)
            for i in range(self.dimx):
                for j in range(other.dimy):
                    for k in range(self.dimy):
                        res.value[i][j] += self.value[i][k] * other.value[k][j]
        return res

    # ------------
    #
    # returns a matrix transpose
    #

    def transpose(self):
        # compute transpose
        res = matrix()
        res.zero(self.dimy, self.dimx)
        for i in range(self.dimx):
            for j in range(self.dimy):
                res.value[j][i] = self.value[i][j]
        return res

    def take(self, list1, list2=[]):
        if list2 == []:
            list2 = list1
        if len(list1) > self.dimx or len(list2) > self.dimy:
            raise (ValueError, "list invalid in take()")

        res = matrix()
        res.zero(len(list1), len(list2))
        for i in range(len(list1)):
            for j in range(len(list2)):
                res.value[i][j] = self.value[list1[i]][list2[j]]
        return res


    def expand(self, dimx, dimy, list1, list2=[]):
        if list2 == []:
            list2 = list1
        if len(list1) > self.dimx or len(list2) > self.dimy:
            raise (ValueError, "list invalid in expand()")

        res = matrix()
        res.zero(dimx, dimy)
        for i in range(len(list1)):
            for j in range(len(list2)):
                res.value[list1[i]][list2[j]] = self.value[i][j]
        return res

    # ------------
    #
    # Computes the upper triangular Cholesky factorization of
    # a positive definite matrix.
    # This code is based on http://adorio-research.org/wordpress/?p=4560
    #

    def Cholesky(self, ztol=1.0e-5):

        res = matrix()
        res.zero(self.dimx, self.dimx)

        for i in range(self.dimx):
            S = sum([(res.value[k][i]) ** 2 for k in range(i)])
            d = self.value[i][i] - S
            if abs(d) < ztol:
                res.value[i][i] = 0.0
            else:
                if d < 0.0:
                    raise (ValueError, "Matrix not positive-definite")
                res.value[i][i] = sqrt(d)
            for j in range(i + 1, self.dimx):
                S = sum([res.value[k][i] * res.value[k][j] for k in range(i)])
                if abs(S) < ztol:
                    S = 0.0
                try:
                    res.value[i][j] = (self.value[i][j] - S) / res.value[i][i]
                except:
                    raise (ValueError, "Zero diagonal")
        return res

        # ------------

    #
    # Computes inverse of matrix given its Cholesky upper Triangular
    # decomposition of matrix.
    # This code is based on http://adorio-research.org/wordpress/?p=4560
    #

    def CholeskyInverse(self):

        res = matrix()
        res.zero(self.dimx, self.dimx)

        # Backward step for inverse.
        for j in reversed(range(self.dimx)):
            tjj = self.value[j][j]
            S = sum([self.value[j][k] * res.value[j][k] for k in range(j + 1, self.dimx)])
            res.value[j][j] = 1.0 / tjj ** 2 - S / tjj
            for i in reversed(range(j)):
                res.value[j][i] = res.value[i][j] = \
                    -sum([self.value[i][k] * res.value[k][j] for k in \
                          range(i + 1, self.dimx)]) / self.value[i][i]
        return res

    # ------------
    #
    # computes and returns the inverse of a square matrix
    #
    def inverse(self):
        aux = self.Cholesky()
        res = aux.CholeskyInverse()
        return res

    # ------------
    #
    # prints matrix (needs work!)
    #
    def __repr__(self):
        return repr(self.value)


####### ABOVE CODES are the tools of matrix calculation ################

# --------------------------------
#
# print the result of SLAM, the robot pose(s) and the landmarks
#

def print_result(N, num_landmarks, result):
    print('')
    print(
    'Estimated Pose(s):')
    for i in range(N):
        print(
        '    [' + ', '.join('%.3f' % x for x in result.value[2 * i]) + ', ' \
        + ', '.join('%.3f' % x for x in result.value[2 * i + 1]) + ']')
    print('')
    print(
    'Estimated Landmarks:')
    for i in range(num_landmarks):
        print(
        '    [' + ', '.join('%.3f' % x for x in result.value[2 * (N + i)]) + ', ' \
        + ', '.join('%.3f' % x for x in result.value[2 * (N + i) + 1]) + ']')


# --------------------------------
#
# slam - retains entire path and all landmarks
#

def slam(data, N, num_landmarks, motion_noise, measurement_noise):
    #
    #
    initial_pos= 50

    Omega = matrix([[1.0, 0.0],
                    [0.0, 1.0]])
    Xi = matrix([[initial_pos],
                 [initial_pos]])

    l=N-1
    dim = 2*(l + num_landmarks + 1)
    Omega  = Omega.expand(dim,dim,[0,1])
    Xi = Xi.expand(dim,1,[0,1],[0])
    for i in range(l):

        # obtain information from measurements
        # about dx
        ix=2*i # x_index to restore data
        dx = data[i][1][0]
        # about dy
        iy=2*i+1 # y_index index to restore data
        dy = data[i][1][1]

        ### defined matrix and vector
        move_x = matrix([[1.0, -1.0],
                       [-1.0, 1.0]])
        dXi_x = matrix([[-dx],
                      [dx]])
        move_y = matrix([[1.0, -1.0],
                         [-1.0, 1.0]])
        dXi_y = matrix([[-dy],
                        [dy]])
        move_x = move_x.expand(dim,dim,[ix,ix+2])
        dXi_x = dXi_x.expand(dim,1,[ix,ix+2],[0])
        move_y = move_y.expand(dim, dim, [iy,iy+2])
        dXi_y = dXi_y.expand(dim, 1, [iy,iy+2], [0])

        ## adding to the Omega
        Omega += move_x
        Xi += dXi_x
        Omega += move_y
        Xi += dXi_y

        # Landmarks measurements
        num_meas = len(data[i][0])

        for j in range(num_meas):
            # the name of the Landmark
            num = data[i][0][j][0]

            # x,y _index to restore data
            numx=2*num
            numy=2*num+1
            Lx = data[i][0][j][1]
            Ly = data[i][0][j][2]

            ###defined matrix and vector
            L_x = matrix([[1.0, -1.0],
                       [-1.0, 1.0]])
            LXi_x = matrix([[-Lx],
                      [Lx]])
            L_x = L_x.expand(dim,dim,[ix,2*(l+1)+numx])
            LXi_x = LXi_x.expand(dim,1,[ix,2*(l+1)+numx],[0])

            L_y = matrix([[1.0, -1.0],
                          [-1.0, 1.0]])
            LXi_y = matrix([[-Ly],
                            [Ly]])
            L_y = L_y.expand(dim, dim, [iy, 2 * (l+1) + numy])
            LXi_y = LXi_y.expand(dim, 1, [iy, 2 * (l+1) + numy], [0])

            ## adding to the Omega
            Omega += L_x
            Xi += LXi_x
            Omega += L_y
            Xi += LXi_y

    mu=Omega.inverse()*Xi

    return mu



num_landmarks = 5  # number of landmarks
N = 20  # time steps
world_size = 100.0  # size of world
measurement_range = 50.0  # range at which we can sense landmarks
motion_noise = 2.0  # noise in robot motion
measurement_noise = 2.0  # noise in the measurements
distance = 20.0  # distance by which robot (intends to) move each iteratation

# -------------
# Testing
#
# Uncomment one of the test cases below to compare your results to
# the results shown for Test Case 1 and Test Case 2.

# test_data1 = [[[[1, 19.457599255548065, 23.8387362100849], [2, -13.195807561967236, 11.708840328458608],
#                 [3, -30.0954905279171, 15.387879242505843]], [-12.2607279422326, -15.801093326936487]],
#               [[[2, -0.4659930049620491, 28.088559771215664], [4, -17.866382374890936, -16.384904503932]],
#                [-12.2607279422326, -15.801093326936487]],
#               [[[4, -6.202512900833806, -1.823403210274639]], [-12.2607279422326, -15.801093326936487]],
#               [[[4, 7.412136480918645, 15.388585962142429]], [14.008259661173426, 14.274756084260822]],
#               [[[4, -7.526138813444998, -0.4563942429717849]], [14.008259661173426, 14.274756084260822]],
#               [[[2, -6.299793150150058, 29.047830407717623], [4, -21.93551130411791, -13.21956810989039]],
#                [14.008259661173426, 14.274756084260822]],
#               [[[1, 15.796300959032276, 30.65769689694247], [2, -18.64370821983482, 17.380022987031367]],
#                [14.008259661173426, 14.274756084260822]],
#               [[[1, 0.40311325410337906, 14.169429532679855], [2, -35.069349468466235, 2.4945558982439957]],
#                [14.008259661173426, 14.274756084260822]],
#               [[[1, -16.71340983241936, -2.777000269543834]], [-11.006096015782283, 16.699276945166858]],
#               [[[1, -3.611096830835776, -17.954019226763958]], [-19.693482634035977, 3.488085684573048]],
#               [[[1, 18.398273354362416, -22.705102332550947]], [-19.693482634035977, 3.488085684573048]],
#               [[[2, 2.789312482883833, -39.73720193121324]], [12.849049222879723, -15.326510824972983]], [
#                   [[1, 21.26897046581808, -10.121029799040915], [2, -11.917698965880655, -23.17711662602097],
#                    [3, -31.81167947898398, -16.7985673023331]], [12.849049222879723, -15.326510824972983]], [
#                   [[1, 10.48157743234859, 5.692957082575485], [2, -22.31488473554935, -5.389184118551409],
#                    [3, -40.81803984305378, -2.4703329790238118]], [12.849049222879723, -15.326510824972983]], [
#                   [[0, 10.591050242096598, -39.2051798967113], [1, -3.5675572049297553, 22.849456408289125],
#                    [2, -38.39251065320351, 7.288990306029511]], [12.849049222879723, -15.326510824972983]],
#               [[[0, -3.6225556479370766, -25.58006865235512]], [-7.8874682868419965, -18.379005523261092]],
#               [[[0, 1.9784503557879374, -6.5025974151499]], [-7.8874682868419965, -18.379005523261092]],
#               [[[0, 10.050665232782423, 11.026385307998742]], [-17.82919359778298, 9.062000642947142]],
#               [[[0, 26.526838150174818, -0.22563393232425621], [4, -33.70303936886652, 2.880339841013677]],
#                [-17.82919359778298, 9.062000642947142]]]
test_data2 = [[[[0, 26.543274387283322, -6.262538160312672], [3, 9.937396825799755, -9.128540360867689]],
               [18.92765331253674, -6.460955043986683]], [
                  [[0, 7.706544739722961, -3.758467215445748], [1, 17.03954411948937, 31.705489938553438],
                   [3, -11.61731288777497, -6.64964096716416]], [18.92765331253674, -6.460955043986683]], [
                  [[0, -12.35130507136378, 2.585119104239249], [1, -2.563534536165313, 38.22159657838369],
                   [3, -26.961236804740935, -0.4802312626141525]], [-11.167066095509824, 16.592065417497455]], [
                  [[0, 1.4138633151721272, -13.912454837810632], [1, 8.087721200818589, 20.51845934354381],
                   [3, -17.091723454402302, -16.521500551709707], [4, -7.414211721400232, 38.09191602674439]],
                  [-11.167066095509824, 16.592065417497455]], [
                  [[0, 12.886743222179561, -28.703968411636318], [1, 21.660953298391387, 3.4912891084614914],
                   [3, -6.401401414569506, -32.321583037341625], [4, 5.034079343639034, 23.102207946092893]],
                  [-11.167066095509824, 16.592065417497455]], [
                  [[1, 31.126317672358578, -10.036784369535214], [2, -38.70878528420893, 7.4987265861424595],
                   [4, 17.977218575473767, 6.150889254289742]], [-6.595520680493778, -18.88118393939265]],
              [[[1, 41.82460922922086, 7.847527392202475], [3, 15.711709540417502, -30.34633659912818]],
               [-6.595520680493778, -18.88118393939265]],
              [[[0, 40.18454208294434, -6.710999804403755], [3, 23.019508919299156, -10.12110867290604]],
               [-6.595520680493778, -18.88118393939265]],
              [[[3, 27.18579315312821, 8.067219022708391]], [-6.595520680493778, -18.88118393939265]],
              [[], [11.492663265706092, 16.36822198838621]],
              [[[3, 24.57154567653098, 13.461499960708197]], [11.492663265706092, 16.36822198838621]],
              [[[0, 31.61945290413707, 0.4272295085799329], [3, 16.97392299158991, -5.274596836133088]],
               [11.492663265706092, 16.36822198838621]], [
                  [[0, 22.407381798735177, -18.03500068379259], [1, 29.642444125196995, 17.3794951934614],
                   [3, 4.7969752441371645, -21.07505361639969], [4, 14.726069092569372, 32.75999422300078]],
                  [11.492663265706092, 16.36822198838621]], [
                  [[0, 10.705527984670137, -34.589764174299596], [1, 18.58772336795603, -0.20109708164787765],
                   [3, -4.839806195049413, -39.92208742305105], [4, 4.18824810165454, 14.146847823548889]],
                  [11.492663265706092, 16.36822198838621]],
              [[[1, 5.878492140223764, -19.955352450942357], [4, -7.059505455306587, -0.9740849280550585]],
               [19.628527845173146, 3.83678180657467]],
              [[[1, -11.150789592446378, -22.736641053247872], [4, -28.832815721158255, -3.9462962046291388]],
               [-19.841703647091965, 2.5113335861604362]],
              [[[1, 8.64427397916182, -20.286336970889053], [4, -5.036917727942285, -6.311739993868336]],
               [-5.946642674882207, -19.09548221169787]], [
                  [[0, 7.151866679283043, -39.56103232616369], [1, 16.01535401373368, -3.780995345194027],
                   [4, -3.04801331832137, 13.697362774960865]], [-5.946642674882207, -19.09548221169787]], [
                  [[0, 12.872879480504395, -19.707592098123207], [1, 22.236710716903136, 16.331770792606406],
                   [3, -4.841206109583004, -21.24604435851242], [4, 4.27111163223552, 32.25309748614184]],
                  [-5.946642674882207, -19.09548221169787]]]


result = slam(test_data2, 20, 5, 2.0, 2.0)
print_result(20, 5, result)

##  Test Case 1
##
##  Estimated Pose(s):
##      [49.999, 49.999]
##      [37.971, 33.650]
##      [26.183, 18.153]
##      [13.743, 2.114]
##      [28.095, 16.781]
##      [42.383, 30.900]
##      [55.829, 44.494]
##      [70.855, 59.697]
##      [85.695, 75.540]
##      [74.010, 92.431]
##      [53.543, 96.451]
##      [34.523, 100.078]
##      [48.621, 83.951]
##      [60.195, 68.105]
##      [73.776, 52.932]
##      [87.130, 38.536]
##      [80.301, 20.506]
##      [72.797, 2.943]
##      [55.244, 13.253]
##      [37.414, 22.315]
##
##  Estimated Landmarks:
##      [82.954, 13.537]
##      [70.493, 74.139]
##      [36.738, 61.279]
##      [18.696, 66.057]
##      [20.633, 16.873]


##  Test Case 2
##
##  Estimated Pose(s):
##      [49.999, 49.999]
##      [69.180, 45.664]
##      [87.742, 39.702]
##      [76.269, 56.309]
##      [64.316, 72.174]
##      [52.256, 88.151]
##      [44.058, 69.399]
##      [37.001, 49.916]
##      [30.923, 30.953]
##      [23.507, 11.417]
##      [34.179, 27.131]
##      [44.154, 43.844]
##      [54.805, 60.919]
##      [65.697, 78.544]
##      [77.467, 95.624]
##      [96.801, 98.819]
##      [75.956, 99.969]
##      [70.199, 81.179]
##      [64.053, 61.721]
##      [58.106, 42.626]
##
##  Estimated Landmarks:
##      [76.778, 42.885]
##      [85.064, 77.436]
##      [13.546, 95.649]
##      [59.448, 39.593]
##      [69.262, 94.238]

