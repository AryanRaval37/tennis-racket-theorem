from engine import System

m = 1 # 1 kg

# define the distances of these masses from the origin
x = 1
y = 2
z = 3

v = 1 # note this is velocity of the mass on x axis
# spinning about intermediate axes meaning all 4 masses not on y axis with velocty
u = System(rigid=True)
u.add_mass(m, (x, 0, 0), (0, 0, -v))
u.add_mass(m, (-x, 0, 0), (0, 0, v))
u.add_mass(m, (0, y, 0), (0, 0, 0.01))
u.add_mass(m, (0, -y, 0), (0, 0, -0.01))
u.add_mass(m, (0, 0, z), (z*v, 0, 0))
u.add_mass(m, (0, 0, -z), (-z*v, 0, 0))

u.export_csv('six_masses.csv', 0.001, 60, 100)
