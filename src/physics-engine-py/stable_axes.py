# quick dirty file to test stability of different axes
# the unstiff sprigs testing was also done here.
from engine import System

m = 1

x = 1
y = 2
z = 3

w = 1
eps = 0.01

u = System(rigid=True)
u.add_mass(m, (x, 0, 0), (0, 0, -eps*w*x))
u.add_mass(m, (-x, 0, 0), (0, 0, eps*w*x))
u.add_mass(m, (0, y, 0), (0, 0, y*w))
u.add_mass(m, (0, -y, 0), (0, 0, -y*w))
u.add_mass(m, (0, 0, z), (eps*w*z, -z*w, 0))
u.add_mass(m, (0, 0, -z), (-eps*w*z, z*w, 0))
u.export_csv('stable_x_py.csv', 0.001, 60, 100)

u = System(rigid=True)
u.add_mass(m, (x, 0, 0), (0, eps*w*x, -x*w))
u.add_mass(m, (-x, 0, 0), (0, -eps*w*x, x*w))
u.add_mass(m, (0, y, 0), (-eps*w*y, 0, 0))
u.add_mass(m, (0, -y, 0), (eps*w*y, 0, 0))
u.add_mass(m, (0, 0, z), (z*w, 0, 0))
u.add_mass(m, (0, 0, -z), (-z*w, 0, 0))
u.export_csv('stable_y_py.csv', 0.001, 60, 100)

u = System(rigid=True)
u.add_mass(m, (x, 0, 0), (0, x*w, 0))
u.add_mass(m, (-x, 0, 0), (0, -x*w, 0))
u.add_mass(m, (0, y, 0), (-y*w, 0, eps*w*y))
u.add_mass(m, (0, -y, 0), (y*w, 0, -eps*w*y))
u.add_mass(m, (0, 0, z), (0, -eps*w*z, 0))
u.add_mass(m, (0, 0, -z), (0, eps*w*z, 0))
u.export_csv('stable_z_py.csv', 0.001, 60, 100)
