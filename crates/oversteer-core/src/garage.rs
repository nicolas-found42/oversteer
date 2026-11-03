use crate::Customization;
use serde::{Deserialize, Serialize};
#[derive(Clone, Debug, Serialize, Deserialize, PartialEq, Eq)]
pub struct CartItem {
    pub id: String,
    pub car_id: String,
    pub label: String,
    pub cost: u32,
    pub field: String,
}
#[derive(Clone, Debug, Default, Serialize, Deserialize)]
#[serde(default)]
pub struct VehicleHistory {
    pub mileage_m: f64,
    pub wins: u32,
    pub losses: u32,
    pub purchase_price: u32,
    pub total_spent: u64,
    pub pink_slip_wins: u32,
    pub pink_slip_losses: u32,
    pub sales: u32,
    pub acquired_by: String,
}
#[derive(Clone, Copy, Debug, Serialize, Deserialize, PartialEq, Eq)]
pub enum TransactionKind {
    SpectatorStake,
    SpectatorPayout,
    BuyCar,
    SellCar,
    Customization,
    WagerEscrow,
    WagerSettlement,
    RaceReward,
    PinkSlipWin,
    PinkSlipLoss,
    RecruitDriver,
    EntranceFee,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct CareerTransaction {
    pub sequence: u64,
    pub kind: TransactionKind,
    pub amount: i64,
    pub car_id: Option<String>,
    pub event_id: Option<String>,
    pub description: String,
}
pub(crate) fn cart_changes(
    id: &str,
    old: &Customization,
    new: &Customization,
    owned: &[String],
) -> Vec<CartItem> {
    let mut items = vec![];
    let mut push = |field: &str, label: &str, cost: u32| {
        let owned_part = match field {
            "wheels" => Some(format!("wheels:{}", new.wheels)),
            "body_kit" => Some(format!("body_kit:{}", new.body_kit)),
            "interior_kit" => Some(format!("interior_kit:{}", new.interior_kit)),
            _ if field.starts_with("part:") => Some(format!(
                "{field}:{}",
                new.parts
                    .get(&field[5..])
                    .map(String::as_str)
                    .unwrap_or("stock")
            )),
            _ => None,
        };
        let cost = if owned_part
            .as_ref()
            .map(|p| owned.contains(p))
            .unwrap_or(false)
        {
            0
        } else {
            cost
        };
        items.push(CartItem {
            id: format!("{id}:{field}"),
            car_id: id.into(),
            label: label.into(),
            cost,
            field: field.into(),
        });
    };
    for slot in old
        .parts
        .keys()
        .chain(new.parts.keys())
        .collect::<std::collections::BTreeSet<_>>()
    {
        if old.parts.get(slot) != new.parts.get(slot) {
            let stock = new.parts.get(slot).map(|p| p == "stock").unwrap_or(true);
            push(
                &format!("part:{slot}"),
                &format!("{} part", slot.replace('_', " ")),
                if stock { 0 } else { 2000 },
            );
        }
    }
    if old.paint != new.paint || old.finish != new.finish || old.native_paint != new.native_paint {
        // Native821C5E20 stores one paint record/price, including family and RGB.
        let finish = new
            .native_paint
            .as_ref()
            .and_then(|record| record.finish_id())
            .unwrap_or(&new.finish);
        let price = match finish {
            "gloss" => 3000,
            "metallic" => 5000,
            "flake" | "pearl" => 12000,
            "matt" | "matte" => 7500,
            "thinfilm" => 20000,
            // Legacy reconstruction finishes remain readable, without claiming
            // a native price or a native thin-film/chrome equivalence.
            _ => {
                u32::from(old.paint != new.paint) * 500 + u32::from(old.finish != new.finish) * 250
            }
        };
        push("paint", "Body paint", price);
    }
    if old.wheels != new.wheels {
        push(
            "wheels",
            "Wheel swap",
            if new.wheels == "stock" { 0 } else { 1000 },
        );
    }
    if old.body_kit != new.body_kit {
        push(
            "body_kit",
            "Body kit",
            if new.body_kit == "stock" { 0 } else { 2000 },
        );
    }
    if old.interior_kit != new.interior_kit {
        push(
            "interior_kit",
            "Interior kit",
            if new.interior_kit == "stock" { 0 } else { 1500 },
        );
    }
    for (field, label, before, after) in [
        ("engine", "Engine", old.engine, new.engine),
        (
            "transmission",
            "Transmission",
            old.transmission,
            new.transmission,
        ),
        ("suspension", "Suspension", old.suspension, new.suspension),
        ("tyres", "Tyres", old.tyres, new.tyres),
        ("nitrous", "Nitrous", old.nitrous, new.nitrous),
    ] {
        if before != after {
            let key = format!("{field}:{after}");
            let highest = owned
                .iter()
                .filter_map(|p| p.strip_prefix(&format!("{field}:")))
                .filter_map(|v| v.parse::<u8>().ok())
                .max()
                .unwrap_or(before)
                .max(before);
            let cost = if owned.contains(&key) {
                0
            } else {
                u32::from(after.saturating_sub(highest)) * 1000
            };
            push(field, &format!("{label} stage {after}"), cost);
        }
    }
    if old.tuning != new.tuning {
        push("tuning", "Setup tuning", 250);
    }
    if old.vinyls != new.vinyls {
        push(
            "vinyls",
            "Vinyl layers",
            250 * new.vinyls.len().max(1) as u32,
        );
    }
    if old.plate_text != new.plate_text || old.plate_style != new.plate_style {
        push("plate", "License plate", 250);
    }
    if old.wheel_paint != new.wheel_paint {
        push("wheel_paint", "Wheel paint", 250);
    }
    if old.part_paints != new.part_paints {
        push(
            "part_paints",
            "Part paint",
            250 * new.part_paints.len().max(1) as u32,
        );
    }
    items
}
pub(crate) fn revert_field(new: &mut Customization, old: &Customization, field: &str) {
    match field {
        "paint" => {
            new.paint = old.paint;
            new.finish = old.finish.clone();
            new.native_paint = old.native_paint.clone();
        }
        "finish" => new.finish = old.finish.clone(),
        "wheels" => new.wheels = old.wheels.clone(),
        "body_kit" => new.body_kit = old.body_kit.clone(),
        "interior_kit" => new.interior_kit = old.interior_kit.clone(),
        "engine" => new.engine = old.engine,
        "transmission" => new.transmission = old.transmission,
        "suspension" => new.suspension = old.suspension,
        "tyres" => new.tyres = old.tyres,
        "nitrous" => new.nitrous = old.nitrous,
        "tuning" => new.tuning = old.tuning,
        "vinyls" => new.vinyls = old.vinyls.clone(),
        "plate" => {
            new.plate_text = old.plate_text.clone();
            new.plate_style = old.plate_style.clone();
        }
        "wheel_paint" => new.wheel_paint = old.wheel_paint,
        "part_paints" => new.part_paints = old.part_paints.clone(),
        _ => {
            if let Some(slot) = field.strip_prefix("part:") {
                if let Some(part) = old.parts.get(slot) {
                    new.parts.insert(slot.into(), part.clone());
                } else {
                    new.parts.remove(slot);
                }
            }
        }
    }
}
pub(crate) fn owned_parts(custom: &Customization) -> Vec<String> {
    let mut parts = vec![
        format!("wheels:{}", custom.wheels),
        format!("body_kit:{}", custom.body_kit),
        format!("interior_kit:{}", custom.interior_kit),
    ];
    for (slot, part) in &custom.parts {
        parts.push(format!("part:{slot}:{part}"));
    }
    for (field, level) in [
        ("engine", custom.engine),
        ("transmission", custom.transmission),
        ("suspension", custom.suspension),
        ("tyres", custom.tyres),
        ("nitrous", custom.nitrous),
    ] {
        for i in 0..=level {
            parts.push(format!("{field}:{i}"));
        }
    }
    parts
}
