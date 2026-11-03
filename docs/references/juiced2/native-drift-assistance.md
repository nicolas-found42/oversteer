# Native drift assistance and speed control

The recovered tyre and rigid-body equations are only part of the reference
game's handling. Static executable analysis also identifies additional vehicle
update routines that directly change linear and angular velocity. These are
original control behavior, not a justification for adding arbitrary forces to
make a reconstruction pass a score target.

## Separate update paths

The vehicle update `820F7290` tests the physics object's `4336` gear/state bits.
When those bits permit the update, vehicle field `156 == 1` calls `82114BD8`;
other values call `821151E8`. The former reads the actual input values at
bindings `284`, `288`, and `296`. The active-player-input predicate `82130CC0`
also requires vehicle field `156 == 1`. Together these support interpreting the
two paths as player and AI drift assistance. This role interpretation is a
static inference; no original-game execution has been observed.

Unmodified source and assembly are retained under
`artifacts/juiced2-build/native-ai/`. The AI routine is 1,924 assembly
instructions and reads the registered drift yaw, lookahead, curvature, and speed
settings. Its detailed strategy remains under reconstruction.

## The setters really alter authoritative velocity

`8226B8C8` copies the supplied vector into world linear velocity at
`3684/3688/3692`, transforms it through inverse basis `3568` to update local
velocity `3716/3720/3724`, and rewrites linear momentum
`3652/3656/3660 = world_velocity * mass`. The AI assistance routine calls it
with previous world velocity plus its calculated assistance delta.

`8226BA58` copies its argument into body angular velocity at
`3732/3736/3740`, updates world angular velocity `3700/3704/3708` through
basis `3520`, and updates angular momentum `3668/3672/3676`. Both assistance
paths call these setters. Merely porting wheel forces omits this layer.

## Native throttle demand

`82133FE0` takes target speed and reads local forward speed `3724`. Let
`e = forward_speed - target_speed`:

- When `e < -1`, demand is `clamp(e * -0.06666667014360428, 0, 1)`.
- When `e > 1`, demand is `-clamp(e * 0.10000000149011612, 0, 1)`.
- Otherwise demand is zero, including exact equality at either boundary.

The accelerating branch instead returns `-1` if forward speed is below `-1`
and actor field `244` is zero. That field's complete state meaning is not yet
recovered. The helper does not control speed using total velocity magnitude.

`8214EF08` supplies its controller's target speed at `+44` to this helper or
the alternative PID helper `821340A8`, clamps the returned demand by the
controller's limits, and marks the corresponding input component valid.
The PID helper's state starts at actor `+724`; its derivative input is the
previous controller component supplied in `f2`, not an assumed frame interval.

The drift-speed constructor `8213C660` multiplies the registered speed by the
literal float `0.44699999690055847` at `8204D1E4`. Thus the configured `200`
is approximately **200 mph / 89.4 m/s**, not 200 km/h. This conversion alone
does not justify imposing that target on every reconstructed driving policy.

## Remaining binding limits

The player routine reads globals `825A858C` and `825A8590`. Their decoded image
defaults and a bounded direct-reference search are retained in
`artifacts/juiced2-build/native-ai/drift-gates/defaults-and-search.json`.
There are no other direct reads, writes, or literal pointers to those globals
in that search. Indirect writes and register aliases remain unknown; image
defaults do not establish their values in a running original game.

Port the assistance's actual arithmetic and lifecycle, retain its frame and
coordinate conventions, and verify it independently of any driving controller.
Legal-input drift-score and career scenarios are still required after that
port. This finding is not evidence that those scenarios already pass.

Jev's retained verification accepted the velocity setter with probability
`0.97`; the speed-demand and dispatcher judgments remained flagged for review
(`0.56` and `0.81` support respectively). The implementation owner independently
read the speed-demand helper and added exact-boundary fixtures; the source
branch above was also manually checked. The model's judgments do not establish
original-game runtime behavior or completion of the assistance port.
