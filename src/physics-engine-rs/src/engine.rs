use crate::body::RigidBody;

pub struct Engine {
    bodies: Vec<RigidBody>,
    t: f64,
}
