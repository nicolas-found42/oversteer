# Native speed challenge

The supported Xbox 360 image identifies `SpeedChallenge` as subtype 3 in the
string table at `824B0B28`. The image identity and matching recompiled source
commit are recorded in the handling recovery findings.

The recovered consumer is `sub_82131888`, in generated
`default/juiced2_recomp.64.cpp`. The retained extraction is
`artifacts/juiced2-build/native-speed/sub_82131888.cpp`.

The active subtype lives at configuration offset 24. While game state is 6
and the actor's race state at `actor+628+400` is unfinished, the consumer:

1. Computes the full three-dimensional velocity magnitude from native body
   fields 3716, 3720 and 3724. The target at active challenge context offset 8
   uses metres per second. The UI consumer `sub_822066A8` converts this value
   using native constants 2.235 for mph and 3.6 for km/h.
2. Reads whether the challenge was armed from controller offset 416. An
   unarmed challenge requires speed **strictly greater** than the target to
   set offsets 416 and 420 to 1.
3. Still in that previously-unarmed branch, checks controller timer 356
   against `f32(10.0)` at `8201FF90` (`41 20 00 00`). A timer greater than ten
   selects failure reason 5 and calls `sub_821DEB98`. Crossing the target for
   the first time after the deadline therefore still fails.
4. In the previously-armed branch, speed **strictly below** the target selects
   failure reason 4 and calls the same transition. Equality maintains an
   already-armed challenge, but does not initially arm it.

There is no five-second sustained-speed victory branch here. Normal lap
completion determines success when the monitor has armed without failure.
Supplementary vault footage `8wIC1vlEuP8` shows the target during an entire lap
and the result text “YOU MAINTAINED THE TARGET SPEED!” at 66 seconds. Its
platform is unconfirmed, so the native consumer establishes the rule; this
footage only corroborates the visible flow.

The core preserves the cached `was_armed` branch and covers its threshold and
deadline boundaries in the native mode fixture. The original upstream
simulation cadence remains a separate unresolved handling question.

Jev verified four claims with low confidence (0.20–0.34), requesting review.
The branch interpretation was independently read against the retained native
consumer by the primary agent and the core agent; the Jev result is retained
as advisory evidence, not an automatic acceptance.

## Address extraction caveat

Generated recompiler comments omit words belonging to inline switch jump
tables. Counting four bytes per comment from a procedure entry gives incorrect
addresses after such a table. Use `loc_` labels, call-return anchors and the raw
decoded section bytes to establish addresses. For example, the seven-word
table at `82206724` has its first case at `82206740`; the case is not located
at the table's beginning.
