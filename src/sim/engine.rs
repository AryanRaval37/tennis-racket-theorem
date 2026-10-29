pub struct V(f32, f32, f32);

pub struct Mass {
    m: f32,
    x: V,
    v: V,
}

pub struct Spring {
    m1: Mass,
    m2: Mass,
    k: f32,
    len: f32,
}

pub struct RigidBody {
    k: f32, // spring const of springs making both rigid
    masses: Vec<Mass>,
    springs: Vec<Spring>,
    forces: Vec<fn(Vec<V>, Vec<V>, u32) -> Vec<V>>, // f(x, v, t) -> force
}

pub struct Engine {
    bodies: Vec<RigidBody>,
    t: u64,
}

impl RigidBody {
    pub fn new(rigid: bool, k: f32) -> Self {
        Self {
            rigid: rigid,
            k: k,
            masses: vec![],
            springs: vec![],
            forces: vec![],
            t: 0,
        }
    }

    pub fn add_mass(self, m: Mass) -> u32 {
        self.masses.push(m);
        return self.masses.len() - 1;
    }

    pub fn add_force(self, f: fn(Vec<V>, Vec<V>, u32) -> Vec<V>) {
        self.forces.push(f);
    }
}

fn main() {
    println!("It compiles!");
}
