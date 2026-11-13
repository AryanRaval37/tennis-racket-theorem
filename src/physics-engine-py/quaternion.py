import numpy as np
import matplotlib.pyplot as plt
import csv

# yes I found the real values
m, balance, swingweight, twistweight = 0.318, 0.3299, 0.0317, 0.00157
I1 = twistweight # about the handle
I2 = swingweight - m * (balance - 0.10)**2 # across the face, parallel axis theorem moves it to the centre of mass
I3 = I1 + I2 # face normal, perpendicular axis theorem (the racket is close to flat)

q = np.array([1.0, 0, 0, 0])

# initialising angular velocity
# The oddly specific numbers are because I wanted to find an optimal number where the racket when thrown up
# lands exact half a turn flipped
omega = np.array([-1.9646, 9.2592, 0.0], dtype=float)

dt = 0.001
t_max = 0.7 # again oddly specific
steps = round(t_max / dt)

time = np.zeros(steps + 1)
W = np.zeros((steps + 1, 3))
L = np.zeros((steps + 1, 3))

time[0] = 0.0
W[0] = omega
L[0] = np.array([I1, I2, I3]) * omega

Q = np.zeros((steps + 1, 4))
Q[0] = q

a, b, c = 1.5, 1.0, 0.5   # points of the body
body_points = np.array([
    [ a, 0, 0], [-a, 0, 0],
    [ 0, b, 0], [ 0,-b, 0],
    [ 0, 0, c], [ 0, 0,-c],
])

def quaternion_multiply(a, b):
    aw, ax, ay, az = a
    bw, bx, by, bz = b

    return np.array([
        aw*bw - ax*bx - ay*by - az*bz,
        aw*bx + ax*bw + ay*bz - az*by,
        aw*by - ax*bz + ay*bw + az*bx,
        aw*bz + ax*by - ay*bx + az*bw
    ])

def rotate(q,v):
    q_star = np.array([q[0],-q[1],-q[2],-q[3]])
    v_q = np.array([0.0,v[0],v[1],v[2]])
    v1 = quaternion_multiply(q, v_q)
    r = quaternion_multiply(v1, q_star)
    return r[1:]

def dq(q,w):
    w_q = [0,w[0],w[1],w[2]]
    return 1/2* quaternion_multiply(q,w_q)

def euler_equations(w):  # euler equations
    w1, w2, w3 = w

    dw1 = ((I2 - I3) / I1) * w2 * w3
    dw2 = ((I3 - I1) / I2) * w3 * w1
    dw3 = ((I1 - I2) / I3) * w1 * w2

    return np.array([dw1, dw2, dw3])

def rk4(w, q, dt):
    k1 = euler_equations(w)
    l1 = dq(q, w)

    w2 = w + 0.5*dt*k1
    k2 = euler_equations(w2)
    l2 = dq(q + 0.5*dt*l1, w2)

    w3 = w + 0.5*dt*k2
    k3 = euler_equations(w3)
    l3 = dq(q + 0.5*dt*l2, w3)

    w4 = w + dt*k3
    k4 = euler_equations(w4)
    l4 = dq(q + dt*l3, w4)

    w_new = w + (dt/6.0)*(k1 + 2*k2 + 2*k3 + k4)
    q_new = q + (dt/6.0)*(l1 + 2*l2 + 2*l3 + l4)
    q_new /= np.linalg.norm(q_new)   # normalize every step because rk4 might not preserve |Q| =1
    return w_new, q_new

I = np.array([I1, I2, I3])
w= omega
for i in range(steps):
    w,q = rk4(w, q, dt)
    time[i+1]= time[i]+dt
    W[i + 1] = w
    L[i + 1] = I * w
    Q[i + 1] = q


# ! AI generated function to export csv from the run
fps = 500 # the video plays it in slow motion
save_every = int(round(1 / (fps * dt)))   # 333 for dt = 1e-4 → 30 rows per simulated second

rows = []
for i in range(0, steps + 1, save_every):
    pts = np.array([rotate(Q[i], v) for v in body_points])   # shape (6, 3)
    rows.append([time[i], *Q[i], *pts.ravel()])

rows = np.array(rows)

header = ["t", "qw", "qx", "qy", "qz"] + [
    f"p{j}{ax}" for j in range(1, 7) for ax in "xyz"
]

np.savetxt("dzhanibekov.csv", rows, delimiter=",",
           header=",".join(header), comments="", fmt="%.8f")

print(f"Saved {rows.shape[0]} frames, {rows.shape[1]} columns")
