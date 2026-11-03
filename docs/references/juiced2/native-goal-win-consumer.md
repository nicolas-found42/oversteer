# Native WinRace and PlaceInRace goal consumers

The Rookie qualifier's recovered description says “Place 3rd or higher in an
Eliminator Race,” while its executable script explicitly selects `Type WinRace`
with no placement argument. This inconsistency is preserved in
[leagues.json](../../../data/juiced2/leagues.json). The reconstruction does not
replace that executable goal type using its descriptive text.

These findings are static observations of the recovered Xbox 360 executable.
They do not establish how every original stage-result producer handles a
qualifier. The executable identity is in the
[recovery findings](../../../artifacts/juiced2-recovery/recompiled-handling/FINDINGS.md).
Unmodified generated functions and a content-hash manifest are retained in
`artifacts/juiced2-build/native-goal-win/`.

The type table at `824AF8EC` contains thirteen pointers. Entry zero points to
`82042C30` (`WinRace`), and entry one points to `82042C24` (`PlaceInRace`). Parser
`8221F410` writes the selected index to definition offset 20, with offsets 24
and 28 initially zero. For `PlaceInRace`, it stores the parsed ordinal minus
one at offset 24. `WinRace` does not parse an ordinal through that branch.

The `ClassQualifier` callback `8221FB60` only sets bit `01000000` at definition
offset 48. End-goal callback `8221FA80` copies 52 bytes from definition offset
16 to the goal collection. Neither function changes `WinRace` to
`PlaceInRace` or inserts a top-three threshold.

Evaluator `82220990` dispatches type zero to `82221378` and type one to
`82221618`. In the ordinary contest branch, `82221378` requires a completed
stage at stage offset 396. Modes 8 and 9 compare the stage score at offset
420 against the target obtained from the active contest. For other ordinary
modes, the relevant branches compare the stage winner byte at offset 400
with the participant identifier at offset 4 returned by `821DD510(table, 0)`.
The function does not inspect the qualifier flag to accept a third-place
ordinal. Its championship branch separately requires `821DE748` to return
zero.

`82221618` instead reads the stored zero-based placement threshold from goal
offset 8. Its ordinary contest branch loops result indices from zero through
that threshold, checking the participant identifier in the corresponding
completed result records. Its championship branch accepts a returned ordinal
less than or equal to that threshold. These are distinct executable paths.

This bounded trace supports keeping the executable `WinRace` predicate. It
does not prove that an upstream original qualifier result producer never
records a qualifying driver as a winner. That producer remains an unresolved
boundary; changing third-place promotion requires tracing it or observing the
original runtime. The reconstructed legal-input career proof won this Rookie
qualifier in first place, so it does not resolve the third-place discrepancy.

The generated C++ `loc_...` labels identify switch destinations. The convenience
ASM extractor counts instruction comments and can mislabel addresses after
jump-table metadata; those synthetic line addresses must not override the
generated destination labels.

Jev marked all four bounded claim groups verified, with confidence 0.49–0.61
and review required. The core implementation owner independently checked the
decoded type pointers and all six parser/dispatch/consumer functions, agreeing
with these bounded findings. The retained model result is advisory; it does not
resolve the upstream producer boundary or the original third-place behavior.
