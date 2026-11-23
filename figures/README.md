# figures/

- Static images used by posts (diagrams, XProf screenshots): name them `NN-short-name.png|svg`, where `NN` is the post number.
- `_lib.plots.save(fig, "NN-name")` also writes a generated figure here as SVG, for reuse in slides or the code repo's README.
- Figures inside posts are generated at render time from `data/*.json`, so generated SVGs don't need committing unless you use them elsewhere.
