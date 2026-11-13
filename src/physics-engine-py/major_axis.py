import numpy as np
from engine import System

m = 1
x, y, z = 1, 2, 3
k, c = 1, 0.7 # soft springs, damping c is what lets it lose energy and settle
w = np.array([0.1, 0, 1]) # spin about z (min I), slightly tilted toward x (max I)

u = System(rigid=True, k=k, c=c)
for r in [(x, 0, 0), (-x, 0, 0), (0, y, 0), (0, -y, 0), (0, 0, z), (0, 0, -z)]:
    u.add_mass(m, r, np.cross(w, r)) # v = w x r, the whole body spins together

u.export_csv('major_axis_py.csv', 0.005, 60, 1000)
