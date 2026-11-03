# Reference browser verification

This directory owns the Playwright dependency used by the reference-vault review
pilot tests. Install it with `npm ci --prefix tools/visual`, then run
`npm test --prefix tools/visual`. The browser harness requires the local reference
corpus and builds the current pilot template in a temporary directory. It does
not create human judgments or establish classification acceptance.
