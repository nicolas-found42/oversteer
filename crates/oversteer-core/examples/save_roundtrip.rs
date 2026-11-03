use oversteer_core::*;
fn main() {
    let raw = std::fs::read_to_string(std::env::args().nth(1).unwrap()).unwrap();
    let typed: GameSave = serde_json::from_str(&raw).unwrap();
    std::fs::write(
        "/tmp/oversteer-typed-resave.json",
        serde_json::to_string_pretty(&typed).unwrap(),
    )
    .unwrap();
    let content: GameContent =
        serde_json::from_str(&std::fs::read_to_string("data/juiced2/content.json").unwrap())
            .unwrap();
    let game = Game::load_json(content, &raw).unwrap();
    let first = game.save_json().unwrap();
    let again = Game::load_json(game.content.clone(), &first)
        .unwrap()
        .save_json()
        .unwrap();
    println!("current_serialized_roundtrip_equal {}", first == again);
}
