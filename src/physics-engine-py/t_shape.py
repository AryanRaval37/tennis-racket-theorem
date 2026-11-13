from engine import System

m = 1 # 1 kg

# define the distances of these masses from the origin
x = 1
y = 2

# real dirty way of doing this, should just use omega
v = 1 # note this is velocity of the mass on x axis
# spinning about intermediate axes meaning all 4 masses not on y axis with velocty
u = System(rigid=True)
u.add_mass(m, (x, 0, 0), (0, 0, -v))
u.add_mass(m, (-x, 0, 0), (0, 0, v))
u.add_mass(m, (0, 0, 0))
u.add_mass(m, (0, y, 0))

u.export_csv('t_shape_py.csv', 0.001, 60, 100)
