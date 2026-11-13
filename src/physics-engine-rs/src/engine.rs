use crate::body::RigidBody;
use std::fs::{self, File};
use std::io::{self, BufWriter, Write};

pub struct Engine {
    pub bodies: Vec<RigidBody>,
    built: bool,
    pub t: f64,
}

impl Engine {
    pub fn new() -> Engine {
        Engine {
            bodies: Vec::new(),
            built: false,
            t: 0.0,
        }
    }

    pub fn add_body(&mut self, body: RigidBody) -> usize {
        self.bodies.push(body);
        self.bodies.len() - 1
    }

    pub fn step(&mut self, dt: f64) {
        self.t += dt;
        for b in &mut self.bodies {
            b.step(dt, self.t);
        }
    }

    pub fn run(&mut self, dt: f64, t_end: f64) {
        if !self.built {
            for b in &mut self.bodies {
                b.build();
            }
            self.built = true;
        }
        for b in &mut self.bodies {
            b.cache_force(self.t);
        }
        let steps = ((t_end - self.t) / dt).round_ties_even() as i64; // ties_even = python's round
        for _ in 0..steps {
            self.step(dt);
        }
    }

    // ! AI Generated functions export csv
    // I didn't want to deal with the csv format myself, exports the same thing as the python version of the engine.
    // Same format as engine.py: "# " metadata lines, then rows of t, x0, y0, z0, x1, ...
    // Masses of all bodies are numbered one after another
    pub fn export_csv(&mut self, name: &str, dt: f64, fps: f64, t_end: f64) -> io::Result<()> {
        let runs = concat!(env!("CARGO_MANIFEST_DIR"), "/../sim/runs"); // csv exports go here
        fs::create_dir_all(runs)?;
        let mut out = BufWriter::new(File::create(format!("{runs}/{name}"))?);
        let t0 = self.t;
        let frames = ((t_end - t0) * fps).round_ties_even() as i64 + 1;
        for frame in 0..frames {
            self.run(dt, t0 + frame as f64 / fps);
            if frame == 0 {
                self.write_header(&mut out, dt, fps)?; // after the first run so rigid springs exist
            }
            write!(out, "{}", self.t)?;
            for p in self.bodies.iter().flat_map(|b| &b.masses) {
                write!(out, ",{},{},{}", p.x.0, p.x.1, p.x.2)?;
            }
            writeln!(out)?;
        }
        Ok(())
    }

    fn write_header(&self, out: &mut impl Write, dt: f64, fps: f64) -> io::Result<()> {
        let (mut masses, mut springs, mut offset) = (Vec::new(), Vec::new(), 0);
        for b in &self.bodies {
            masses.extend(b.masses.iter().map(|p| p.m.to_string()));
            springs.extend(
                b.springs
                    .iter()
                    .map(|s| format!("{}-{}", s.i + offset, s.j + offset)),
            );
            offset += b.masses.len();
        }
        let mut cols = vec!["t".to_string()];
        for i in 0..offset {
            cols.extend(["x", "y", "z"].map(|c| format!("{c}{i}")));
        }
        writeln!(out, "# dt={dt} fps={fps}")?;
        writeln!(out, "# masses={}", masses.join(","))?;
        writeln!(out, "# springs={}", springs.join(","))?;
        writeln!(out, "# {}", cols.join(","))
    }
}
