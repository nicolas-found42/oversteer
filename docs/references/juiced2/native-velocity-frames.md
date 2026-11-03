# Native velocity frames

The recompiled Xbox 360 source distinguishes world velocity at vehicle offsets
3684/3688/3692 from body-local velocity at 3716/3720/3724.

This follows the data flow, rather than a guessed field name:

1. `sub_82265888` reads linear momentum 3652/3656/3660, multiplies by inverse
   mass 3616, and writes 3684/3688/3692.
2. `sub_82265FF8` copies 3684/3688/3692 directly into the position derivative
   channels 48/52/56. These are the world-position derivatives.
3. `sub_82265888` constructs the inverse rotation at 3568 by transposing the
   3×3 matrix at 3520. It then transforms 3684/3688/3692 through that inverse
   into 3716/3720/3724.
4. After the integration, `sub_82260778` calls the native atan2 helper with
   3716 and 3724 and stores drift angle at 4320. The lateral/forward angle
   therefore uses body-local velocity.
5. The `3724 > 10` coasting branch in `sub_8225F530` refers to body-forward
   motion. Using world Z would make clutch engagement depend on track heading.

The two velocity vectors have the same norm under an orthonormal rotation.
Consequently the recovered scalar speed checks and drift score speed magnitude
do not gain a mass multiplier or another unit conversion from this distinction.

These are static findings from the supported XEX SHA256
`ae20f2467cc0535872b18517941ac4434f60408cb6d07bf47da799ce1564e574` and recompiled
repository commit `cd5cb875673fa13b0654bed26869341ae30aab19`. Exact extracted
functions are retained in
`artifacts/juiced2-recovery/recompiled-handling/physics-functions/`. Original
runtime execution has not been observed. The root and core owner independently
traced the field use; an earlier working note that called 3684 local was
incorrect and is superseded by this data flow.
