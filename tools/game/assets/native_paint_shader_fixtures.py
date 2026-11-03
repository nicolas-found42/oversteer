"""Check bounded original car shader color and reflectivity kernels."""

import hashlib
import json
import math
import random
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "artifacts/juiced2-build/native-paint-shaders"


def f32(value):
    return struct.unpack("<f", struct.pack("<f", value))[0]


def execute_slice(program, cosine, exponent, base, secondary, minimum, maximum):
    constants = {int(key): value for key, value in program["literal_constants"].items()}
    constants.update(
        {
            56: base + [0.0],
            62: secondary + [0.0],
            66: [exponent] * 4,
            64: [minimum] * 4,
            60: [maximum] * 4,
        }
    )
    registers = [[0.0] * 4 for _ in range(64)]
    # PS619 instruction30 supplies saturate(dot(-normal, normalized view)).
    # This slice verifies its consumers, not interpolant or normal construction.
    registers[11][1] = cosine
    previous_scalar = 0.0

    def source(operand):
        values = (
            registers[operand["index"]]
            if operand["register"] == "r"
            else constants.get(operand["index"], [0.0] * 4)
        )
        values = [values[index] for index in operand["swizzle"]]
        return [
            (-1 if operand["negate"] else 1) * (abs(value) if operand["absolute"] else value)
            for value in values
        ]

    selected = {31, 32, 46, 47, 48, 50, 52, 53}
    for instruction in program["instructions"]:
        if instruction["index"] not in selected:
            continue
        assert not instruction.get("fetch") and not instruction["predicated"]
        a, b, c = [source(operand) for operand in instruction["sources"]]
        opcode = instruction["vector_opcode"]
        if opcode == "dp3":
            vector = [f32(sum(x * y for x, y in zip(a[:3], b[:3])))] * 4
        elif opcode == "add":
            vector = [f32(x + y) for x, y in zip(a, b)]
        elif opcode == "mul":
            vector = [f32(x * y) for x, y in zip(a, b)]
        elif opcode == "mad":
            vector = [f32(x * y + z) for x, y, z in zip(a, b, c)]
        else:
            raise ValueError(opcode)
        opcode = instruction["scalar_opcode"]
        if opcode == "maxs":
            scalar = max(c[3], c[0])
        elif opcode == "adds_prev":
            scalar = f32(c[3] + previous_scalar)
        elif opcode == "log":
            scalar = f32(math.log2(c[3]))
        elif opcode == "exp":
            scalar = f32(2 ** c[3])
        elif opcode == "mulsc":
            operand = instruction["sources"][2]
            word0, _, word2 = [int(word, 16) for word in instruction["raw"]]
            index = ((word0 >> 26) & 1) | (((word2 >> 29) & 1) << 1)
            index |= operand["raw_swizzle"] & 0x3C
            left = constants[operand["raw_index"]][operand["swizzle"][3]]
            right = registers[index][operand["swizzle"][0]]
            assert not operand["absolute"] and not operand["negate"]
            scalar = f32(left * right)
        elif opcode == "retain_prev":
            scalar = previous_scalar
        else:
            raise ValueError(opcode)
        assert not instruction["vector_clamp"] and not instruction["scalar_clamp"]
        # Co-issued operands were read before either destination is committed.
        for channel in range(4):
            if instruction["vector_mask"] >> channel & 1:
                registers[instruction["vector_dest"]][channel] = vector[channel]
            if instruction["scalar_mask"] >> channel & 1:
                registers[instruction["scalar_dest"]][channel] = scalar
        previous_scalar = scalar
    return registers[2][:3], registers[2][3]


def main():
    manifest = OUT / "programs.json"
    programs = json.loads(manifest.read_text())["programs"]
    program = next(item for item in programs if item["id"] == "car_nodamage-pixel-619")
    bindings = {item["name"]: item["register_index"] for item in program["bindings"]}
    assert {
        key: bindings[key]
        for key in ["colour1", "colour2", "twoToneExp", "minReflect", "maxReflect"]
    } == {
        "colour1": 62,
        "colour2": 56,
        "twoToneExp": 66,
        "minReflect": 64,
        "maxReflect": 60,
    }
    rng = random.Random(0x619)
    worst_color = worst_reflect = 0.0
    samples = []
    for index in range(5000):
        cosine = f32(rng.uniform(0.0001, 1.0))
        exponent = f32(rng.uniform(0.0, 8.0))
        base = [f32(rng.random() * 2) for _ in range(3)]
        secondary = [f32(rng.random() * 2) for _ in range(3)]
        minimum, maximum = f32(rng.random()), f32(rng.random())
        actual, reflect = execute_slice(
            program, cosine, exponent, base, secondary, minimum, maximum
        )
        expected = [s + (b - s) * cosine**exponent for b, s in zip(base, secondary)]
        error = max(abs(a - e) for a, e in zip(actual, expected))
        reflect_error = abs(reflect - (maximum + (minimum - maximum) * cosine))
        worst_color = max(error, worst_color)
        worst_reflect = max(reflect_error, worst_reflect)
        assert error < 2e-6 and reflect_error < 2e-7, (actual, expected, reflect)
        if index < 4:
            samples.append(
                dict(
                    cosine=cosine,
                    exponent=exponent,
                    base=base,
                    secondary=secondary,
                    minimum=minimum,
                    maximum=maximum,
                    output=actual,
                    reflect=reflect,
                )
            )
    report = dict(
        helper_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        source_manifest_sha256=hashlib.sha256(manifest.read_bytes()).hexdigest(),
        cases=5000,
        program="car_nodamage-pixel-619",
        instruction_indices=[31, 32, 46, 47, 48, 50, 52, 53],
        equations={
            "angle": "c=saturate(dot(-normal, normalized_view)) at instruction30",
            "paint": "colour1+(colour2-colour1)*pow(c,twoToneExp)",
            "reflect": "maxReflect+(minReflect-maxReflect)*c",
        },
        max_abs_error=dict(color=worst_color, reflect=worst_reflect),
        samples=samples,
        limits=[
            "Decoded original ALU slice compared with independent high-level equations.",
            "CPU f32 model, not native GPU log/exp precision or a hardware rendering test.",
            "Cosine is supplied; tangent frame and normal construction remain separate.",
            "Zero cosine, NaN, denormals, active technique and full BRDF are outside this fixture.",
            "car_nodamage lacks flake/thin-film bindings; other car effects remain distinct.",
        ],
    )
    (OUT / "kernel-fixtures.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({key: report[key] for key in ["cases", "max_abs_error", "equations"]}))


if __name__ == "__main__":
    main()
