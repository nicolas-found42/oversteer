use oversteer_core::*;
fn main() {
    let content: GameContent =
        serde_json::from_str(&std::fs::read_to_string("data/juiced2/content.json").unwrap())
            .unwrap();
    let save = std::fs::read_to_string(std::env::args().nth(1).unwrap()).unwrap();
    let game = Game::load_json(content, &save).unwrap();
    let snapshot = game.frame_snapshot();
    for status in snapshot
        .league_progress
        .goals
        .iter()
        .filter(|s| !s.progress.complete)
    {
        println!(
            "GOAL {} {} {:?} qualifier{}",
            status.goal.id, status.goal.kind, status.goal.args, status.goal.qualifier
        );
        println!("  {}", game.events_for_goal(&status.goal.id).join(" "));
    }
    for event in game
        .content
        .events
        .iter()
        .filter(|e| e.league == snapshot.career.league && !e.is_sponsor)
    {
        println!(
            "EVENT {} {:?} class{} {} proto{} NOS{} end{} {:?}",
            event.id,
            event.mode,
            event.car_class,
            event.contest_type,
            event.prototype,
            event.extreme_nos,
            event.endurance,
            event.track_id
        );
    }
}
