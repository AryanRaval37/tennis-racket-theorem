use super::mass::Mass;
use crate::math::Vector3;
use crate::physics::{Force, Spring};

pub struct RigidBody {
    rigid: bool, // connects every pair of masses with a spring of stiffness k and damping c when built
    k: f64,
    c: f64,
    pub masses: Vec<Mass>,
    pub springs: Vec<Spring>,
    forces: Vec<Force>,
    // forces cached is just the previous dt's forces (helpful for storing for verlet otherwise you'd have to recompute)
    force_cached: Vec<Vector3>,
}

impl RigidBody {
    pub fn new(rigid: bool, k: f64, c: f64) -> RigidBody {
        RigidBody {
            rigid,
            k,
            c,
            masses: Vec::new(),
            springs: Vec::new(),
            forces: Vec::new(),
            force_cached: Vec::new(),
        }
    }

    pub fn add_mass(&mut self, m: f64, x: Vector3, v: Vector3) -> usize {
        self.masses.push(Mass { m, x, v });
        self.masses.len() - 1
    }

    // unstretched at the current positions
    pub fn add_spring(&mut self, i: usize, j: usize, k: f64, c: f64) {
        let len = (self.masses[j].x - self.masses[i].x).mag();
        self.springs.push(Spring { i, j, k, c, len });
    }

    pub fn add_force(&mut self, f: impl Fn(&[Mass], f64) -> Vec<Vector3> + 'static) {
        self.forces.push(Box::new(f));
    }

    // adds springs between all unlinked pairs of masses
    pub fn build(&mut self) {
        if self.rigid {
            for i in 0..self.masses.len() {
                for j in i + 1..self.masses.len() {
                    let linked = self
                        .springs
                        .iter()
                        .any(|s| (s.i, s.j) == (i, j) || (s.i, s.j) == (j, i));
                    if !linked {
                        self.add_spring(i, j, self.k, self.c);
                    }
                }
            }
        }
    }

    pub fn total_force(&self, t: f64) -> Vec<Vector3> {
        let mut total = vec![Vector3::zero(); self.masses.len()];
        for f in &self.forces {
            for (a, b) in total.iter_mut().zip(f(&self.masses, t)) {
                *a += b;
            }
        }
        for s in &self.springs {
            s.apply(&self.masses, &mut total);
        }
        total
    }

    pub fn cache_force(&mut self, t: f64) {
        self.force_cached = self.total_force(t);
    }

    // Verlet integration, t is the time at the end of the step
    pub fn step(&mut self, dt: f64, t: f64) {
        for (p, f) in self.masses.iter_mut().zip(&self.force_cached) {
            p.v += *f * (0.5 * dt) / p.m;
            p.x += p.v * dt;
        }
        self.cache_force(t);
        for (p, f) in self.masses.iter_mut().zip(&self.force_cached) {
            p.v += *f * (0.5 * dt) / p.m;
        }
    }
}
