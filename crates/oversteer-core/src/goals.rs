use serde::{Deserialize, Serialize};
use serde_json::Value;

#[derive(Clone, Debug, Default, Serialize, Deserialize)]
#[serde(default)]
pub struct GoalDefinition {
    pub id: String,
    pub description: String,
    pub kind: String,
    pub args: Vec<Value>,
    pub discipline: String,
    pub subtype: String,
    pub location: String,
    pub route: String,
    pub contest_type: String,
    pub car_class: String,
    pub prototype: bool,
    pub extreme_nos: bool,
    pub team_race: bool,
    pub endurance: bool,
    pub prize_type: String,
    pub qualifier: bool,
    pub vis_unlock: bool,
    pub prot_unlock: bool,
    pub native_rows: Vec<Vec<Value>>,
}
#[derive(Clone, Debug, Default, Serialize, Deserialize)]
#[serde(default)]
pub struct LeagueDefinition {
    pub league: u8,
    pub name: String,
    pub optional_goals_required: u32,
    pub goals: Vec<GoalDefinition>,
}
#[derive(Clone, Debug, Default, Serialize, Deserialize)]
#[serde(default)]
pub struct GoalProgress {
    pub value: f64,
    pub complete: bool,
}
#[derive(Clone, Debug, Default, Serialize, Deserialize)]
pub struct LeagueProgress {
    pub league: u8,
    pub optional_completed: u32,
    pub optional_required: u32,
    pub promotion_open: bool,
    pub goals: Vec<GoalStatus>,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct GoalStatus {
    pub goal: GoalDefinition,
    pub progress: GoalProgress,
}
