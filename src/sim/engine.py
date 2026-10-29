import numpy as np

class System:
    # rigid=True connects every pair of masses with a spring of stiffness k when the system is built
    def __init__(self, rigid=False, k=1e5):
        self.rigid, self.k = rigid, k
        self.x, self.v, self.m = [], [], []
        self.springs = [] # (i, j, k, rest_length)
        self.forces = [] # force functions f(x, v, t) -> (N, 3) array of forces on every mass
        self.t = 0.0

    # Adds mass m with position x and initial velocity v to the system, returns its index
    # x and v are expected to be 3 element tuples
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
        # if body is rigid connect any two pairs of masses with a spring.
        if self.rigid:
            linked = {(i, j) for i, j, _, _ in self.springs}
            for i in range(len(self.m)):
                for j in range(i + 1, len(self.m)):
                    if (i, j) not in linked and (j, i) not in linked:
                        self.add_spring(i, j, self.k)
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
            F[j] -= f
        return F

    def total_force(self):
        return sum(f(self.x, self.v, self.t) for f in self.forces)

    # Verlet integration
    # considered rk4 here but learnt that apparently verlet conservers energy but rk4 might lose it even though per step rk4 is more accurate
    def step(self, dt):
        self.v += 0.5*dt*self.force_cached/self.m
        self.x += dt*self.v
        self.t += dt
        self.force_cached = self.total_force()
        self.v += 0.5*dt*self.force_cached/self.m

    def run(self, dt, T):
        if isinstance(self.x, list): # build only once
            self._build()
        self.force_cached = self.total_force()
        for _ in range(round((T - self.t) / dt)):
            self.step(dt)

    # ! AI generated function to export csv
    # Runs until time T like run(), writing every mass's position fps times per simulated second
    # Rows: t, x0, y0, z0, x1, y1, z1, ...   Lines starting with # are metadata
    def export_csv(self, path, dt, fps, T):
        t0, rows = self.t, []
        for frame in range(round((T - t0) * fps) + 1):
            self.run(dt, t0 + frame / fps)
            rows.append([self.t, *self.x.ravel()])
        cols = ["t"] + [f"{c}{i}" for i in range(len(self.m)) for c in "xyz"]
        header = "\n".join([
            f"dt={dt} fps={fps}",
            "masses=" + ",".join(f"{m:g}" for m in self.m.ravel()),
            "springs=" + ",".join(f"{i}-{j}" for i, j, _, _ in self.springs),
            ",".join(cols),
        ])
        np.savetxt(path, rows, delimiter=",", fmt="%.12g", header=header) # full precision; read with np.loadtxt(path, delimiter=",")
