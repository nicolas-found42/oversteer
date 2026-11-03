# Source vehicle inspector

Exports the actual baked carmodels sprites and researched physics values. It no
longer generates procedural cars or feature-label maps.

```sh
make tests
build/tests/oversteer_tests --dump-corpus-cards artifacts/corpus-cards
npm install --prefix tools/visual
npm test --prefix tools/visual
npm run serve --prefix tools/visual
```

Open http://localhost:4173. Search model codes/names, filter the four source families,
page through all 904 retained vehicles, and magnify their sprites. One shared
physical scale preserves relative vehicle sizes. Physics values include estimates
and labeled nearby trims; per-field evidence is reproducible through
`tools/carmodels/research.py`. `data/carmodels/sprites.json` records image provenance.

For a standalone HTML contact sheet:

```sh
build/tests/oversteer_tests --dump-corpus-sheet artifacts/gallery
```

The C exporter and game use the same PNG decoder and atlas bytes. Browser PNGs are
converted back to straight alpha; the game uses premultiplied alpha. Browser tests
verify catalog coverage, filters, image loading, magnification and inspectable
parameters, and capture each source family under `artifacts/visual/`.
