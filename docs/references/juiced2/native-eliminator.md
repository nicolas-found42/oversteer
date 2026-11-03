# Native Eliminator lap count and elimination

These are static observations from the recovered Xbox 360 executable, not a
recording of the original running game. The executable and generated-source
identity are recorded in [the recovery findings](../../../artifacts/juiced2-recovery/recompiled-handling/FINDINGS.md).
Retained unmodified functions are in
`artifacts/juiced2-build/native-eliminator/`.

## The event's stored lap count is replaced

`821DD5D8` adds a participant to the global table at the pointer loaded with
`lis -32179; lwz -3936`. Its records have a 128-byte stride, and field `+4`
is the participant count. At the end of the function, when configuration
field `24` equals `1` (Eliminator), it writes **participant count minus one**
to the current stage's signed 16-bit lap field:

```text
lwz r10,-3932(r10)       ; active configuration
lwz r9,24(r10)
cmpwi cr6,r9,1
bnelr cr6
lwz r11,4(r11)          ; participant count
lwz r9,4972(r10)        ; current stage index
addi r8,r11,-1
mulli r11,r9,612
add r11,r11,r10
sth r8,78(r11)          ; configuration + 76 + stage*612 + 2
```

The same override appears after participant removal and renumbering in
`821DD6A8`, during stage setup in `821DC928`, and when advancing a stage in
`821DBA48`. This is an override, not multiplication by the stored event lap
count. A five-driver Eliminator therefore needs four laps even if its raw
stage record says one lap.

## Elimination is checked during a racer's lap transition

`821370B8` increments the racer's field `376` when it processes a lap transition.
At `loc_82137684`, nonzero field `376` and mode `1` enter the elimination check.
It counts participant records whose field `12` is zero, then compares the
current racer's field `380` with that count minus one. If equal, it selects
that index from the vector reached through the racer's field `12` and calls
`821DEB98(stage, participant, 1, 0)`. A human participant also sets stage reason
`28` to `6` before that call.

Field `380` is **one-based position**. Initial rank assignment `8213A5D8`
starts at one; the regular update `8213A0E8` supplies rank start one to
`82139FF0`, which writes and increments it. Therefore this condition identifies
the **penultimate racer's** lap transition. Indexing the ordered vector with
that one-based position selects the **last other racer**, who is eliminated
before crossing. It does not remove the actor processing its own transition.
The rank writers and comparators are retained in
`artifacts/juiced2-build/native-ai/rank380/`.

At `loc_82137748`, the ordinary finish condition compares the racer's lap field
`376` with the lap goal at `racer[12][20]`. Eliminator additionally permits
finishing when the same participant-table scan finds exactly one active racer,
provided that participant's field `12` is zero.

`821363A0`, called by both racer update paths, is a separate watcher for marked
participants. It is not the source of the lap cadence or lap-count override.

## Reconstruction checks

Use the initial field size minus one as Eliminator's lap goal. Keep elimination
order and timing separate from that count. A focused fixture must show that a
five-driver event continues beyond the first lap and eliminates the last-place
racer when the penultimate racer crosses. With two racers left, the leader's
lap transition eliminates the remaining rival before finishing. Keep the
ordinary lap-goal finish branch as well as the one-active-racer branch. The
final legal-input scenario must also cover the corresponding career result.
A separate legal-input Rookie qualifier run now completes the five-driver,
four-lap career event in first place and promotes the earned profile. Its
[controls](../../../artifacts/juiced2-build/career-rookie-earned/career-native_28956449_000-controls.json),
[initial save](../../../artifacts/juiced2-build/career-rookie-earned/career-native_28956449_000-initial-save.json),
[result](../../../artifacts/juiced2-build/career-rookie-earned/career-native_28956449_000-final-snapshot.json)
and [driving log](../../../artifacts/juiced2-build/career-rookie-earned/career-rookie-qualifier-avoid.log)
are retained independently of the static source findings. The test uses the
reconstructed Easy option and an input-only policy that steers around physically
present eliminated contestants. It does not establish original AI trajectory or
inactive-car removal semantics; the reconstruction does not silently ghost those
bodies.

The rank-writer verification remains a manual-review finding: Jev returned
support `0.68` for one-based initialization and `0.51` for the vector-selection
consequence. Both were flagged for review. The implementation owner independently
checked the rank writers and corrected the five-driver fixture; these model
judgments are not acceptance of an entire race scenario.
