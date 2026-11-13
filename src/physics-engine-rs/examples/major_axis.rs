use physics_engine_rs::{Engine, RigidBody, Vector3};

fn main() {
    let (m, x, y, z) = (1.0, 1.0, 2.0, 3.0);
    let (k, c) = (1.0, 0.7); // soft springs, damping c is what lets it lose energy and settle
    let w = Vector3(0.1, 0.0, 1.0); // spin about z (min I), slightly tilted toward x (max I)

    let mut b = RigidBody::new(true, k, c);
    for r in [
        Vector3(x, 0.0, 0.0), Vector3(-x, 0.0, 0.0),
        Vector3(0.0, y, 0.0), Vector3(0.0, -y, 0.0),
        Vector3(0.0, 0.0, z), Vector3(0.0, 0.0, -z),
    ] {
        b.add_mass(m, r, w.cross(&r)); // v = w x r, the whole body spins together
    }

    let mut u = Engine::new();
    u.add_body(b);
    u.export_csv("major_axis_rs.csv", 0.005, 60.0, 1000.0).unwrap();
}
