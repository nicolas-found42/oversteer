# Juiced 2 visual research vault

Collected on November 3, 2026 for the Oversteer reconstruction investigation.
This page records the reference collection, made before the rebuild interview.
The approved implementation is documented in [the game guide](../../game/README.md)
and [the Godot/Rust decision](../../adr/0005-use-godot-and-rust.md).

Original code findings are recorded separately:

- [Speed Challenge boundaries](native-speed-challenge.md)
- [Tyre force composition and blend](native-tyre-force.md)
- [Angular momentum and quaternion integration](native-angular-momentum.md)
- [Script camera FOV units](native-script-camera-fov.md)
- [Velocity coordinate frames](native-velocity-frames.md)
- [Body shape inertia](native-body-inertia.md)
- [Drift multiplier role gates and remaining bindings](native-drift-multipliers.md)
- [Eliminator lap override and elimination conditions](native-eliminator.md)
- [Native drift assistance and speed control](native-drift-assistance.md)
- [NOS capacity, pressure, external force and refill](native-nitrous.md)
- [Career win-goal consumer and qualifier boundary](native-goal-win-consumer.md)
- [Initialized pearl-balance control](native-pearl-balance.md)
- [Original two-color and reflection shader kernels](native-paint-shader-kernels.md)
- [Collision query stack and evidence boundary](collision-query-stack.md)

## Open the vault

- [Local browser](../../../artifacts/juiced2-vault/index.html)
- [All assets and original source timestamps](../../../artifacts/juiced2-vault/assets.json)
- [Video sources](sources.json) and [standalone screenshot sources](screenshots.json)
- [Contact sheets](../../../artifacts/juiced2-vault/contact-sheets/index.json)
- [Taxonomy decision ledger](../../../artifacts/juiced2-vault/judgments/taxonomy-v2/README.md)
- [Classification coverage and reported usage](../../../artifacts/juiced2-vault/judgments/usage.json)
- [Structural validation](../../../artifacts/juiced2-vault/validation.json)

The media and generated judgments live under the repository's existing ignored
`artifacts/` root. The source indexes and collection/classification tools are repository
inputs; a fresh checkout does not contain the downloaded media. Nothing was published.

## Collection

The current collection contains 36 unique videos totaling 11 hours 41 minutes 59 seconds,
76 unique standalone press screenshots, and 16,363 timestamped frame records.
Together these make 16,439 asset records. Exact duplicate imagery can occur at different
timestamps: 16,431 image files have 16,403 distinct SHA-256 values. Retaining those
contexts avoids silently losing where a repeated menu or black transition occurred.

The last expansion doubled videos from 18 to 36 and screenshots from 38 to 76. Frame
sampling increased from 2,239 to 16,363 records, rather than merely doubling it.

Each video has a SHA-256 digest, byte count, `ffprobe` metadata, uploader, public URL,
declared platform, available chapters, and capture caveats. PC, Xbox 360, PS3, PS2,
and PSP references remain distinct. Emulator overlays, inferred edits, low source
resolution, unconfirmed modifications, and omitted challenges are not erased.
Promotional stills may represent prerelease presentation; they do not prove shipped
gameplay behavior. Uploader titles such as “100%” do not establish exhaustive coverage.

## Sampling

The dense pass selects approximately one source frame every three seconds. Additional
scene-change frames and focused sequences retain smaller interactions, including
vinyl manipulation, wager selection, spooking notifications, drift chaining, crew DNA,
and customization controls. Earlier frames are preserved. Sampling records contain
actual decoded presentation timestamps, not invented frame numbers.

The original recordings retain their full temporal context and audio. Samples are
an index into those recordings, not a substitute for watching a transition. Source
recordings were acquired at up to 720p, with 480p used for longer recordings; some
uploads themselves have much lower resolution. This limits readable minute detail.

## Jev taxonomy and placement

The active [catalog](../../../tools/references/jev_catalog_v2.py) contains 17 domains,
247 candidate screen states, 249 independent visible-detail tags, seven facets,
three score dimensions, and 12 localization regions. Catalog membership is not a
claim that a feature exists in the game or has been observed in this collection.

Jev assessed all 251 proposed screen candidates and all 249 tag candidates in batches.
Four screen candidates were demoted or rejected, with their relevant attribute or
fallback coverage retained. Independent visibility/hidden-fact checks supported 229
of the 247 retained definitions at the recorded thresholds; 18 remain conditional.
The earlier overlapping suitability classification had substantial uncertainty;
its raw judgments remain in the ledger and are not represented as blanket approval.

The classifier uses pinned `typesafe/jev-1.14` through the configured OpenRouter
Decisions endpoint. It sends public reference images, catalog questions, and the
previous frame when appropriate. It does not send private game source or save keys.

1. **Choice** selects a broad domain, then a finer screen state within that domain.
   If routing is uncertain, a plausible second domain is also examined and retained.
2. **Noul** judges overlapping visible details independently. Common details and
   domain-specific details are evaluated separately. An unasked tag is not a negative.
3. **Score** retains distributions for readability, interaction detail, and obstruction.
4. **Box**, paired with a presence Noul, locates controls and HUD regions. Absent region
   outputs are discarded; uncertain boxes remain proposed and never become ground truth.
5. Adjacent recorded frames within six seconds are compared for screen, selection,
   car appearance, score, and notification changes. These observations do not establish
   control inputs, causation, physical velocity, or hidden scoring rules.

Exact compressed requests, responses, input hashes, image preparation, probabilities,
and stage dependencies are saved. Choice acceptance requires a top probability of at
least 0.85 and margin of at least 0.5. Noul values at least 0.8 indicate visible evidence;
values between 0.2 and 0.8 remain unresolved. Text-dependent positives remain proposed
when the readability distribution indicates only large headings or less are readable.

Jev's image and Box support is experimental. Tiny source images are enlarged only to
meet transport dimensions; that does not create missing detail. Coordinates refer to
the submitted image. Still-image tags describing sliding or countersteer are appearance
judgments, not verified dynamics. An unlock notification outside the career/crew route
can currently escape its domain-specific tag; consult the image and screen category.

See the primary [TypeSafe image documentation](https://docs.typesafe.ai/images.md) and
[question primitives](https://docs.typesafe.ai/primitives.md). The exact documentation
used during this run is retained in the local vault metadata.

## Classification status and reproduction

All 16,439 images now have completed Jev records, with zero pending records and zero
request errors. Every record retains broad-domain and detailed judgments, three score
distributions, evaluated visible-detail tags, and presence-gated region results.
There are 16,327 adjacent-frame comparisons and 83,724 retained region proposals.

Processing completion does not make uncertain labels certain: 13,997 screen labels
remain flagged for review. The browser retains the underlying probabilities, alternate
domains, readability gates, and unresolved regions. Empty category pages remain evidence
gaps; they do not prove that a feature is absent from the game.

Earlier credit failures and six request timeouts were resolved by resuming from cached
stages. The resume queue is now empty. The final resume reported $1.18 in new provider
calls; completed v2 records collectively report $13.34. These figures do not include
all earlier taxonomy work, superseded passes, or incomplete-stage calls.

[Resume queue](../../../artifacts/juiced2-vault/judgments/v2/resume-queue.json) and
[completion checks](../../../artifacts/juiced2-vault/metadata/classification-completion-checks.json)
record the completed state. Matching cached stages can be aggregated without contacting
the provider:

```sh
python3 tools/references/classify_vault_v2.py --offline --workers 16
python3 tools/references/vault_media.py build
```

For newly added images, use the provider-backed command:

```sh
python3 tools/references/classify_vault_v2.py --workers 16 --cost-cap 20
python3 tools/references/vault_media.py build
```

API failures are never converted into semantic answers. A credit failure stops new paid
requests for that run. Raw stages preserve the exact request, response, source hashes,
and model identity; the summary usage covers completed image records.

## Verification boundary

Structural validation checks asset identities, files, hashes, dimensions, timestamps,
source references, raw judgment links, and exact contact-sheet coverage. Browser checks
exercise filters and JavaScript execution. These checks do not establish the semantic
accuracy of every machine label. Final claim verification is recorded separately in
[the verification result](../../../artifacts/juiced2-vault/judgments/final-claims-verification.json).
Jev verified all five completion claims but its advisory patch gate escalated on low
confidence. [Primary-agent review](../../../artifacts/juiced2-vault/judgments/final-review-resolution.json)
records the direct code inspection and executed checks; no automatic gate approval is asserted.
Physics constants, AI decisions, exact timing, score
formulas, complete feature coverage, and undocumented platform differences remain open.

The prior REA evidence records a controlled metadata-acquisition process, not execution
of Juiced 2: [REA evidence](../../../artifacts/juiced2-vault/judgments/rea-acquisition.json),
ID `ev_0ede2a00180a8c274f6fe1f65faa2813478f819e7d4852d2a8da8f47279c1481`.
At that acquisition stage, no game executable had been supplied or decompiled.
Subsequent original-code and supplied-image findings are linked above. Recorded
footage remains historical visual evidence, rather than a controlled runtime experiment.
