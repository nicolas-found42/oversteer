# Native drift multiplier audit

`sub_821143C0`, called by the drift update `sub_82113648`, writes the per-racer
score multiplier at offset 132. The scoring helper `sub_82113CF8` consumes it.
The raw source and decoded constants are retained in
`artifacts/juiced2-build/native-drift-audit/`.

## Participant role gate

In native modes 11 and 12 the function gets the racer slot's definition pointer
from the array at global `lis -32179; lwz -3916`, with 120-byte entries and a
pointer at entry offset 12. It checks bit zero of the byte at definition offset
36. A set bit yields multiplier one. A clear bit enters the adjustment branch.

Independent source review by the root and core owner strongly identifies this
as the human participant flag:

- `sub_8221C540` copies the active career profile into its current slot and
  sets that bit with `oris ...,256` on the big-endian word at 36. It then
  initializes the named `CrewMate0`, `CrewMate1` and `CrewMate2` records without
  that flag operation.
- `sub_82167678` sets it for participant role 1 and clears it for other roles
  while constructing the race grid.
- `sub_8222D418` copies a participant into a later slot and clears the same bit
  with `rlwinm ...,0,8,6`.

Consequently mode 11's multiplier ten belongs to the AI adjustment branch;
it must not be assigned to the human player merely to satisfy a score target.
This role meaning is a strong static inference, not an observed original runtime
trace. Mode 9 Endurance follows the ordinary multiplier-one branch.

## Mode 12: Drift King

The human branch remains one. For an AI participant, the source forms a ratio
using total points (live 92 plus banked 124), the first human participant's
total, and the AI's one-based score rank at race-info offset 380:

```text
rank_factor = fma(float32(score_rank - 1), float32(0.2), float32(1))
ratio = float32(float32(first_human_total / rank_factor) / self_total)
ratio = 1 when self_total is zero
```

The source performs two single-precision divisions in that order. Combining
their denominators is algebraically equivalent over real numbers but can change
the recorded single-precision result.

`821143C0` calls `821DD510` with `r4 = 0`. That helper scans 128-byte participant
records for role value one and returns the requested human ordinal's record;
the multiplier then follows record 44 to actor 636 for the reference score.
Thus a maximum over AI scores would change this rubber-banding equation.
`8213A5D8` selects the `82139D70` score comparator in native mode 12, sorts the
participants, and stores sequential integers starting at **one** in 380 and
396. These source functions are retained under
`artifacts/juiced2-build/native-eliminator/race-manager/` and
`artifacts/juiced2-build/native-ai/rank380/`. This resolves the earlier rank/skill
uncertainty and corrects the earlier description of a leading-score reference.

The source multiplies this ratio by one of the following values, indexed by the
current profile's field zero, and clamps the result to `[0.2, 10]`:

| Profile field zero | Ratio > 1 | Ratio ≤ 1 |
| --- | ---: | ---: |
| default | 1.1 | 0.1 |
| 1 | 1.15 | 0.2 |
| 2 | 1.2 | 0.3 |
| 3 | 1.25 | 0.4 |
| 4 | 1.3 | 0.5 |
| 5 | 1.3 | 0.6 |
| 6 | 1.3 | 0.7 |
| 7 | 1.3 | 0.8 |
| 8–9 | 1.35 | 0.8 |

The profile field is consistent with the league index, but that binding must
remain explicit. A configuration field at offset 36 equal to two, or the branch
with game-state field 1048 equal to zero and 964 unequal to one, instead uses
base 2.5. The exact meanings of those configuration/state fields are unresolved.
Their branches must not be silently equated with difficulty or quick race.

## Mode 10: Twin Drift

For one specifically selected actor pair, the function reads each race-info
float at offset 164 and computes:

```text
d = sqrt(3) * abs(a164 - b164)
x = clamp(d * 0.01 - 5, 0, 100)
multiplier = 0.5 + 1.5 * ((100 - x) * 0.01)^3
multiplier = 2 when a164 > b164
```

The repeated scalar difference in all three squared terms is present in the
source; it is not a recovered three-dimensional distance. Offset 164 appears
to be course progress. Its units and the selected actor ordering still need
binding before this equation can safely drive the reconstruction. Other
participants take the ordinary multiplier-one path.

This audit narrows the remaining work; it does not claim that every adjustment
is implemented. Original bonus flag 104, contact retention inputs and these
unbound caller fields remain separate evidence questions. The supported XEX
SHA256 is `ae20f2467cc0535872b18517941ac4434f60408cb6d07bf47da799ce1564e574`;
the recompiled repository commit is `cd5cb875673fa13b0654bed26869341ae30aab19`.

Jev's first partial-excerpt check is retained in `jev-role-gate.json` in the
audit directory. It marked the numeric role-branch claim unsupported and both
claims review-required. That request did not include the decoded constants.
The numeric values above come from the separately retained big-endian constant
reads and the independent branch reviews, not automatic model acceptance.

The rank/reference follow-up is retained in
`artifacts/juiced2-build/native-ai/rank380/jev-king-reference.json`. The rank
claim selected verified with 0.91 support and automatic acceptance; the
first-human reference claim selected verified with 0.50 support and required
review (confidence 0.25). Root and the core owner independently traced the
selector's ordinal-zero scan and the scoring-pointer dereference. This manual
review resolves the source interpretation; the probabilistic result alone does
not establish it.
