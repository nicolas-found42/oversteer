"""Stage static original car_nodamage Xenos programs, not active-car parity proof."""

import hashlib
import json
import struct
from pathlib import Path

from decode_texturecombine import ROOT, alu, data, fmt_operand, fmt_scalar, groups

OUT = ROOT / "artifacts/juiced2-build/native-paint-shaders"
OUT.mkdir(exist_ok=True)


def decode(name, kind, index):
    record = groups[0 if kind == "vertex" else 1][index]
    start = record["offset"]
    raw = data[start : start + record["size"]]
    base = record["metadata_size"]
    header = struct.unpack_from(">I", raw, 0x18)[0]
    offset, size = struct.unpack_from(">2I", raw, header)
    assert offset + size == record["code_size"]
    code = raw[base + offset : base + offset + size]
    words = struct.unpack(">" + str(size // 4) + "I", code)
    cf = []
    instructions = {}
    lines = []
    stop = False
    for pair in range(len(words) // 3):
        a, b, c = words[3 * pair : 3 * pair + 3]
        for half, (w0, w1) in enumerate([(a, b & 65535), ((b >> 16) | (c << 16), c >> 16)]):
            opcode = (w1 >> 12) & 15
            entry = dict(
                index=pair * 2 + half,
                opcode=opcode,
                address=w0 & 4095,
                count=(w0 >> 12) & 7,
                sequence=(w0 >> 16) & 4095,
                predicate_condition=bool(w1 & (1 << 9)),
            )
            cf.append(entry)
            if opcode in [1, 2, 5, 6]:
                lines.append(f"CF{entry['index']} op{opcode}:")
                for j in range(entry["count"]):
                    index = entry["address"] + j
                    fetch = bool((entry["sequence"] >> (j * 2)) & 1)
                    if fetch:
                        fw = words[index * 3 : index * 3 + 3]
                        op = fw[0] & 31
                        ins = dict(
                            index=index,
                            fetch=True,
                            fetch_opcode=op,
                            raw=[f"{w:08x}" for w in fw],
                            dest=(fw[0] >> 12) & 63,
                            source=(fw[0] >> 5) & 63,
                            fetch_constant=(fw[0] >> 20) & 31,
                            dest_swizzle=[(fw[1] >> (k * 3)) & 7 for k in range(4)],
                        )
                        if op == 0:
                            ins.update(
                                vertex_format=(fw[1] >> 16) & 63,
                                vertex_stride=fw[2] & 255,
                                vertex_offset_words=((fw[2] >> 8) & 0x7FFFFF),
                                fetch_constant_select=(fw[0] >> 25) & 3,
                            )
                        else:
                            ins.update(
                                texture_index=(fw[0] >> 20) & 31,
                                source_swizzle=[(fw[0] >> (26 + k * 2)) & 3 for k in range(3)],
                            )
                        lines.append(f" {index:02d} FETCH " + str(ins))
                    else:
                        ins = alu(words, index)
                        src = ", ".join(fmt_operand(o) for o in ins["sources"])
                        dst = (
                            ("EXPORT" if ins["export"] else "r")
                            + str(ins["vector_dest"])
                            + "."
                            + "".join("xyzw"[k] for k in range(4) if ins["vector_mask"] >> k & 1)
                        )
                        suffix = "_sat" if ins["vector_clamp"] else ""
                        line = f" {index:02d} {ins['vector_opcode']}{suffix} {dst}, {src}"
                        if ins["scalar_mask"] or ins["scalar_opcode"] != "retain_prev":
                            line += (
                                f" | {ins['scalar_opcode']} r{ins['scalar_dest']}."
                                + "".join(
                                    "xyzw"[k] for k in range(4) if ins["scalar_mask"] >> k & 1
                                )
                                + ", "
                                + fmt_scalar(ins)
                            )
                        lines.append(line)
                    instructions[index] = ins
            else:
                lines.append(f"CF{entry['index']} op{opcode} raw{w0:08x}/{w1:04x}")
                assert opcode in [0, 12], entry
            if opcode in [2, 6]:
                stop = True
                break
        if stop:
            break
    ctbase = 0x28
    _, _, _, count, at, _, _ = struct.unpack_from(">7I", raw, ctbase)
    bindings = []
    for i in range(count):
        no, rs, ri, rc, res, ty, de = struct.unpack_from(">I4H2I", raw, ctbase + at + i * 20)
        no += ctbase
        bindings.append(
            dict(
                name=raw[no : raw.index(0, no)].decode(),
                register_set=rs,
                register_index=ri,
                register_count=rc,
            )
        )
    literal = {
        str(256 - offset // 16 + i): list(struct.unpack_from(">4f", raw, base + i * 16))
        for i in range(offset // 16)
    }
    ident = name + "-" + kind + "-" + str(record["index"])
    (OUT / (ident + ".shader")).write_bytes(raw)
    (OUT / (ident + ".ucode")).write_bytes(code)
    (OUT / (ident + ".asm.txt")).write_text("\n".join(lines) + "\n")
    return dict(
        id=ident,
        kind=kind,
        record=record,
        sha256=hashlib.sha256(raw).hexdigest(),
        ucode_sha256=hashlib.sha256(code).hexdigest(),
        bindings=bindings,
        literal_constants=literal,
        control_flow=cf,
        instructions=list(instructions.values()),
    )


assert data[0x3885CC : 0x3885CC + 12] == b"car_nodamage"
programs = []
techniques = []
for descriptor, name, vertex, pixel in [
    (0x38964C, "Car_2a", 575, 617),
    (0x389770, "Car_2b", 575, 618),
    (0x389894, "Car_3", 576, 619),
    (0x3899E0, "Car_NoTexturing", 575, 620),
]:
    assert data[descriptor : data.index(0, descriptor)].decode() == name
    annotation_count, annotation_bytes = struct.unpack_from(">2I", data, descriptor + 40)
    at = descriptor + 48 + annotation_bytes
    assert struct.unpack_from(">I", data, at)[0] == 1
    assert data[at + 4 : at + 7] == b"P0\0"
    assert struct.unpack_from(">I", data, at + 60)[0] == vertex
    assert struct.unpack_from(">I", data, at + 108)[0] == pixel
    # The expressions following these exact indices are four-byte constants.
    assert struct.unpack_from(">I", data, at + 64)[0] == 4
    assert struct.unpack_from(">I", data, at + 112)[0] == 4
    techniques.append(
        dict(
            name=name,
            descriptor=hex(descriptor),
            pass_offset=hex(at),
            vertex_index=vertex,
            pixel_index=pixel,
            annotation_count=annotation_count,
            annotations=data[descriptor + 48 : at].hex(),
        )
    )
    for kind, index in [("vertex", vertex), ("pixel", pixel)]:
        ident = f"car_nodamage-{kind}-{index}"
        if not any(p["id"] == ident for p in programs):
            programs.append(decode("car_nodamage", kind, index))
report = dict(
    helper_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    source=dict(
        path="artifacts/juiced2-build/world-uv/Juiced2.fxl", sha256=hashlib.sha256(data).hexdigest()
    ),
    effect=dict(name="car_nodamage", name_offset="0x3885cc"),
    techniques=techniques,
    programs=programs,
    decoder_source_sha256=hashlib.sha256(
        (ROOT / "tools/game/assets/decode_tunnel_shaders.py").read_bytes()
    ).hexdigest(),
    limits=[
        "Static named effect/pass bindings; not evidence of active gameplay technique selection.",
        "car/carLicenced/carGPR/carPlastic permutations remain distinct.",
        "Disassembly requires independent equation/fixture checks before a shader port.",
        "Textures, interpolants, render states and lighting inputs remain separate.",
        "This is source-only staging; no runtime shaders or assets changed.",
    ],
)
(OUT / "programs.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
print(
    json.dumps(
        dict(
            techniques=techniques,
            programs=[dict(id=p["id"], instructions=len(p["instructions"])) for p in programs],
        )
    )
)
