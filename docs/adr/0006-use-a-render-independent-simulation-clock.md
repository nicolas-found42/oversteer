# Use a render-independent simulation clock

The reconstruction runs its authoritative Rust game simulation at 60 outer ticks
per second, independently of Godot's rendering rate. `Game::advance` accumulates
elapsed time and consumes complete ticks; incoming elapsed time retains the
existing native 0.2-second cap. Pausing does not accumulate gameplay time.

This is an **explicit reconstruction policy**, not a claim that the original
game used a fixed 60 Hz upstream clock. That original clock has not been
recovered. The original scheduler, numerical helper equations and nonlinear
vehicle stage commits remain inside the authoritative tick.

The policy is needed because the recovered drift scoring helper contains a
quadratic frame-interval term. Calling it once per render frame would change
points and career outcomes between a 60 Hz and 120 Hz display. Rendering
performance must not determine gameplay progress. Input recordings and headless
driving/career scenarios also need a stable simulation clock.

Keep the direct native helper cadence fixture: it characterizes the recovered
equation's dependence on its caller. Separately verify that `Game::advance`
produces the same gameplay results for equivalent input/time streams delivered
at 30, 60 and 120 Hz. The agreed rendering acceptance remains actual 1920×1080 at
60 FPS on the current M5 Pro; this clock choice does not establish that measured
performance result.
