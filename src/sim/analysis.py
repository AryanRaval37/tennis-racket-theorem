# Shared by the plot_*.py scripts: reading engine runs, the octahedron's moments of inertia, Euler's equations, figure style
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from draw import body_axes, body_omega

RUNS = Path(__file__).parent / "runs"
OUT = Path(__file__).parents[2] / "report" / "Images"
I = np.array([26.0, 20.0, 10.0]) # masses of 1 kg at x = 1, y = 2, z = 3: x = max I, y = middle I, z = min I


def euler(t, w):
    return [(I[1] - I[2]) * w[1] * w[2] / I[0], (I[2] - I[0]) * w[2] * w[0] / I[1], (I[0] - I[1]) * w[0] * w[1] / I[2]]


def load_run(name):
    # positions from an engine CSV; velocities by finite differences, every mass 1 kg
    data = np.loadtxt(RUNS / name, delimiter=",")
    t, pos = data[:, 0], data[:, 1:].reshape(len(data), -1, 3)
    r = pos - pos.mean(axis=1, keepdims=True)
    v = np.gradient(r, t, axis=0, edge_order=2)
    return t, pos, r, v, np.cross(r, v).sum(axis=1)


def save(fig, name):
    fig.savefig(OUT / f"{name}.pdf")
    fig.savefig(OUT / f"{name}.png", dpi=300)


plt.rcParams.update({"font.size": 9, "mathtext.fontset": "cm", "font.family": "serif", "font.serif": ["cmr10"], "axes.formatter.use_mathtext": True})
