use crate::body::Mass;
use crate::math::Vector3;

pub struct Spring {
    pub i: usize, // index of the first mass in the masses vector
    pub j: usize,
    pub k: f64,
    pub c: f64, // damping: resists the masses moving apart or together, loses energy but keeps L
    pub len: f64, // rest length
}

impl Spring {
    // again same thing here -> read comment in force.rs for changing how forces work
    // adds this spring's force on masses i and j into f
    pub fn apply(&self, masses: &[Mass], f: &mut [Vector3]) {
        let d = masses[self.j].x - masses[self.i].x; // points from i to j
        let r = d.mag();
        let dv = masses[self.j].v - masses[self.i].v;
        let fs = d * (self.k * (r - self.len) + self.c * dv.dot(&d) / r) / r; // stretched or moving apart -> pulls i toward j
        f[self.i] += fs;
        f[self.j] -= fs;
    }
}
