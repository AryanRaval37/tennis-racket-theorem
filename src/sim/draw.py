# ! Fully AI generated file to render the amazing video
# Takes in the exported csv from the engine and uses that data to make the manim video
# manim is an amazing library developed by 3blue1brown for videos on his youtube channel.
# I didn't think it was worth looking up the docs of the library and writing this all myself, its just to draw out the videos, nothing to do with computational phyics.
# Therefore I would say this counts as ethical use of AI.

from pathlib import Path
import numpy as np
from manim import *

CSV = Path(__file__).parent / "runs" / "six_masses_py.csv"
SPEED = 4 # simulated seconds per video second
COLORS = [BLUE, BLUE, YELLOW, YELLOW, RED, RED] # mass colours: x pair, y pair, z pair
AXIS_COLORS = [BLUE, YELLOW, RED] # Omega_1, Omega_2, Omega_3 use the same colours as their axis
MARGIN = 0.6 # space between things and the screen edge
# Centres the body in the left half of the screen. With the camera at theta = -45 deg,
# "screen left" is the world direction -(x + y); 5.1 world units * zoom 0.7 = 3.55, a quarter of the screen width
BODY_SHIFT = -5.1 * np.array([1, 1, 0]) / np.sqrt(2)


def read_springs(path):
    # finds the line "# springs=0-1,0-2,..." and turns it into [(0, 1), (0, 2), ...]
    for line in open(path):
        if line.startswith("# springs="):
            pairs = line.strip().removeprefix("# springs=").split(",")
            return [tuple(int(n) for n in pair.split("-")) for pair in pairs]


def body_axes(positions):
    # Body axes from the three mass pairs (0-1 on x, 2-3 on y, 4-5 on z), as unit vectors
    e = np.stack([positions[:, 0] - positions[:, 1],
                  positions[:, 2] - positions[:, 3],
                  positions[:, 4] - positions[:, 5]], axis=1) # e[row, k] = axis k
    return e / np.linalg.norm(e, axis=2, keepdims=True)


def body_omega(times, positions):
    e = body_axes(positions)
    de = np.gradient(e, times, axis=0) # how fast each axis is moving
    # Each axis moves as de_k = omega x e_k. Summing e_k x de_k over the 3 axes gives 2 omega
    omega = 0.5 * np.cross(e, de).sum(axis=1)
    return (e * omega[:, None, :]).sum(axis=2) # Omega[row, k] = omega . e_k (body frame)


class OmegaPlot(ThreeDScene):
    def construct(self):
        data = np.loadtxt(CSV, delimiter=",")
        times = data[:, 0]
        positions = data[:, 1:].reshape(len(data), -1, 3)
        springs = read_springs(CSV)
        Omega = body_omega(times, positions)

        row = ValueTracker(0)

        def now():
            return int(row.get_value())

        def pos(mass):
            return positions[now(), mass] + BODY_SHIFT

        # --- the body (3D, on the left) ---
        self.set_camera_orientation(phi=70 * DEGREES, theta=-45 * DEGREES, zoom=0.7)
        for i, j in springs:
            line = Line(pos(i), pos(j), stroke_width=1, stroke_opacity=0.4)
            line.add_updater(lambda l, i=i, j=j: l.put_start_and_end_on(pos(i), pos(j)))
            self.add(line)
        # 8 faces of the diamond (octahedron): each face takes one mass from the x, y and z pairs
        for a in (0, 1):
            for b in (2, 3):
                for c in (4, 5):
                    face = Polygon(pos(a), pos(b), pos(c), stroke_width=0, fill_color=GREY_B, fill_opacity=0.12)
                    face.add_updater(lambda f, a=a, b=b, c=c: f.set_points_as_corners([pos(a), pos(b), pos(c), pos(a)]))
                    self.add(face)
        for mass in range(positions.shape[1]):
            dot = Dot3D(pos(mass), radius=0.15, color=COLORS[mass])
            dot.add_updater(lambda d, mass=mass: d.move_to(pos(mass)))
            self.add(dot)

        # --- the plot (2D, pinned to the screen on the right) ---
        axes = Axes(x_range=[0, times[-1], 20], y_range=[-1, 1, 0.5], x_length=5.2, y_length=3,
                    tips=False, axis_config={"include_numbers": True, "font_size": 16})
        axes.to_edge(RIGHT, buff=MARGIN + 0.6) # extra room for the "t (s)" label
        axis_labels = axes.get_axis_labels(x_label=MathTex(r"t\,(\mathrm{s})", font_size=24),
                                           y_label=MathTex(r"\Omega\,(\mathrm{rad/s})", font_size=24))

        # legend: a coloured line sample next to each label, all in one row
        names = [r"\Omega_1\;(x)", r"\Omega_2\;(y)", r"\Omega_3\;(z)"]
        legend = VGroup(*[
            VGroup(Line(ORIGIN, 0.4 * RIGHT, color=AXIS_COLORS[k], stroke_width=4),
                   MathTex(names[k], font_size=24)).arrange(RIGHT, buff=0.15)
            for k in range(3)
        ]).arrange(RIGHT, buff=0.5)
        legend.next_to(axes, UP, buff=0.6)
        title = Text("Body-frame angular velocity", font_size=24).next_to(legend, UP, buff=0.3)
        VGroup(title, legend, axes, axis_labels).set_y(0) # centre the whole plot block vertically
        self.add_fixed_in_frame_mobjects(axes, axis_labels, legend, title)

        for k in range(3):
            curve = VMobject(color=AXIS_COLORS[k], stroke_width=2)
            # redraw the curve from the first row up to now; +2 so it always has at least 2 points
            curve.add_updater(lambda c, k=k: c.set_points_as_corners(axes.c2p(times[:now() + 2], Omega[:now() + 2, k]).T))
            self.add_fixed_in_frame_mobjects(curve)

        # --- the clock: "t = " and "s" never change, only the number in between does ---
        clock_number = DecimalNumber(0, num_decimal_places=1, font_size=32)
        clock = VGroup(MathTex("t =", font_size=32), clock_number, MathTex(r"\mathrm{s}", font_size=32))
        clock.arrange(RIGHT, buff=0.15).to_corner(UL, buff=MARGIN)

        def update_clock(c):
            clock_number.set_value(times[now()])
            c.arrange(RIGHT, buff=0.15).to_corner(UL, buff=MARGIN) # re-space, the number gets wider as it grows
            # set_value() rebuilds the digits as new objects, which a 3D scene doesn't keep pinned, so pin again
            self.add_fixed_in_frame_mobjects(c)

        clock.add_updater(update_clock)
        self.add_fixed_in_frame_mobjects(clock)

        duration = (times[-1] - times[0]) / SPEED
        self.play(row.animate.set_value(len(data) - 1), run_time=duration, rate_func=linear)
        self.wait(2) # hold the finished plot
