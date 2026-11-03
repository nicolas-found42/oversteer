# Original two-color and reflection kernels

The supplied `Juiced2.fxl` contains a named `car_nodamage` effect at file offset
`0x3885cc`. Its four static techniques bind these original programs:

| Technique descriptor | Name | Vertex index | Pixel index |
|---|---|---:|---:|
| `0x38964c` | `Car_2a` | 575 | 617 |
| `0x389770` | `Car_2b` | 575 | 618 |
| `0x389894` | `Car_3` | 576 | 619 |
| `0x3899e0` | `Car_NoTexturing` | 575 | 620 |

The descriptor pass fields and four-byte constant expressions bind these indices;
their names are not inferred from adjacent shader order. The raw records,
microcode, disassembly, constant tables and hashes are retained in
`artifacts/juiced2-build/native-paint-shaders/programs.json`.

Pixel program 619 binds `colour1` to c62, `colour2` to c56, `twoToneExp` to c66,
`minReflect` to c64 and `maxReflect` to c60. The separately recovered 72-byte
material uploader maps these to secondary RGB, base RGB, exponent, minimum and
maximum reflection respectively.

Its bounded color and reflection calculations are:

```text
c = saturate(dot(normal, fragment_to_camera))
color = secondary_rgb + (base_rgb - secondary_rgb) * pow(c, twoToneExp)
reflection_factor = maxReflect + (minReflect - maxReflect) * c
```

The direction is source-bound: vertex program 576 exports world position minus
`g_cameraPosition` through interpolant 4. Pixel program 619 normalizes that view
vector and instruction 30 takes the saturated negative dot product with its
constructed normal. Godot's corresponding fragment-to-camera direction therefore
uses the positive dot product. An absolute dot product or `1-c` exponent input
does not reproduce this kernel.

Instructions 31/32 compute the reflection difference through the previous-scalar
register. Instructions 46/47 and 52 compute base-2 log, exponent multiplication
and base-2 exponent; 48/53 compute the color interpolation. Instruction 50 writes
the reflection factor. Co-issued scalar operands must be read before either
instruction destination is committed.

Reproduce the staged extraction and bounded equation checks with:

```sh
python3 tools/game/assets/decode_native_paint_shaders.py
python3 tools/game/assets/native_paint_shader_fixtures.py
```

The 5,000 sampled input cases compare a decoded ALU slice with independent
high-level equations. Largest absolute differences are approximately 1.43e-7 for
color and 5.53e-8 for reflection. This is a CPU float32 model of the source
instructions, rather than hardware GPU precision or a rendered parity check.
The log-at-zero edge, NaNs and denormals are outside those sampled cases.

These findings do not identify the active full-game car technique. The distinct
`car`, `carLicenced`, `carGPR` and `carPlastic` effects include dynamic shader
selection expressions. This particular `car_nodamage` program has no flake or
thin-film bindings. Its full normal construction, texture inputs, light and
environment bindings, damage, grading and complete BRDF remain separate work.
The live Godot paint shader is still an adaptation until the corresponding
source equations and inputs are integrated and checked in native captures.
