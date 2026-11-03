use serde::{Deserialize, Serialize};

/// Native 72-byte paint material. No seed/default coefficients are invented.
/// Typed fields are authoritative; `raw_be_bytes` is refreshed on customization.
#[derive(Clone, Debug, Serialize, Deserialize, PartialEq)]
pub struct NativePaintRecord {
    pub native_type: u32,
    pub base_rgb: [f32; 3],
    pub fleck_rgb: [f32; 3],
    pub secondary_rgb: [f32; 3],
    pub two_tone_exp: f32,
    pub min_reflect: f32,
    pub max_reflect: f32,
    pub flakie: f32,
    pub fleck_power: f32,
    pub fleck_locality: f32,
    pub try_thin_film: f32,
    pub film_thickness: f32,
    pub raw_be_bytes: Vec<u8>,
}
impl NativePaintRecord {
    pub fn from_be_bytes(bytes: &[u8]) -> Result<Self, String> {
        if bytes.len() != 72 {
            return Err("Native paint record must contain 72 bytes".into());
        }
        let word = |offset| u32::from_be_bytes(bytes[offset..offset + 4].try_into().unwrap());
        let float = |offset| f32::from_bits(word(offset));
        let rgb = |offset| [float(offset), float(offset + 4), float(offset + 8)];
        Ok(Self {
            native_type: word(0),
            base_rgb: rgb(4),
            fleck_rgb: rgb(16),
            secondary_rgb: rgb(28),
            two_tone_exp: float(40),
            min_reflect: float(44),
            max_reflect: float(48),
            flakie: float(52),
            fleck_power: float(56),
            fleck_locality: float(60),
            try_thin_film: float(64),
            film_thickness: float(68),
            raw_be_bytes: bytes.to_vec(),
        })
    }
    pub fn to_be_bytes(&self) -> [u8; 72] {
        let mut bytes = [0; 72];
        bytes[..4].copy_from_slice(&self.native_type.to_be_bytes());
        let floats = self
            .base_rgb
            .into_iter()
            .chain(self.fleck_rgb)
            .chain(self.secondary_rgb)
            .chain([
                self.two_tone_exp,
                self.min_reflect,
                self.max_reflect,
                self.flakie,
                self.fleck_power,
                self.fleck_locality,
                self.try_thin_film,
                self.film_thickness,
            ]);
        for (index, value) in floats.enumerate() {
            bytes[4 + index * 4..8 + index * 4].copy_from_slice(&value.to_be_bytes());
        }
        bytes
    }
    pub fn finish_id(&self) -> Option<&'static str> {
        ["gloss", "metallic", "flake", "pearl", "matt", "thinfilm"]
            .get(self.native_type as usize)
            .copied()
    }
    pub fn price(&self) -> Option<u32> {
        [3000, 5000, 12000, 12000, 7500, 20000]
            .get(self.native_type as usize)
            .copied()
    }
}

pub(crate) fn sync_customization(custom: &mut crate::Customization) {
    if let Some(record) = custom.native_paint.as_mut() {
        record.raw_be_bytes = record.to_be_bytes().to_vec();
        custom.paint[..3].copy_from_slice(&record.base_rgb);
        if let Some(finish) = record.finish_id() {
            custom.finish = finish.into();
        }
    }
}
