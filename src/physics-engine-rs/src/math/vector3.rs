// this is basically like the python equivalent of defining operator overloading
use std::ops::{Add, AddAssign, Div, Mul, Sub, SubAssign};

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Vector3(pub f64, pub f64, pub f64);

impl Vector3 {
    pub fn zero() -> Vector3 {
        Vector3(0.0, 0.0, 0.0)
    }

    pub fn mag(&self) -> f64 {
        (self.0 * self.0 + self.1 * self.1 + self.2 * self.2).sqrt()
    }

    pub fn dot(&self, other: &Vector3) -> f64 {
        self.0 * other.0 + self.1 * other.1 + self.2 * other.2
    }

    pub fn cross(&self, other: &Vector3) -> Vector3 {
        Vector3(
            self.1 * other.2 - self.2 * other.1,
            self.2 * other.0 - self.0 * other.2,
            self.0 * other.1 - self.1 * other.0,
        )
    }

    pub fn normalize(&mut self) {
        let mag = self.mag();
        if mag != 0.0 {
            self.0 /= mag;
            self.1 /= mag;
            self.2 /= mag;
        }
    }
}

impl Add for Vector3 {
    type Output = Vector3;
    fn add(self, o: Vector3) -> Vector3 {
        Vector3(self.0 + o.0, self.1 + o.1, self.2 + o.2)
    }
}

impl Sub for Vector3 {
    type Output = Vector3;
    fn sub(self, o: Vector3) -> Vector3 {
        Vector3(self.0 - o.0, self.1 - o.1, self.2 - o.2)
    }
}

impl Mul<f64> for Vector3 {
    type Output = Vector3;
    fn mul(self, s: f64) -> Vector3 {
        Vector3(self.0 * s, self.1 * s, self.2 * s)
    }
}

impl Div<f64> for Vector3 {
    type Output = Vector3;
    fn div(self, s: f64) -> Vector3 {
        Vector3(self.0 / s, self.1 / s, self.2 / s)
    }
}

impl AddAssign for Vector3 {
    fn add_assign(&mut self, o: Vector3) {
        *self = *self + o;
    }
}

impl SubAssign for Vector3 {
    fn sub_assign(&mut self, o: Vector3) {
        *self = *self - o;
    }
}
