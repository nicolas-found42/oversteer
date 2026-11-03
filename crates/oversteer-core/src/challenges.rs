use serde::{Deserialize, Serialize};

#[derive(Clone, Copy, Debug, Default, PartialEq, Eq, Serialize, Deserialize)]
pub enum SpeedChallengeState {
    #[default]
    Pending,
    Armed,
    FailedReach,
    FailedMaintain,
}
impl SpeedChallengeState {
    /// Native82131888, preserving the cached armed branch and strict comparisons.
    pub fn update(self, speed: f32, target: f32, elapsed: f32) -> Self {
        match self {
            Self::Pending => {
                if elapsed > 10. {
                    Self::FailedReach
                } else if speed > target {
                    Self::Armed
                } else {
                    Self::Pending
                }
            }
            Self::Armed if speed < target => Self::FailedMaintain,
            _ => self,
        }
    }
    pub fn failed(self) -> bool {
        matches!(self, Self::FailedReach | Self::FailedMaintain)
    }
}
