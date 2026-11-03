use serde::{Deserialize, Serialize};
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct SpectatorBet {
    pub racer: usize,
    pub stake: u32,
    pub odds: f32,
    pub payout: i64,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub enum BetKind {
    Cash,
    PinkSlip,
}
#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub enum BetOfferStatus {
    Offered,
    Countered,
    Accepted,
    Declined,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct DriverBetOffer {
    pub racer: usize,
    pub kind: BetKind,
    pub amount: u32,
    pub counter_amount: u32,
    pub status: BetOfferStatus,
    pub reason: String,
}
