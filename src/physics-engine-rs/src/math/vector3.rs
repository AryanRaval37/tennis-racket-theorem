pub struct Vector3(f32, f32, f32);

impl Vector3 {
    pub fn zero() -> Vector3 {
        Vector3(0.0, 0.0, 0.0)
    }

    pub fn mag(&self) -> f32 {
        (self.0 * self.0 + self.1 * self.1 + self.2 * self.2).sqrt()
    }

    pub fn dot(&self, other: &Vector3) -> f32 {
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
