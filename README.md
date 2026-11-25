# steering-blog

Source for the blog series **Batched Steering on TPU**: hundreds of LLM steering experiments in one forward
pass on a TPU (TorchTPU Sprint 26H4). Built with [Quarto](https://quarto.org), published to GitHub Pages by
GitHub Actions.

Answer key and source of every "original repo" number: Avishek Biswas,
[`learn-mech-interp/03-steering`](https://github.com/avbiswas/learn-mech-interp/tree/main/03-steering) (MIT).

## Layout

```
_quarto.yml               site config: theme (light/dark), KaTeX, citations, code folding, draft mode
index.qmd                 series landing page (lists posts by `order`)
about.qmd                 About page
references.bib            citations, used as [@key] in posts
posts/_metadata.yml       author, licence, citation settings shared by all posts
posts/NN-slug/index.qmd   one folder per post
_lib/plots.py             plotting helpers: load(), heatmap(), line(), bars(), save(), PALETTE/ROLE
_styles/                  SCSS themes + shared CSS (.key-result box, .todo marker)
data/                     result JSON that posts plot (copied from the lab repo's results/)
figures/                  static images (diagrams, XProf screenshots) and optional exported SVGs
.github/workflows/publish.yml   render + deploy to GitHub Pages
```

| Post | Status |
|------|--------|
| 01 Make a model sad in four lines | draft, complete |
| 02 Steering is a search problem | draft, complete (cites original repo numbers) |
| 03 First steps with TorchTPU and hooks | draft, complete (TPU facts filled in) |
| 04 One row per experiment | draft, complete (TPU results) |
| 05 Maps of the steering window | complete (E1 sad map + test check, E2 tomato map, E3 1,000-trial removal search) |
| 06 How fast is one pass? | complete for modes A–D + scaling curve (XProf not measured) |
| 07 Refusal, and two pushes at once | complete (stretch: E4 refusal direction, E5 sad + tomato mixing) |

## Preview locally

```bash
pip install -r requirements.txt     # jupyter + matplotlib for the figure cells
quarto preview                      # live-reloading local server
quarto render                       # full build into _site/
```

If Quarto picks the wrong Python, point it at the right one: `QUARTO_PYTHON=/path/to/python quarto render`.

## Adding results

1. Copy a result file from the lab repo, e.g. `results/m1_repro_sad.json` → `data/04-equivalence.json`.
   Name files `NN-what.json` after the post that uses them. Keep them small (summaries, not raw generations).
2. In the post, load and plot it:

   ````markdown
   ```{python}
   #| echo: false
   import os, sys
   sys.path.insert(0, os.environ.get("QUARTO_PROJECT_DIR", "../.."))
   from _lib.plots import load, heatmap, line, bars, ROLE
   ```

   ```{python}
   #| label: fig-mood-map
   #| fig-cap: "Mood by layer and push strength."
   res = load("05-mood-map.json")
   heatmap(res["values"], x=res["strengths"], y=res["layers"], center=0,
           xlabel="push strength (×)", ylabel="layer", cbar_label="mood", data=res)
   ```
   ````

3. Conventions the helpers enforce or expect:
   - `"_placeholder": true` in a JSON file stamps a red PLACEHOLDER watermark on its figures. Real results
     must not have it (or set it to `false`).
   - Numbers from someone else's work get `source="..."` so the figure carries a source line, and the text
     says "original repo's results". See `data/answer_key_03_steering.json` and post 02.
   - Use `ROLE["steered"]`, `ROLE["control"]`, `ROLE["tune"]`, `ROLE["test"]`… so a colour means the same
     thing in every post.
4. Replace every `<span class="todo">TODO…</span>` in the post. Check none are left:
   `grep -rn 'class="todo"' posts/`

## Finishing a stub

Remove `draft: true` from its front matter and the "Stub: not written yet" callout, set the real `date`,
and drop the `stub` category. Drafts are rendered (so CI checks they build) but are hidden from the listing,
navigation and search (`draft-mode: unlinked`); anyone with the direct URL can still open them.

## Publishing

1. Create the GitHub repo `steering-blog` and push `main`.
2. Repo → Settings → Pages → Source: **GitHub Actions**.
3. Every push to `main` renders and deploys to `https://tinevimbomusingadi.github.io/steering-blog/`.
   Pull requests only render (a build check), they don't deploy.

GitHub Pages on a **private** repo needs a paid plan (GitHub Pro or above), so the repo probably has to be
public at launch. Until then, stub posts are hidden by draft mode, but their source is visible in a public repo.

If the repo name or account changes, update `site-url` and `repo-url` in `_quarto.yml`.
