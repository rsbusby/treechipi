import numpy as np

DEBUG = 0

# hack damping coefficient
damp = 0.98

# Gaussian pulse
t0 = 20
spread = 8

t = 20

maxEx = 0.0
minEx = 0.0
signal = 0
signal2 = 0
fdtd_const = 20
signalGain = 1.0;
hiVal = 10000;
countt = 0;
maxPixel = 0;
# Number of time steps
nsteps=100;
# Cell size and time stepping
#c0 = 3.e8
#dx = 0.01
#dt = dx / (2. * c0)

# Constants
#cc = c0 * dt / dx

#cc = 0.25


# Initialize vectors
#ex1[ke];
#float hy1[ke];
#float ex2[ke];
#float hy2[ke];
#
#
#
# #initialize EM arrays
# for k in range(1, ke):
#     ex1[k] = 0.0
#     hy1[k] = 0.0
#     ex2[k] = 0.0
#     hy2[k] = 0.0
#

class FDTD1D(object):

    def __init__(self, ke, **kwargs):

        self.ke = ke
        self.ex = np.zeros(self.ke)
        self.hy = np.zeros(self.ke)
        self.ex = np.zeros(self.ke)
        self.hy = np.zeros(self.ke)

        self.cc = kwargs.get('cc', 0.5)
        print(f'\n\n\nFDTD cc is {self.cc}\n\n\n')

        self.threshold = 0.001

        self.verbosity = 1

    def step_slow(self, e0):

        # E field loop
        for k in range(1, self.ke, 1):
            self.ex[k] = damp * self.ex[k] + self.cc * (self.hy[k - 1] - self.hy[k])

        # Source
        if e0 > self.threshold:
            self.ex[0] = e0 #np.pow(np.exp(-.5 * ((t - t0) / spread)), 2)
            if self.verbosity:
                print(f"e0: {e0}")
        else:
            # reflects B
            self.ex[0] = 0.0

        # H field loop
        for k in range(0, self.ke - 1, 1):
            # hy[k]=damp*(hy[k]+cc*(ex[k]-ex[k+1]));
            self.hy[k] = (self.hy[k] + self.cc * (self.ex[k] - self.ex[k + 1]))

    # @staticmethod
    # def utah_fdtd_step(ex, hy, e0, threshold, verbosity=1):
    #
    #   # E field loop
    #     for k in range(1, ke):
    #         ex[k]=damp*ex[k]+cc*(hy[k-1]-hy[k])
    #
    #   # Source
    #     if e0 > threshold:
    #         ex[0] = e0  #pow(exp(-.5*((t-t0)/spread)), 2)
    #
    #     if verbosity:
    #         print(e0)
    #
    #     else:
    #         # reflects B
    #         ex[0] = 0.0;
    #
    #
    #   # H field loop
    #     for k in range(0, ke - 1, 1):
    #         #hy[k]=damp*(hy[k]+cc*(ex[k]-ex[k+1]));
    #         hy[k]=(hy[k]+cc*(ex[k]-ex[k+1]))
    #
    #
    #
    #
