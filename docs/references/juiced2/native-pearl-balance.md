# Native pearl balance initializes to the normalized slider range

The paint editor's pearl balance setter uses a span at `8257D19C` and bias at
`824CE600`. Both are zero in the decoded disc snapshot, but that snapshot is
before C++ static initialization. Using its zero span as a live constant would
incorrectly flatten the control and make its inverse divide by zero.

Constructor `82474BB0` loads the float bias, subtracts it from the double **1.0**
at `8204D0F8`, rounds to binary32 and stores the result into the span. Its pointer
is present at `824A022C`, index 135 of the constructor table.

The entry function `xstart` calls `823D8398` at `823D8034`. On its successful
initialization path, that helper iterates four-byte pointers from `824A0010`
through `824A0B68` exclusive, skips zero and minus one, and calls each remaining
pointer. The pearl constructor is therefore in the startup path.

With the decoded initial bias **0**, startup produces span **1**. The original
setter's default expression `x * span + bias` consequently maps the normalized
slider directly to the exponent. This is a recovered initialized default;
later indirect changes to the globals were not established by this trace.

Reproduce the original-byte reads, pointer check, source hashes and retained
entry/constructor functions with
`python3 tools/game/assets/recover_pearl_balance.py`. Evidence is retained in
`artifacts/juiced2-build/presentation/pearl-balance-startup/`. This is static
execution-path evidence, not a trace of the original game running.

Jev marked both claim groups verified but flagged review at confidence 0.79 and
0.33. The frontend implementation owner independently checked the two source
functions, entry call, section hashes, exact pointer slot, bias and double
constant, agreeing with the initialized-default conclusion. The model result
alone did not establish it.
