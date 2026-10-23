import numpy as np

class Universe:
    def __init__(self):
        self.x, self.v, self.m = [], [], []
        self.springs = [] # (i, j, k, rest_length)
        self.forces = [] # force functions f(x, v, t) -> (N, 3) array of forces on every mass
        self.t = 0.0

    # Adds mass m with position x and initial velocity v to the universe, returns its index
    def add_mass(self, m, x, v=(0, 0, 0)):
        self.m.append(m)
        self.x.append(x)
        self.v.append(v)
        return len(self.m) - 1

    # Adds a spring between ith and jth mass with stiffness k, unstretched at the current positions
    def add_spring(self, i, j, k):
        rest = np.linalg.norm(np.subtract(self.x[j], self.x[i]))
        self.springs.append((i, j, k, rest))

    # Adds a force function f(x, v, t) -> (N, 3) array
    # It gives you the current pos, velocities and time of the simulation, and your function should return the force on each mass
    def add_force(self, f):
        self.forces.append(f)

    # call once before first step
    def _build(self):
        self.x = np.array(self.x, float)
        self.v = np.array(self.v, float)
        self.m = np.array(self.m, float).reshape(-1, 1) # (N, 1)
        if self.springs:
            self.forces.append(self._spring_force)

    def _spring_force(self, x, v, t):
        F = np.zeros_like(x)
        for (i, j, k, rest) in self.springs:
            d = x[j] - x[i] # points from i to j
            r = np.linalg.norm(d)
            f = k * (r - rest) * d / r # stretched -> pulls i toward j
            F[i] += f
            F[j] -= f # Newton's 3rd law
        return F

    def total_force(self):
        return sum(f(self.x, self.v, self.t) for f in self.forces)

    # Verlet integration
    def step(self, dt):
        self.v += 0.5*dt*self.force_cached/self.m
        self.x += dt*self.v
        self.t += dt
        self.force_cached = self.total_force()
        self.v += 0.5*dt*self.force_cached/self.m

    def run(self, dt, T):
        if isinstance(self.x, list): # build only once, so a second run continues instead of doubling springs
            self._build()
        self.force_cached = self.total_force()
        for _ in range(round((T - self.t) / dt)):
            self.step(dt)
