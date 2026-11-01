import sys
from pathlib import Path
import numpy as np
from manim import *
sys.path.append(str(Path(__file__).parent)) # manim doesn't add this folder, needed to import draw
from draw import read_springs, body_omega, COLORS, AXIS_COLORS, MARGIN, BODY_SHIFT

CSV = Path(__file__).parent / "runs" / "major_axis_rs.csv"
SPEED = 12 # simulated seconds per video second. csv is 60 rows/s, so at 60 fps every frame moves exactly SPEED rows
END = 600 # seconds of the run to show, it has basically settled by then
PLOT_EVERY = 30 # plot every 30th row, the curves don't need all 60000 points


class MajorAxis(ThreeDScene):
    def construct(self):
        data = np.loadtxt(CSV, delimiter=",")
        data = data[data[:, 0] <= END]
        times = data[:, 0]
        positions = data[:, 1:].reshape(len(data), -1, 3)
        springs = read_springs(CSV)
        Omega = body_omega(times, positions)
        velocities = np.gradient(positions, times, axis=0)
        energy = 0.5 * (velocities ** 2).sum(axis=(1, 2)) # all masses are 1 kg

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

        # --- the plots (2D, pinned to the screen on the right) ---
        def make_axes(y_range, y_label, height):
            axes = Axes(x_range=[0, times[-1], 100], y_range=y_range, x_length=5.2, y_length=height,
                        tips=False, axis_config={"include_numbers": True, "font_size": 16})
            labels = axes.get_axis_labels(x_label=MathTex(r"t\,(\mathrm{s})", font_size=24),
                                          y_label=MathTex(y_label, font_size=24))
            return axes, labels

        omega_axes, omega_labels = make_axes([-1, 1, 0.5], r"\Omega\,(\mathrm{rad/s})", 2.2)
        energy_axes, energy_labels = make_axes([0, 6, 2], r"E_k\,(\mathrm{J})", 1.4)

        names = [r"\Omega_1\;(x,\ \max I)", r"\Omega_2\;(y)", r"\Omega_3\;(z,\ \min I)"]
        legend = VGroup(*[
            VGroup(Line(ORIGIN, 0.4 * RIGHT, color=AXIS_COLORS[k], stroke_width=4),
                   MathTex(names[k], font_size=22)).arrange(RIGHT, buff=0.15)
            for k in range(3)
        ]).arrange(RIGHT, buff=0.35)
        title = Text("Damped body settles on its max-I axis", font_size=24)
        column = VGroup(title, legend, VGroup(omega_axes, omega_labels), VGroup(energy_axes, energy_labels))
        column.arrange(DOWN, buff=0.45).to_edge(RIGHT, buff=MARGIN + 0.6).set_y(0)
        self.add_fixed_in_frame_mobjects(title, legend, omega_axes, omega_labels, energy_axes, energy_labels)

        t_plot = times[::PLOT_EVERY]

        def live_curve(axes, ys, color):
            ys = ys[::PLOT_EVERY]
            curve = VMobject(color=color, stroke_width=2)
            # +2 so it always has at least 2 points
            curve.add_updater(lambda c: c.set_points_as_corners(
                axes.c2p(t_plot[:now() // PLOT_EVERY + 2], ys[:now() // PLOT_EVERY + 2]).T))
            self.add_fixed_in_frame_mobjects(curve)

        for k in range(3):
            live_curve(omega_axes, Omega[:, k], AXIS_COLORS[k])
        live_curve(energy_axes, energy, GREEN)

        # --- the clock ---
        clock_number = DecimalNumber(0, num_decimal_places=0, font_size=32)
        clock = VGroup(MathTex("t =", font_size=32), clock_number, MathTex(r"\mathrm{s}", font_size=32))
        clock.arrange(RIGHT, buff=0.15).to_corner(UL, buff=MARGIN)

        def update_clock(c):
            clock_number.set_value(times[now()])
            c.arrange(RIGHT, buff=0.15).to_corner(UL, buff=MARGIN)
            self.add_fixed_in_frame_mobjects(c)

        clock.add_updater(update_clock)
        self.add_fixed_in_frame_mobjects(clock)

        duration = (times[-1] - times[0]) / SPEED
        self.play(row.animate.set_value(len(data) - 1), run_time=duration, rate_func=linear)
        self.wait(2)
