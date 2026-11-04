use oversteer_core::*;

#[test]
fn evo_uses_gsr_mass_instead_of_the_bad_secondary_catalog_value() {
    let mut content = GameContent {
        cars: vec![
            CarDefinition {
                id: "GT4_MITS0001".into(),
                handling: Handling {
                    mass: 320.,
                    ..Default::default()
                },
                ..Default::default()
            },
            CarDefinition {
                id: "unrelated".into(),
                handling: Handling {
                    mass: 1100.,
                    ..Default::default()
                },
                ..Default::default()
            },
        ],
        ..Default::default()
    };
    let original = content.clone();
    content.apply_oversteer_vehicle_corrections();
    assert_eq!(content.cars[0].handling.mass, 1410.);
    assert_eq!(content.cars[1].handling.mass, 1100.);
    assert_eq!(original.cars[0].handling.mass, 320.);
    content.apply_oversteer_vehicle_corrections();
    assert_eq!(content.cars[0].handling.mass, 1410.);
}
