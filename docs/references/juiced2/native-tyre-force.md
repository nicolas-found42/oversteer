# Native tyre force composition

The Xbox 360 recompiled source for `sub_8226DA48` composes its nonlinear tyre
force and residual sliding force without a final component-wise `load * mu`
clamp. This is a static source finding; the original game has not been executed
under instrumentation.

The source is retained in
`artifacts/juiced2-recovery/recompiled-handling/physics-functions/8226DA48.cpp`,
from the supported XEX SHA256
`ae20f2467cc0535872b18517941ac4434f60408cb6d07bf47da799ce1564e574` and recompiled
repository commit `cd5cb875673fa13b0654bed26869341ae30aab19`.

After calling `sub_8226D6F8` at `0x8226DBFC`, the function:

- Optionally scales both stored forces at wheel offsets 392 and 396 by
  `1 - wheel[44] * wheel[404]` when field 404 is positive. The runtime writer and
  full meaning of field 404 remain unresolved; it must not be assumed to mean
  handbrake grip.
- At `loc_8226DC34`, compares saturation field 364 with the global threshold at
  `r29 + 8`. Above that threshold, the throttle-dependent factor
  `1 - (1 - global[r29 + 4]) * wheel[44]` scales force 392.
- At `loc_8226DC60`, projects forces 392 and 396 along the two contact basis
  vectors at 320–328 and 304–312, multiplies by blend field 400, and adds or
  subtracts the result according to the sign of wheel angular velocity at 20.
- At `loc_8226DCF8`, forms residual velocity as contact velocity at 344–352
  minus the first contact basis times `wheel[20] * rolling_radius[300]`.
  When blend 400 is below one, the function adds an opposing residual-vector
  contribution scaled by the native lookup, load 200, coefficient 60, the
  global scalar and `1 - blend`.

The function then returns at `loc_8226DDF8`. There is no subsequent final
component clamp inside this function. A reconstruction clamp after these
operations would override the recovered cornering scalar and can change
cornering limits and drift initiation. Internal nonlinear saturation and
the native blend still apply; removing a reconstruction clamp does not mean
discarding those native limits.

## Contact blend

Field 400 is written inside `sub_8226DA48`. Its ordinary-contact value is the
product of three factors, using original big-endian float constants:

```text
A = (clamp(contact_speed[360], 3, 5) - 3) * 0.5
B = 1 - (clamp(abs(slip_angle[336]), 1, 1.2000000476837158) - 1)
        * 4.999999046325684
C = (clamp(longitudinal_slip[384], -0.8999999761581421, -0.6000000238418579)
        + 0.8999999761581421) * 3.333333969116211
blend = A * B * C
```

Positive field 404 forces the intermediate blend to one. A positive blend is
then multiplied by `(wheel[76] - 0.800000011920929) * 5` when wheel[76] exceeds
that threshold; otherwise it becomes zero. Earlier contact gates require a
positive load 200, positive body-space axis Y at 92 and world-space axis Y at 76 of at
least `0.10000000149011612`.

`sub_8226DF90` calls `sub_82260970` with `wheel + 52`. That routine transforms
the world contact normal at its offsets 20/24/28 through the body's inverse
basis at 3568 into body-space offsets 36/40/44. Thus wheel 72/76/80 is the
**world** normal and wheel 88/92/96 is the **body-space** normal. An earlier
reading of this note reversed these frames; the inverse-basis consumer resolves
the direction.

`sub_8225BFF0` computes the body-space contact-point velocity, including the
angular-velocity cross product with the contact arm. Wheel 136/140/144 stores
that velocity and wheel 172 stores its dot product with the body-space contact
normal. `sub_8226D940` uses this normal velocity in the suspension damper and
returns force along the body-space normal. Absolute world vertical velocity is
not an equivalent input on a slope.

During integration stages, `sub_82260970` updates wheel compression 176 by
subtracting `dot(world_normal, new_world_point - old_world_point)`. This retains
the sampled contact plane. A frozen contact height with a changing world X/Z
would instead change compression during motion tangent to a sloped road. The
reconstruction now retains the sampled plane's X/Z anchor and normal for this
calculation. The focused tangent-motion fixture and all-course traversal remain
separate checks; correcting the source equation alone does not establish every
course's drivability.

`sub_8226DE08` writes contact speed 360 and contact angle 336.
`sub_8226D4E0` computes longitudinal slip from absolute wheel speed, rolling
radius, contact speed and the cosine of that angle. Beyond its angle gate,
the original sentinel is **100**, read at `0x8204CB08`; it is not minus one.

This finding does not establish full vehicle parity. Contact geometry, rolling
radius, suspension, untraced runtime fields and the original upstream clock
remain separate evidence questions. Sustained drift and original career score
targets require legal-input runtime scenarios after this correction.

Jev's two source checks are retained in
`artifacts/juiced2-build/native-tyre-force/jev-verification.json`. Both selected
verified with review required (confidence 0.24 and 0.64). They are not automatic
acceptance; the branch and arithmetic reading above is the independent source
review. The core owner also independently identified the reconstruction clamp.

The contact-frame follow-up is retained in
`artifacts/juiced2-build/native-tyre-force/jev-contact-plane.json`. Jev selected
verified for the normal-frame and damper-input claims, and unsupported for the
plane-compression claim; all three required review (confidence 0.58, 0.66 and
0.26). Independent source review resolves the arithmetic directly: in
`82260970`, `f11/f10/f9` hold the new-minus-old world-point components, the
`fmuls/fmadds` chain contracts them with offsets 20/24/28, and `fsubs` subtracts
that scalar from offset 124. The call's `wheel + 52` maps 124 to wheel 176.
The `8225BFF0` final dot product writes offset 120, mapping to wheel 172.
These are independently reviewed static facts, not automatic model acceptance
or an original-game runtime trace.
