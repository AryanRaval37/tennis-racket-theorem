use physics_engine_rs::{Engine, RigidBody, Vector3};

fn main() {
    let (m, x, y, z, v) = (1.0, 1.0, 2.0, 3.0, 1.0);
    let mut b = RigidBody::new(true, 1e5, 0.0);
    b.add_mass(m, Vector3(x, 0.0, 0.0), Vector3(0.0, 0.0, -v));
    b.add_mass(m, Vector3(-x, 0.0, 0.0), Vector3(0.0, 0.0, v));
    b.add_mass(m, Vector3(0.0, y, 0.0), Vector3(0.0, 0.0, 0.01));
    b.add_mass(m, Vector3(0.0, -y, 0.0), Vector3(0.0, 0.0, -0.01));
    b.add_mass(m, Vector3(0.0, 0.0, z), Vector3(z * v, 0.0, 0.0));
    b.add_mass(m, Vector3(0.0, 0.0, -z), Vector3(-z * v, 0.0, 0.0));

    let mut u = Engine::new();
    u.add_body(b);
    u.export_csv("six_masses_rs.csv", 0.00001, 60.0, 100.0)
        .unwrap();
}
