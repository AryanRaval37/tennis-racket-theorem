use crate::body::Mass;
use crate::math::Vector3;

// f(masses, t) -> force on every mass
// You give it a function that takes masses and time and returns a vector of forces on each mass
// little annoying that I have to used this box dyn thing because its not really a function pointer here like pure C, its a reference.
pub type Force = Box<dyn Fn(&[Mass], f64) -> Vec<Vector3>>;

// This is not the cleanest way to do it, I would have liked to use a trait for a force and let a force be a struct.
// You should give it body state (more general than list of masses) and it need to implment a function that returns force
// vec of structs better than storing vec of function pointers.
// todo : Update this later
