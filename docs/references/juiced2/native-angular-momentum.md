# Native angular momentum and quaternion integration

The retained PowerPC assembly and recompiled C++ for `82265490`, `82265888`,
`82265FF8`, and `82308498` are in
`artifacts/juiced2-build/native-angular-momentum/`. This is a static source audit
of the supported Xbox 360 image, not an original executable runtime trace.

## State and coordinate frames

`82265888` copies Runge–Kutta state bytes 80/84/88 into body bytes
3668/3672/3676. These are **world angular momentum**, rather than body angular
velocity. The function normalizes the WXYZ quaternion at 3636/3640/3644/3648,
constructs rotation `R` at 3520, and computes the world inverse inertia tensor
at 3472 as `R * inverse_body_inertia * transpose(R)`.

It multiplies that tensor by angular momentum to obtain world angular velocity
at 3700/3704/3708. The inverse rotation at 3568 then produces body angular
velocity at 3732/3736/3740. `82265490` initializes inverse body inertia from the
reciprocals of mass parameter 220 times the respective 224/228/232 inertia
parameter times parameter 264.

## Derivatives

`82265FF8` clears body force at 3764/3768/3772 and body torque at
3780/3784/3788, then invokes the force callback through vtable byte offset 20.
After that callback, it transforms body torque by `R`, stores world torque at
3796/3800/3804, and copies it into derivative bytes 80/84/88. Thus the angular
Runge–Kutta channels integrate world momentum with world torque.

The matrix-vector expressions include affine translation terms, but
`82308498` explicitly writes zero to matrix byte offsets 12, 28, and 44. Those
terms therefore do not add a translation to the force or torque transform.

For normalized `q = (w,x,y,z)` and world angular velocity `(a,b,c)`, the
quaternion derivative is the world-angular-velocity premultiplication:

```text
dw = -0.5 * (x*a + y*b + z*c)
dx =  0.5 * (w*a + z*b - y*c)
dy =  0.5 * (w*b + x*c - z*a)
dz =  0.5 * (w*c + y*a - x*b)
```

PowerPC `fnmsubs` means the rounded fused expression `c - a*b`. Reading it as
`-(a*b+c)` changes signs in this derivation. The generated C++ independently
preserves the instruction's operand order.

## Reconstruction boundary

A body-angular-velocity integrator with a continuous Euler gyroscopic term is
not the same discrete state representation as these native Runge–Kutta
channels. The Rust port must carry world momentum through the stages and
derive angular velocity from each stage's normalized orientation and tensor.
Conversions at the external body-velocity boundary can introduce additional
rounding and are not evidence of bitwise parity with the PowerPC image.

The derivative function itself adds no separate explicit gyroscopic torque.
That observation does not establish the complete contents of its virtual force
callback. Native collision hull binding, all contact-query details, and the
original callback's remaining adjustments require their own evidence.

The supported XEX SHA256 is
`ae20f2467cc0535872b18517941ac4434f60408cb6d07bf47da799ce1564e574`;
the recompiled repository commit is
`cd5cb875673fa13b0654bed26869341ae30aab19`.
