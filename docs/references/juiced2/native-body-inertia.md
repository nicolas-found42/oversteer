# Native body inertia

`sub_82263BB8` calculates the default diagonal inertia per unit mass from source
shape dimensions. It uses the first shape from the parameter object's list at
76/80. When the automatic flag at parameter offset 240 is nonzero, it reads
shape dimensions 160/164/168, multiplies each by the float at `0x8202F7C8`
(`0.009999999776482582`), and writes:

```text
parameter[224] = (height² + length²) * 0.0833333358168602
parameter[228] = (width² + length²)  * 0.0833333358168602
parameter[232] = (height² + width²)  * 0.0833333358168602
```

The coefficient is the original float at `0x8204D500`, approximately 1/12.
`sub_82265490` multiplies those values by parameter mass 220 and scalar 264,
then takes reciprocals to produce the inverse diagonal at 3424/3444/3464.
Zero products produce zero inverse values. `sub_82262FE0` initializes automatic
flag 240 to one and scalar 264 to one. Explicit parsers `sub_82264300` and
`sub_82264468` can supply inertia components and their scalar.

This is a full body shape calculation. Substituting wheelbase and track width
for body length and width understates the rotational inertia. Applying the
native box equation to accepted donor body dimensions is a donor adaptation;
it must be recorded as such rather than presented as the original reference
car's exact mass distribution. Actual donor dimensions already retained with
the accepted roster are preferable to tuning inertia solely to make a driving
fixture pass.

Static source identity: supported XEX SHA256
`ae20f2467cc0535872b18517941ac4434f60408cb6d07bf47da799ce1564e574`, recompiled
repository commit `cd5cb875673fa13b0654bed26869341ae30aab19`. Exact functions and
decoded big-endian constants are under
`artifacts/juiced2-recovery/recompiled-handling/`. No original runtime trace is
claimed. The core owner independently confirmed the consumer and is checking
the parameter bindings and coupled driving scenarios.

Jev's two checks selected verified but required review at confidence 0.70.
They are retained in `artifacts/juiced2-build/native-tyre-force/inertia-jev.json`
and do not automatically establish parity or validate a driving scenario.
