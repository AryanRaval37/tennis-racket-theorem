use super::mass::Mass;
use crate::math::Vector3;
use crate::physics::Spring;

pub struct RigidBody {
    k: f32, // spring const of springs making both rigid
    masses: Vec<Mass>,
    springs: Vec<Spring>,
}
