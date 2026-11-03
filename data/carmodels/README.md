# Donor metadata and numeric profiles

Pinned source: [nicolas-found42/carmodels](https://github.com/nicolas-found42/carmodels/tree/ce047799fc550cdf92e4f7b62d97ef5c603e53ad).
The source ledger records 904 retained cars/trucks and 531 exclusions. The native
starter roster selects 30 vehicles from GT4, MC3, MCLA, and Ford Racing 2; see
`data/juiced2/accepted-roster.json` and the [asset workflow](../../tools/game/assets/README.md).

`profiles/` contains all 904 researched tuning profiles, with separate source-model
identity comments. `sources.jsonl` preserves selected factual references, original
numerical strings, URLs and quality limits. Nearby production-trim substitutions
are labeled; unknown physics fields remain estimates or priors.


The secondary specification compilation is
[gor3a/vehicle-makes-models](https://github.com/gor3a/vehicle-makes-models/tree/ee99776470a45214bf524cdfe22e5dbf4bd67f93),
compiled from Autoevolution and distributed under
[ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/).
Selected records retain attribution and original JSON pointers. Other manufacturer,
museum, club and specialist facts retain their own source classes and URLs.
Full articles, credentials and GLBs are not distributed here.
