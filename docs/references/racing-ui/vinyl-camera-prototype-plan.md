# V088 bounded workshop-camera prototype

Question: do side, rear or high-oblique views materially improve inspection of an actual installed decal over the current vinyl camera? This is a throwaway observer experiment, not a projection system or production camera change.

Run only after the root agent releases the shared native runtime:

`uv run --frozen python tools/game/verify_ui_hud_vinyl_camera_prototype.py --output build/verification/ui-hud/reference-vinyl-camera`

Budget: **four PNGs total**, no incidental/final captures. New isolated save/settings; existing background-window guard; native Metal and normal render cadence. No forced rendering, frame stepping, gameplay camera, physics or scoring changes. Runtime timeout120s. Wrapper rejects runtime errors, missing guard, failed checks or any image inventory other than the four named views.

The observer enters Career → Garage → Customization, adds one existing catalogue decal, buys it through the actual isolated checkout/confirmation flow, returns to Vinyl and asserts that the owned car's installed customization contains a vinyl. This distinguishes actual installed artwork from a fake screenshot overlay or an uncommitted shader mockup.

Exact preview root comes from `reference-stage-navigation/main-preview.json`: `Showroom model — static wheels`. The Civic GLB JSON scene name independently confirms it; actual selected model is `res://assets/cars/GT4_HOND0018.glb`. The camera is the viewport's actual current Camera3D. Failure to resolve either is a failed prototype, not a guessed node fallback.

View0 captures unmodified production composition. Views1–3 change only this workshop camera in `RenderingServer.frame_pre_draw` after ordinary app processing: side, rear, high-oblique. Directions are transformed by the actual preview basis, using actual visible mesh corners and the existing1336×752 protected stage at536,224 with48px inner padding. The fitting loop mirrors existing `fit_preview` rather than inventing surface projection; model transform and installed game snapshot must remain unchanged across every view. Each view records camera/preview paths, transforms, FOV, offsets and projected mesh corners in `vinyl-camera.json`.

No surface-target metadata is asserted. Comparing the four stills can establish useful inspection angles for this car/decal only; it cannot establish full decal placement, all-car framing, animation quality or recovered projection rules. Host visual inspection plus screened/audited transcripts will make the keep/omit recommendation after the authorized run.

Preparation checks: Python syntax compilation, Ruff formatting/check. Native launch deliberately deferred until runtime release; GDScript/native execution is not yet verified.
