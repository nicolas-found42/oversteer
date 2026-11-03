"""Bind the native pearl-balance span to the successful startup constructor path."""

import hashlib
import json
import re
import shutil
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "artifacts/juiced2-recovery/recompiled-handling"
OUTPUT = ROOT / "artifacts/juiced2-build/presentation/pearl-balance-startup"


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    data_path = SOURCE / "decoded-sections/824A0000-.data.bin"
    constants_path = SOURCE / "decoded-sections/82000400-.rdata.bin"
    data, constants = data_path.read_bytes(), constants_path.read_bytes()
    bias_address = ((-32179 << 16) - 6656) & 0xFFFFFFFF
    double_address = ((-32251 << 16) - 12040) & 0xFFFFFFFF
    span_address = ((-32168 << 16) - 11876) & 0xFFFFFFFF
    bias = struct.unpack_from(">f", data, bias_address - 0x824A0000)[0]
    high = struct.unpack_from(">d", constants, double_address - 0x82000400)[0]
    span_disk = struct.unpack_from(">f", data, span_address - 0x824A0000)[0]
    initialized = struct.unpack(">f", struct.pack(">f", high - bias))[0]
    begin, end, entry = 0x824A0010, 0x824A0B68, 0x824A022C
    pointer = struct.unpack_from(">I", data, entry - 0x824A0000)[0]
    assert begin <= entry < end and (entry - begin) % 4 == 0
    assert pointer == 0x82474BB0
    functions = []
    for address in ["82474BB0", "823D8398"]:
        path = SOURCE / "physics-functions" / f"{address}.cpp"
        shutil.copyfile(path, OUTPUT / path.name)
        functions.append({"name": address, "path": str(path.relative_to(ROOT)),
                          "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    starts = []
    for path in (SOURCE / "generated/default").glob("*recomp*.cpp"):
        source = path.read_text()
        match = re.search(r"DEFINE_REX_FUNC\(xstart\)", source)
        if not match:
            continue
        following = source.find("DEFINE_REX_FUNC(", match.end())
        body = source[match.start():following if following >= 0 else len(source)]
        assert "sub_823D8398(ctx, base)" in body and "ctx.lr = 0x823D8038" in body
        starts.append((path, body))
    assert len(starts) == 1
    path, body = starts[0]
    (OUTPUT / "xstart.cpp").write_text(body)
    functions.append({"name": "xstart", "path": str(path.relative_to(ROOT)),
                      "retained_body_sha256": hashlib.sha256(body.encode()).hexdigest()})
    report = {
        "evidence_type": "Static original bytes and translated PPC, not a runtime trace",
        "startup_path": "xstart call823D8034 ->823D8398 ->constructor table ->82474BB0",
        "table": {"begin": f"{begin:08X}", "end_exclusive": f"{end:08X}",
                  "entry": f"{entry:08X}", "entry_index": (entry - begin) // 4,
                  "pointer": f"{pointer:08X}", "skip_values": [0, -1]},
        "bias": {"address": f"{bias_address:08X}", "decoded_initial": bias,
                 "bits": data[bias_address-0x824A0000:bias_address-0x824A0000+4].hex()},
        "upper_double": {"address": f"{double_address:08X}", "value": high,
                         "bits": constants[double_address-0x82000400:
                                           double_address-0x82000400+8].hex()},
        "span": {"address": f"{span_address:08X}", "disc_initial": span_disk,
                 "after_constructor": initialized, "expression": "f32(double1 - f32(bias))"},
        "default_ui_mapping": "exponent = f32(x * initialized_span + bias), therefore x",
        "functions": functions,
        "sections": [{"path": str(path.relative_to(ROOT)),
                      "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
                     for path in [data_path, constants_path]],
        "limits": ["Successful startup reaches the C++ constructor loop.",
                   ("This proves the initialized default, not absence of every "
                    "later indirect write.")],
    }
    (OUTPUT / "contract.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"bias": bias, "upper": high, "initialized_span": initialized,
                      "table_index": (entry - begin) // 4, "path": str(OUTPUT)}))


if __name__ == "__main__":
    main()
