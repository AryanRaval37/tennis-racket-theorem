# ! Fully AI generated file to render the racket video
# Same body motion as quaternion.py (Euler's equations with a real racket's I), drawn as a tennis racket.
# A flat racket has I_handle < I_across < I_normal, so body axes map as
# x (min I) -> along the handle, y (middle I) -> across the face, z (max I) -> face normal.
# Make the csv first: cd src/sim/runs && uv run python ../../physics-engine-py/quaternion.py
import sys
from pathlib import Path
import numpy as np
from manim import *
sys.path.append(str(Path(__file__).parent)) # manim doesn't add this folder, needed to import draw
from draw import body_axes, body_omega, AXIS_COLORS, MARGIN, BODY_SHIFT

CSV = Path(__file__).parent / "runs" / "dzhanibekov.csv"
SPEED = 0.2 # simulated seconds per video second, slow motion: the real toss is under a second
G = 9.81 # m/s^2
HAND_Z = -3.2 # height of the centre of mass when thrown and caught
WORLD_PER_M = 6 # the racket is built in metres, then blown up by this for the screen (the toss height too)

# Babolat Pure Drive 2025, the same racket quaternion.py takes its I from. Body x = 0 is the balance point (centre of mass)
LENGTH, BALANCE = 0.6858, 0.3299 # 27 in long, balanced 32.99 cm from the butt
BED_A, BED_B = 0.163, 0.126 # string bed half length / half width: pi a b = 645 cm^2 (100 in^2 head), a 1.3 : 1 oval
FRAME_W, FRAME_D = 0.013, 0.025 # frame tube width in the face plane, and depth along the face normal (23-26 mm beam)
HEAD_X = LENGTH - BALANCE - BED_A - FRAME_W # centre of the head
GRIP_END, THROAT_X = 0.19 - BALANCE, 0.24 - BALANCE # grip covers the first 19 cm, throat arms split 24 cm from the butt
GRIP_R = 0.018 # octagon corner radius for a 4 3/8 in (11.1 cm round) grip
# Front of the racket (body +z) and back (-z). Thrown front up, caught back up.
# Spinning end over end it shows the camera its front, then its back, every half turn, like a real one would
FRONT_COLOR, BACK_COLOR, FRAME_COLOR = XKCD.PURPLE, XKCD.OLIVEGREEN, GREY_B


def tube(curve, width, depth, u_res):
    # Frame tube along a curve in the face plane, curve(s) for s in [0, 1]
    def point(s, v):
        t = curve(s + 1e-4) - curve(s - 1e-4)
        n = np.array([t[1], -t[0], 0]) / np.linalg.norm(t) # sideways, in the face plane
        return curve(s) + width / 2 * np.cos(v) * n + depth / 2 * np.sin(v) * OUT
    return Surface(point, u_range=[0, 1], v_range=[0, TAU], resolution=(u_res, 8), checkerboard_colors=False,
                   fill_opacity=1, stroke_width=0)


def make_racket():
    A, B = BED_A + FRAME_W / 2, BED_B + FRAME_W / 2 # centre line of the hoop

    def hoop_point(th):
        return np.array([HEAD_X + A * np.cos(th), B * np.sin(th), 0])

    def arm(sign): # throat arm from the shaft to the hoop, meeting it along the hoop's direction so it blends in
        th = PI - sign * 0.8
        along = sign * np.array([A * np.sin(th), -B * np.cos(th), 0]) # along the hoop, towards the tip
        start, end = np.array([THROAT_X, 0, 0]), hoop_point(th)
        curve = bezier([start, start + 0.05 * np.array([1, 0.3 * sign, 0]), end - 0.05 * along / np.linalg.norm(along), end])
        return tube(curve, FRAME_W, 0.023, 12)

    hoop = tube(lambda s: hoop_point(TAU * s), FRAME_W, FRAME_D, 64)
    shaft = Cylinder(radius=0.011, height=THROAT_X - GRIP_END, direction=RIGHT, resolution=(1, 8),
                     checkerboard_colors=False, fill_opacity=1, stroke_width=0).move_to([(GRIP_END + THROAT_X) / 2, 0, 0])
    grip = Cylinder(radius=GRIP_R, height=GRIP_END + BALANCE, direction=RIGHT, resolution=(1, 8),
                    checkerboard_colors=False, fill_opacity=1, stroke_width=0).move_to([(GRIP_END - BALANCE) / 2, 0, 0])
    solid = VGroup(hoop, arm(1), arm(-1), shaft, grip)
    for f in solid.family_members_with_points(): # paint the front and back halves of the frame
        z = f.points[:, 2].mean()
        f.set_fill(FRONT_COLOR if z > 1e-6 else BACK_COLOR if z < -1e-6 else FRAME_COLOR)

    # String bed: a see-through tint and strings for each side. Only the side facing the camera is shown (set every frame)
    bed = VGroup()
    for color in (FRONT_COLOR, BACK_COLOR):
        fill = Ellipse(2 * BED_A, 2 * BED_B, stroke_width=0, fill_color=color, fill_opacity=0.35).shift(HEAD_X * RIGHT)
        strings = VGroup()
        for y in np.linspace(-BED_B, BED_B, 18)[1:-1]: # 16 mains, parallel to the handle
            half = BED_A * np.sqrt(1 - (y / BED_B) ** 2)
            strings.add(Line([HEAD_X - half, y, 0], [HEAD_X + half, y, 0]))
        for x in np.linspace(-BED_A, BED_A, 21)[1:-1]: # 19 crosses
            half = BED_B * np.sqrt(1 - (x / BED_A) ** 2)
            strings.add(Line([HEAD_X + x, -half, 0], [HEAD_X + x, half, 0]))
        bed.add(VGroup(fill, strings.set_stroke(color, width=1.2)))
    for m in bed.family_members_with_points():
        m.shade_in_3d = m.unshaded = True # only shade_in_3d things get depth sorted, everything else is drawn on top
        m.z_index_group = bed # sort the bed as one sheet, tint under strings, not piece by piece
    return VGroup(bed, solid)


class Racket(ThreeDScene):
    def construct(self):
        data = np.loadtxt(CSV, delimiter=",", skiprows=1)
        times = data[:, 0]
        positions = data[:, 5:].reshape(len(data), -1, 3) # the 6 marker points, one pair on each body axis
        e = body_axes(positions)
        Omega = body_omega(times, positions)

        # The run is one toss: it leaves the hand at t = 0 and is back at the end.
        # Gravity puts no torque about the centre of mass, so it only moves the centre, along a parabola
        toss = times[-1]
        centre = BODY_SHIFT + (HAND_Z + WORLD_PER_M * 0.5 * G * times * (toss - times))[:, None] * OUT

        row = ValueTracker(0)

        def now():
            return int(row.get_value())

        # --- the racket (3D, on the left) ---
        self.set_camera_orientation(phi=60 * DEGREES, theta=-45 * DEGREES, zoom=0.7)
        # shade_in_3d also turns on lighting, which washes the string bed out when it faces the light: skip it there
        shade = self.camera.modified_rgbas
        self.camera.modified_rgbas = lambda m, rgbas: rgbas if getattr(m, "unshaded", False) else shade(m, rgbas)
        # where the camera sits. generate_: get_rotation_matrix() is only refreshed when a frame is drawn, it is still level here
        eye = self.camera.get_focal_distance() * self.camera.generate_rotation_matrix()[2]
        racket = make_racket().scale(WORLD_PER_M, about_point=ORIGIN)
        front, back = racket[0]
        parts = racket.family_members_with_points()
        body_points = [p.points.copy() for p in parts]

        def orient(m):
            for part, p in zip(parts, body_points):
                part.points = p @ e[now()] + centre[now()] # e[row] holds the body axes as rows, so this is R @ p
            # Which side of the bed you see, along the real line of sight. The camera's own depth sort uses its centre
            # line, which is ~15 degrees off for the racket at the side of the screen, so it picks wrong near edge on
            facing = e[now(), 2] @ (eye - centre[now()]) > 0
            for side, shown in ((front, facing), (back, not facing)):
                side[0].set_fill(opacity=0.35 * shown)
                side[1].set_stroke(opacity=float(shown))

        racket.add_updater(orient)
        self.add(racket)

        # --- the plot (2D, pinned to the screen on the right) ---
        axes = Axes(x_range=[0, toss, 0.1], y_range=[-10, 10, 5], x_length=5.2, y_length=3,
                    tips=False, axis_config={"include_numbers": True, "font_size": 16})
        axes.to_edge(RIGHT, buff=MARGIN + 0.6) # extra room for the "t (s)" label
        axis_labels = axes.get_axis_labels(x_label=MathTex(r"t\,(\mathrm{s})", font_size=24),
                                           y_label=MathTex(r"\Omega\,(\mathrm{rad/s})", font_size=24))

        names = [r"\Omega_1\;(\text{handle},\ \min I)", r"\Omega_2\;(\text{across face},\ \text{middle } I)",
                 r"\Omega_3\;(\text{face normal},\ \max I)"]
        legend = VGroup(*[
            VGroup(Line(ORIGIN, 0.4 * RIGHT, color=AXIS_COLORS[k], stroke_width=4),
                   MathTex(names[k], font_size=22)).arrange(RIGHT, buff=0.15)
            for k in range(3)
        ]).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        legend.next_to(axes, UP, buff=0.6)
        title = Text("One toss about the middle axis: one flip", font_size=24).next_to(legend, UP, buff=0.3)
        VGroup(title, legend, axes, axis_labels).set_y(0) # centre the whole plot block vertically
        self.add_fixed_in_frame_mobjects(axes, axis_labels, legend, title)

        for k in range(3):
            curve = VMobject(color=AXIS_COLORS[k], stroke_width=2)
            # redraw the curve from the first row up to now; +2 so it always has at least 2 points
            curve.add_updater(lambda c, k=k: c.set_points_as_corners(axes.c2p(times[:now() + 2], Omega[:now() + 2, k]).T))
            self.add_fixed_in_frame_mobjects(curve)

        # --- the clock ---
        clock_number = DecimalNumber(0, num_decimal_places=2, font_size=32)
        clock = VGroup(MathTex("t =", font_size=32), clock_number, MathTex(r"\mathrm{s}", font_size=32))
        clock.arrange(RIGHT, buff=0.15).to_corner(UL, buff=MARGIN)

        def update_clock(c):
            clock_number.set_value(times[now()])
            c.arrange(RIGHT, buff=0.15).to_corner(UL, buff=MARGIN)
            self.add_fixed_in_frame_mobjects(c) # set_value() makes new digit objects, pin them again

        clock.add_updater(update_clock)
        self.add_fixed_in_frame_mobjects(clock)

        duration = (times[-1] - times[0]) / SPEED
        self.play(row.animate.set_value(len(times) - 1), run_time=duration, rate_func=linear)
        self.wait(2)
