# Native NOS pressure, force, drain and recharge

The native NOS update adds a **BODY +Z external force**. A flat engine-torque
multiplier is insufficient to reproduce it. These findings come from static
translated PowerPC and decoded executable bytes, not an original-game runtime
trace. Reproduce the retained contract with
`python3 tools/game/assets/recover_native_nitrous.py`.

The contract and unmodified functions are retained in
`artifacts/juiced2-build/native-nitrous/`. Each decoded scalar records its exact
binary32 bits, section hash and `lis`/`addi`/`lfs` address operands. In particular,
the capacity default is **5**, the override sentinel is **−2**, and the autonomous
recharge coefficient is **25**. Earlier provisional hand calculations of those
constants were wrong; the generated operand calculation supersedes them.

## Force and bottle pressure

`820F69F8` snapshots current bottle quantity into car offset 112 when NOS becomes
active. `820F82D0` divides that activation snapshot by capacity at vehicle offset
4304. It selects these exact binary32 constants using strict comparisons:

| Activation quantity / capacity | Pressure factor |
| --- | --- |
| Exactly 1 | 1.4 |
| Greater than 0.66 | 1 |
| Greater than 0.33 | 0.7 |
| Otherwise | 0.3 |

The current quantity falling during the same blast does not select a lower
pressure band. A new activation takes a new snapshot.

The additional force requires NOS enabled at car offset 96, the active flag
`00400000` in vehicle offset 4336, positive bottle quantity, more than one contact
wheel at car offset 528, and an encoded physical gear other than zero or one.
Those gear values must be mapped to the core's own forward/reverse convention.
With those gates satisfied, ordered single-precision operations compute:

```text
throttlePressure = vehicle[4236] * pressureFactor
scaled = tuningPower * throttlePressure
externalBodyForce.z += scaled * 13600
```

`tuningPower` comes from `821064C8(global[132], car[684], 0)`; it is a package
factor, not a guessed multiplier per upgrade stage. `13600` is the decoded
initial value at `824CBEB0`. Its original runtime mutability remains separate
from observing the instruction that reads it.

The core implementation owner independently traced `8225EB58` → `82266218`:
the latter copies vehicle 3812/3816/3820 directly to BODY force 3764/3768/3772.
`82265FF8` rotates that force by the body's rotation into the WORLD momentum
derivative. No extra mass or timestep multiplication belongs in this force-copy
step. The external force persists through intermediate integration stages and
is cleared by `8226B088`; the original game/world update order needs preserving
or an explicit reconstruction policy.

## Capacity and drain

`8225DB98` parses two `Nitro` floats: multiplier at parameter 416 and capacity at
420/424. None of the 93 retained filename-bound stock profiles contains that
row. The live spawn path additionally calls `8210D0E8`, which writes multiplier
1 and the following capacity:

```text
car[9640] == -2 ? 5 : fma(car[9640], 3, 2)
```

The car-instance constructor `82109860` initializes this control to 0.5, so the
ordinary constructed car obtains **3.5 units**, rather than taking the sentinel
fallback of 5. Copy constructors preserve the field; `8210B510` and `8210B058`
stream it as four bytes after the preceding field at 9636. The original UI
setter/range remains unresolved.
`8225FDE0` initializes current quantity 4300 and capacity 4304 from parameters
420/424, and drain rate 4308 to 0.4. Additional reset/start calls can clear the
current quantity, so construction alone does not prove a race starts full.

`82260108` drains an active bottle with
`max(0, fma(-rate, dt, quantity))` before integration. `8225E3B8` separately applies
parameter 416 to engine torque only when the active flag and positive quantity
remain. That path does not replace the external-force path.

## Recharge metric and timing

`8226DA48` retains the full residual contact velocity after subtracting wheel
surface velocity. In `82111E50`, a contact wheel with point speed greater than
4 computes `clamp(abs(residual.x * (1 / pointSpeed)), 0, 1)`, with the reciprocal
rounded before multiplication; lower speeds produce zero.
This is not the vehicle's body slip angle.

The wheel helper adds the ratio to its owner car offset 512. Its caller
`820F5480` adds the same wheel's stored ratio again, for all four wheels, then
multiplies the result by 0.25. The independently reviewed consequence is
`metric = 0.5 * sum(four wheel ratios)`, with a possible range of zero through
two. Removing the double accumulation would change the recovered behavior.

When that metric exceeds 0.2, NOS is inactive and the bottle is below capacity,
the recharge timer accumulates. Only after it exceeds 0.3 does the update use:

```text
coefficient = controlMode156 == 2 ? 25 : 12
quantity = min(capacity, fma((metric * coefficient) * dt, 0.04, quantity))
```

Control mode 156 is distinct from drift field 788. The existing control audit
binds mode 1 to active human control and mode 2 to autonomous/common control;
it does not mean normal driving versus drifting.

The additional branch gated by active race configuration offset 12 and inactive
NOS adds `min(globalDelta, 0.06666667) * 0.3`, capped at capacity. The separate
native-performance contract binds contest parser offset 48 through its stored
payload and embedded configuration to this offset: it is the Extreme NOS flag.
Normal recharge and this extra branch can both apply in a frame.

The original bottle customization writer, accepted-donor tuning adaptation,
remaining activation eligibility and original world scheduler are explicit
boundaries. This source contract is not a claim that the current runtime has
already ported all these behaviors.
