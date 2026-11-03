# third_party

Vendored, unmodified third-party sources. Nothing here is edited by this project; update by
replacing a file wholesale and recording the provenance below.

## stb/stb_image.h — stb_image v2.30

- Upstream: <https://github.com/nothings/stb>
- Pinned revision: `d14d46f6b44456eb88beac58cba833a4135d4c89`, file `stb_image.h`.
- SHA-256: `594c2fe35d49488b4382dbfaec8f98366defca819d916ac95becf3e75f4200b3`.
- Licence: dual public domain / MIT; full terms remain in the unmodified header.
- `src/render/car_model.c` defines the implementation with PNG-only support and
  internal linkage. Gameplay and headless tests decode the same lossless sprite atlas;
  no window or raylib function is needed for decoding.

## raygui/raygui.h — raygui 5.0-dev (`RAYGUI_VERSION_MAJOR 4`, `MINOR 5`, `PATCH 0`)

- Upstream: <https://github.com/raysan5/raygui>
- Obtained from: `.slim/clonedeps/repos/raysan5__raylib/examples/core/raygui.h`, the copy
  shipped inside the raylib 6.0 source tree this project builds against. No download was
  needed and no byte was changed.
- Licence: zlib/libpng, Copyright (c) 2014-2026 Ramon Santamaria (@raysan5). The full
  licence text is in the header's own banner comment.

## stb/stb_image_write.h — stb_image_write v1.16

- Upstream: <https://github.com/nothings/stb>
- Obtained from: `.slim/clonedeps/repos/raysan5__raylib/src/external/stb_image_write.h`, the
  copy shipped inside the raylib 6.0 source tree this project builds against. No download was
  needed and no byte was changed (sha256
  `17f339e7582ff4d4d56e40b0e87d77eda8d8f8e62806278ddf8fcf0b8b3d9a84`).
- Licence: dual public domain / MIT, Sean Barrett. The full text is in the header's own banner.

stb_image_write is a **test-only** dependency, used to write the vehicle contact sheet from
`build/tests/oversteer_tests.exe` without a GPU or a window. `tests/car_sheet.c` is the single translation
unit that defines `STB_IMAGE_WRITE_IMPLEMENTATION`. Neither `build/dev/game.dll`, `build/dev/oversteer.exe`,
nor `build/release/oversteer_release.exe` links it.

raygui is a **development-only** dependency. It is compiled into `build/dev/game.dll` only when
`OVERSTEER_DEV_TOOLS` is defined (the default for `build.sh` / `build.bat` development builds)
and `OVERSTEER_HEADLESS` is not. `src/dev/dev_lab.c` is the single translation unit that defines
`RAYGUI_IMPLEMENTATION`. Release builds (`--release`) and the headless test executable link
none of it, which is why `build/release/oversteer_release.exe` and `build/tests/oversteer_tests.exe` are unaffected.
