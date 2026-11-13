// ! AI generated file to calculate the flip time for a given perturbation angle eps.
// I wrote this in python before but it was just too slow so I just asked AI to port it to rust.

// Flip time vs perturbation: spin about y (middle I) tilted by eps toward x, time how long until the first flip.
// "Flipped" = the body's y axis has turned perpendicular to L (L is fixed in space).
use physics_engine_rs::{Engine, RigidBody, Vector3};
use std::fs;
use std::io::Write;

fn main() {
    let (m, x, y, z) = (1.0, 1.0, 2.0, 3.0);
    // cargo run --release --example flip_time -- 0.001 100   to pick dt and spring stiffness k, default 1e-5 and 1e5
    let dt: f64 = std::env::args()
        .nth(1)
        .map_or(0.00001, |s| s.parse().unwrap());
    let k: f64 = std::env::args().nth(2).map_or(1e5, |s| s.parse().unwrap());
    let runs = concat!(env!("CARGO_MANIFEST_DIR"), "/../sim/runs");
    fs::create_dir_all(runs).unwrap();
    let mut out = fs::File::create(format!("{runs}/flip_time_rs_dt{dt}_k{k}.csv")).unwrap();
    writeln!(
        out,
        "# dt={dt} k={k} spin w = (eps, 1, 0), masses at x={x} y={y} z={z}\n# eps,t_flip"
    )
    .unwrap();

    for n in 1..=500 {
        let eps = 0.0000002 * n as f64; // 2e-7 .. 0.0001, evenly spaced for a linear plot
        let w = Vector3(eps, 1.0, 0.0);
        let mut b = RigidBody::new(true, k, 0.0);
        for r in [
            Vector3(x, 0.0, 0.0),
            Vector3(-x, 0.0, 0.0),
            Vector3(0.0, y, 0.0),
            Vector3(0.0, -y, 0.0),
            Vector3(0.0, 0.0, z),
            Vector3(0.0, 0.0, -z),
        ] {
            b.add_mass(m, r, w.cross(&r)); // v = w x r, the whole body spins together
        }

        let mut u = Engine::new();
        u.add_body(b);
        u.run(dt, 0.0); // builds the springs
        let ms = &u.bodies[0].masses;
        let l = ms
            .iter()
            .fold(Vector3::zero(), |l, p| l + p.x.cross(&p.v) * p.m); // fixed in space
        let y_axis = |u: &Engine| u.bodies[0].masses[2].x - u.bodies[0].masses[3].x;
        while y_axis(&u).dot(&l) > 0.0 && u.t < 200.0 {
            u.step(dt);
        }
        println!("eps={eps:.3e} t_flip={:.4}", u.t);
        writeln!(out, "{eps},{}", u.t).unwrap();
    }
}
