# Native script camera FOV units

Raw `CamFOV` script values cannot be passed directly to Godot's degree-valued
camera field. The recovered script-camera path scales those values by the
single-precision constant at `8204D8A4`, **0.008726389147341251**, before passing
them to the native projection object. That is approximately π/360, not π/180.
For an unadjusted explicit value of 80, this path produces a full vertical FOV
of approximately **39.99882148 degrees**.

## Binding chain

- Script parser `8208C2D8` stores the two `CamFOV` arguments at camera definition
  offsets 16 and 36. `820847C0` copies explicit start offset 16 directly into
  runtime offset 484. There is no factor of two in that copy.
- During updates, `82086738` blends runtime start 484 toward definition end 36
  through `820700A8`, using progress 480. It adds adjustments 1208 and 1120,
  multiplies by `8204D8A4`, and stores the result at runtime 488.
- The ordinary call passes that result to `822E9E58` with `r6 = 2` and the
  second FOV argument zero. The setter uses the first FOV for both axis fields
  when the second argument is zero. The native mode-11 branch applies another
  multiplier before the call; its context is separate from the unadjusted case.
- Projection builder `822E8580` uses reciprocal tangent of half the respective
  stored FOV to construct diagonal matrix entries 0 and 20. Its aspect mode 2
  replaces entry 0 with entry 20 divided by aspect, preserving vertical extent.
- The inherited-start branch in `820847C0` reads an existing renderer FOV and
  multiplies it by `8204D8A8`, **114.59494018554688**, when converting back to
  script units. This agrees with the forward conversion.

The tangent helper `8243AE28` reduces its argument by π/2 using multiplier
2/π and a high/low split of π/2, selecting a reciprocal branch by parity. It
does not double the input angle. The projection's half-angle constant at
`8201A8E4` is separately decoded as 0.5.

## Evidence and limits

The exact generated C++ and addressed PowerPC assembly are retained under
`artifacts/juiced2-recovery/recompiled-handling/physics-functions/` and
`physics-asm/`, named by the function addresses above. Decoded constants and
candidate/caller discovery are in
`artifacts/juiced2-build/presentation/projection-constants.json`,
`projection-fov-callers.json`, and `runtime-fov484-writers.json`.

This is a static interpretation of the supported Xbox 360 image, not a runtime
trace of the original game. It does not recover subject anchors, component
offset bases, camera travel/roll, FOV drift/trigger behavior, or scene placement.
Native camera constructors and other direct renderer callers can use other
aspect modes. Apply this conversion to the recovered **script-camera path**,
not every Godot camera or every native direct-renderer FOV.

Jev's four claims selected verified but all required review (confidence
0.35–0.79), retained in `projection-fov-jev.json`. The root read the full
assembly and decoded constants directly. The frontend owner independently
confirmed the explicit-start copy, update multiplier, ordinary half-angle
projection and mode-2 aspect branch before applying the script-only conversion.
This manual review resolves the interpretation; the probabilities alone do not.
