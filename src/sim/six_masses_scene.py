# from pathlib import Path
import numpy as np
from manim import *

CSV = "six_masses.csv"
SPEED = 4 # simulated seconds per video second
COLORS = [BLUE, BLUE, YELLOW, YELLOW, RED, RED] # yellow = intermediate (y) axis

def read_springs(path):
    # finds the line "# springs=0-1,0-2,..." and turns it into [(0, 1), (0, 2), ...]
    for line in open(path):
        if line.startswith("# springs="):
            pairs = line.strip().removeprefix("# springs=").split(",")
            return [tuple(int(n) for n in pair.split("-")) for pair in pairs]

class SixMasses(ThreeDScene):
    def construct(self):
        data = np.loadtxt(CSV, delimiter=",") # rows: t, x0, y0, z0, x1, ...
        times = data[:, 0]
        positions = data[:, 1:].reshape(len(data), -1, 3) # positions[row, mass] = [x, y, z]
        springs = read_springs(CSV)

        self.set_camera_orientation(phi=70 * DEGREES, theta=-45 * DEGREES)

        row = ValueTracker(0) # which row of the csv is on screen

        def pos(mass):
            return positions[int(row.get_value()), mass]

        for i, j in springs:
            line = Line(pos(i), pos(j), stroke_width=1, stroke_opacity=0.4)
            line.add_updater(lambda l, i=i, j=j: l.put_start_and_end_on(pos(i), pos(j)))
            self.add(line)

        for mass in range(positions.shape[1]):
            dot = Dot3D(pos(mass), radius=0.15, color=COLORS[mass])
            dot.add_updater(lambda d, mass=mass: d.move_to(pos(mass)))
            self.add(dot)

        duration = (times[-1] - times[0]) / SPEED
        self.play(row.animate.set_value(len(data) - 1), run_time=duration, rate_func=linear)
