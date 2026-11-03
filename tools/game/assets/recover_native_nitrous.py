"""Retain the bounded native NOS force, pressure, drain and refill contract."""

import hashlib
import json
import shutil
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "artifacts/juiced2-recovery/recompiled-handling"
OUTPUT = ROOT / "artifacts/juiced2-build/native-nitrous"

# Effective addresses come from explicit lis/addi/lfs operands, not hand-added hex.
# Each tuple is (lis immediate, intervening addi, lfs displacement, source function).
LOADS = {
    "pressure_full": (-32251, 0, -11280, "820F82D0"),
    "pressure_upper_boundary": (-32251, 0, -11324, "820F82D0"),
    "pressure_lower_boundary": (-32251, 0, -10856, "820F82D0"),
    "pressure_middle": (-32255, 0, 5516, "820F82D0"),
    "pressure_low_and_refill_delay": (-32254, -16, -22924, "820F82D0"),
    "refill_coefficient_common": (-32254, -16, 0, "820F82D0"),
    "refill_coefficient_control_mode_2": (-32251, 0, -12016, "820F82D0"),
    "refill_scale": (-32179, 0, -16608, "820F82D0"),
    "extra_refill_delta_cap": (-32253, 0, -152, "820F82D0"),
    "forward_force_gain": (-32179, 0, -16720, "820F82D0"),
    "drain_rate": (-32253, 0, -2280, "8225FDE0"),
    "refill_metric_gate": (-32253, 0, -2388, "820F82D0"),
    "wheel_point_speed_gate": (-32253, 0, -2348, "82111E50"),
    "four_wheel_aggregation_scale": (-32181, 0, 27272, "820F5480"),
    "capacity_override_sentinel": (-32253, 0, -2664, "8210D0E8"),
    "capacity_override_scale": (-32253, 0, -2520, "8210D0E8"),
    "capacity_override_bias": (-32253, 0, -2196, "8210D0E8"),
    "capacity_default": (-32253, 0, -3768, "8210D0E8"),
    "instance_capacity_control_default": (-32254, 0, -22300, "82109860"),
}
FUNCTIONS = [
    "820F82D0", "820F69F8", "820F39E0", "820F5480", "82111E50", "8226DA48",
    "8225DB98", "8225FDE0", "82260108", "8225E3B8", "8210D0E8", "821064C8",
    "8225EB58", "82266218", "82265FF8", "8226B088", "820F7F78", "820F3028",
    "82109860", "82109BE8", "8210A330", "8210B510", "8210B058",
]


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    sections = [
        (int(path.name.split("-")[0], 16), path, path.read_bytes())
        for path in (SOURCE / "decoded-sections").glob("*.bin")
    ]
    constants = {}
    for name, (high, addend, displacement, function) in LOADS.items():
        address = ((high << 16) + addend + displacement) & 0xFFFFFFFF
        matches = [
            (base, path, data) for base, path, data in sections
            if base <= address and address + 4 <= base + len(data)
        ]
        if len(matches) != 1:
            raise ValueError(f"Ambiguous source constant {name}: {address:08X}")
        base, path, data = matches[0]
        raw = data[address - base:address - base + 4]
        constants[name] = {
            "address": f"{address:08X}", "bits_be": raw.hex(),
            "value": struct.unpack(">f", raw)[0], "function": function,
            "address_operands": {"lis": high, "addi": addend, "lfs": displacement},
            "section": str(path.relative_to(ROOT)), "section_sha256": sha256(path),
            "status": "decoded executable initial value; original runtime changes not observed",
        }
    functions = []
    for address in FUNCTIONS:
        path = SOURCE / "physics-functions" / f"{address}.cpp"
        shutil.copyfile(path, OUTPUT / path.name)
        functions.append({"address": address, "source": str(path.relative_to(ROOT)),
                          "sha256": sha256(path)})
    contract = {
        "schema_version": 1,
        "evidence_type": "Static translated PPC and decoded original executable bytes",
        "constants": constants, "functions": functions,
        "force": {
            "gates": ["car96 != 0", "V4336 & 0x00400000", "V4300 > 0",
                      "car528 > 1 contact wheels", "encoded physical gear not 0 or 1"],
            "pressure_input": "activation snapshot car112 / capacity V4304",
            "bands": ["ratio == 1: 1.4", "ratio > .66: 1", "ratio > .33: .7", "else: .3"],
            "ordered_f32_expression": "V3820 += ((V4236 * pressure) * tuningPower) * 13600",
            "tuning_power": "821064C8(global132, car684, 0)",
            "frame": "BODY +Z external force3812/3816/3820, copied to3764/3768/3772",
            "integration": "R rotates BODY force to WORLD RK momentum derivative; no extra dt here",
        },
        "drain": "if active flag: V4300=max(0,fma(-V4308,dt,V4300)); initialized V4308=.4",
        "capacity": {
            "spawn_writer": "8210D0E8: if car9640 != -2: fma(car9640,3,2), else5",
            "instance_default": "82109860 initializes car9640=.5, giving live capacity3.5",
            "stored": "P416=1; P420=P424=capacity; init V4300=P420,V4304=P424",
            "persistence": "8210B510/8210B058 stream9636, then+4(9640), as four-byte values",
            "limit": ("UI setter for car9640 and complete start/reset "
                      "lifecycle unresolved"),
        },
        "refill": {
            "wheel_metric": ("speed=length(physicalWheel136/140/144); speed>4 ? "
                             "clamp(abs(residual368X*(1/speed)),0,1) : 0"),
            "aggregation": ("Child82111E50 adds ratio to owner512; caller820F5480 adds "
                            "it AGAIN, then *.25: metric=.5*sum4(ratios)"),
            "gates": "metric>.2, inactive NOS, tank<capacity; accumulating timer must exceed.3",
            "normal": "tank=min(capacity,fma((metric*(controlMode156==2?25:12))*dt,.04,tank))",
            "extra": ("activeConfig12!=0 && inactive: "
                      "tank=min(capacity,fma(min(globalDelta,.06666667),.3,tank))"),
            "control_mode": ("156==1 active human;156==2 autonomous/common; "
                             "distinct from drift field788"),
        },
        "independent_review": [
            "Core owner independently traced BODY-force copy and RK frame/lifecycle.",
            ("Core owner independently confirmed double wheel-metric accumulation "
             "and mode156 boundary."),
        ],
        "limits": [
            "Source observations are not original executable runtime traces.",
            "Active config12 ExtremeNOS binding is retained separately in native-performance.",
            ("Force/tuning adaptation for accepted donor vehicles still requires "
             "a coherent core port."),
            ("Original world scheduler/control handoff and exact step ordering "
             "remain separate boundaries."),
        ],
    }
    (OUTPUT / "contract.json").write_text(json.dumps(contract, indent=2) + "\n")
    print(json.dumps({"constants": len(constants), "functions": len(functions),
                      "path": str(OUTPUT / "contract.json")}))


if __name__ == "__main__":
    main()
