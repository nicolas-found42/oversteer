use oversteer_core::*;
fn main() {
    let _label = "1m";
    let event = "native_c8c48fc7_035";
    let league = 3;
    let content: GameContent =
        serde_json::from_str(&std::fs::read_to_string("data/juiced2/content.json").unwrap())
            .unwrap();
    let fixture = std::fs::read_to_string(
        "artifacts/juiced2-build/rome-drift-1m-host-3d-v1-initial-save.json",
    )
    .unwrap();
    let mut game = Game::load_json(content, &fixture).unwrap();
    let prefix = "artifacts/juiced2-build/rome-drift-1m-host-3d-v2-classes";
    std::fs::write(
        format!("{prefix}-initial-save.json"),
        game.save_json().unwrap(),
    )
    .unwrap();
    game.command(GameCommand::StartRace {
        event_id: event.into(),
        career: true,
        wager: 0,
        pink_slip: false,
    })
    .unwrap();
    std::fs::write(
        format!("{prefix}-initial-snapshot.json"),
        serde_json::to_vec(&game.frame_snapshot()).unwrap(),
    )
    .unwrap();
    let mut controls = Vec::new();
    let mut first_active_tick = None;
    let mut unsupported = 0u32;
    let start = std::time::Instant::now();
    for tick in 0..14400 {
        let before = game.frame_snapshot();
        let race = before.race.as_ref().unwrap();
        if race.countdown <= 0. && first_active_tick.is_none() {
            first_active_tick = Some(tick);
        }
        let mut input = game.scenario_endurance_predictive_input();
        let desired = input.steering;
        let raw = if desired == 0. {
            0.
        } else {
            -desired.signum() * (0.12f32 + 0.88f32 * desired.abs())
        };
        input.steering = if raw.abs() > 0.12 {
            -raw.signum() * (raw.abs() - 0.12) / 0.88
        } else {
            0.
        };
        controls.push(serde_json::json!({"tick":tick,"active_tick":first_active_tick.map(|first|tick-first),"countdown_before":race.countdown,"desired_steering":desired,"raw_axes":{"steering_0":raw,"throttle_5":input.throttle,"brake_4":input.brake},"input":input}));
        game.advance(1. / 60., input);
        let snapshot = game.frame_snapshot();
        let race = snapshot.race.as_ref().unwrap();
        let p = &race.racers[0];
        if race.elapsed > 0. && p.surface_contacts.iter().filter(|c| c.active).count() < 2 {
            unsupported += 1;
        }
        if tick % 600 == 0 {
            println!(
                "tick{tick} time{} chain{} pos{:?}",
                race.elapsed, p.chain_score, p.position
            );
        }
        if snapshot.screen == GameScreen::Results || unsupported > 30 || tick == 14399 {
            std::fs::write(
                format!("{prefix}-controls.json"),
                serde_json::to_vec(&controls).unwrap(),
            )
            .unwrap();
            std::fs::write(format!("{prefix}-save.json"), game.save_json().unwrap()).unwrap();
            std::fs::write(
                format!("{prefix}-final-snapshot.json"),
                serde_json::to_vec(&snapshot).unwrap(),
            )
            .unwrap();
            let metadata = serde_json::json!({"event_id":event,"car_id":"GT4_SUBR0017","initial_league_fixture":league,"first_active_tick":first_active_tick,"tick_count":controls.len(),"outer_dt_seconds":1./60.,"unsupported_frames":unsupported,"cpu_seconds":start.elapsed().as_secs_f64(),"core_checkpoint":"source-full-3d-class-paint-v2","steering_mapping":"raw=-sign(desired)*(0.12+0.88*abs(desired)); actual=-sign(raw)*(abs(raw)-0.12)/0.88, all f32 before advance","result":snapshot.result});
            std::fs::write(
                format!("{prefix}-evidence.json"),
                serde_json::to_vec_pretty(&metadata).unwrap(),
            )
            .unwrap();
            println!("RESULT {metadata}");
            break;
        }
    }
}
