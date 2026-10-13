# Notebook revision · 13 October 2026

The GitHub notebook is the canonical lesson. Its downloadable `.ipynb`, saved HTML result, source checksum, and figure/data bundle now travel together. The Vercel interface embeds this actual saved output instead of a simulated notebook result. No Hugging Face source or deployment was inspected or changed.

## Teaching and execution contract

- Preserve the existing demonstrations, references, bilingual explanations, and human authorship. Each executable idiom gains a task, named method, data/unit note, evidence boundary, and adaptation prompt.
- Run the bundled-data core first. `RUN_PACKAGE_EXTENSIONS=False` keeps specialist libraries optional, with explicit not-run status. A printed skip is not an executed algorithm. Package installation may require internet; the default lesson data do not require a live API, account, or key.
- Compare the same records and fixed scales. Source hashes accompany snapshots; paper/topic assignments are not citations, heritage dates are designations, rainfall is modeled monthly mean precipitation, and archaeological teaching assertions are categorical rather than counts/probabilities.
- Export editable SVG/PDF/PNG, relevant CSV dictionaries, parameter state, and a student design record. Actual peer feedback stays blank until collected. The saved bundle is the reference run; students edit and export their own record in Colab.
- Widget controls require Colab. The web result supports readable static outputs and saved Plotly/Altair inspection where the browser and supporting libraries permit it. The record verifies Python execution, not end-to-end Colab gestures, R, every optional package, touch operation, screen-reader conformance, or community validation.

## Rebuild and maintain

Use Python 3.12 with `requirements-notebooks.txt` and Node 22.12+ (checked with Node 24.19).

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-notebooks.txt
npm run notebook:build
.venv/bin/python scripts/publish_notebooks.py
npm test
```

`notebook:build` modifies editable sources; `notebook:publish` executes each in a fresh IPython process and generates matching HTML, bundles, and `public/notebooks/manifest.json`. A failed core cell stops publication. Execution uses no Jupyter kernel sockets. `--render-only` refreshes HTML from already executed notebooks and existing run assets; it does not verify a new run. Generated source cells have stable IDs; original code is retained in cell metadata so repeated source generation is idempotent. Saved output files are stored as compressed text parts; a pinned external Plotly renderer supports browser inspection so ordinary Vercel builds need no Python runtime.

Run `npm test` after any notebook or embedding change. Regression checks compare the exact notebook SHA-256, every embedded SVG/PNG, recorded figure totals, cell anchors, optional status, and local download destinations. A source edit without republishing will fail the checksum check.

## Applied design tools

| Checklist skill/tool | Applied decision | Source |
|---|---|---|
| Frontend Design | Full-width readable results, clear output/source/download hierarchy | https://github.com/anthropics/skills/tree/main/skills/frontend-design |
| UI UX Pro Max | Responsive spacing, clear control and status treatment, readable notebook framing | https://github.com/nextlevelbuilder/ui-ux-pro-max-skill |
| Impeccable | Remove simulated result UI, clarify saved execution versus runnable controls, repair overflow | https://github.com/pbakaus/impeccable |
| Scientific visualization / scientific-data-figures | Real-data comparisons, fixed baselines, explicit units, editable vectors | https://github.com/K-Dense-AI/scientific-agent-skills/tree/main/scientific-skills/scientific-visualization |
| figure-reviewer | Separate figure inspection, label/collision repairs, grayscale and source review | https://research-figure-guide.nature.com/ |

These are the tools relevant to this revision, not a claim that every tool in the AI Design Tools Checklist was executed. Generated illustrations were unnecessary: all quantitative and relationship figures are reproducible code-driven outputs.

## Revised lessons

| Canonical notebook | Revision |
|---|---|
| `public/notebooks/INFOSCI301_Week4_Network_Studio_Colab.ipynb` | App-matched 30-paper / 47-topic / 84-link comparison; topic-count baseline; ordered bipartite view; matrix showing 12 of 47 topics with complete CSV and ID dictionaries. Retains the original Karate Club and 20-paper explorations as separate exercises. |
| `public/notebooks/INFOSCI301_Week4_Spatiotemporal_Studio_Colab.ipynb` | Same 1,457 unique designation IDs in timeline, map and cube; fixed full-record extents; borough colors plus symbols; background-free EONET core; optional trajectory length requests meters explicitly. |
| `public/notebooks/INFOSCI301_Week2_Idiom_Algorithm_Gallery_Python_R.ipynb` | Restores the missing editable source from this repository's versioned HTML. Preserves all 38 idioms and 72 tool references; labels synthetic gallery data and unexecuted R/recipe templates; increases gallery label size. |

The old `legacy-idiom-atlas.html` URL now serves the matching regenerated gallery. The three notebook cards embed genuine outputs and expose Colab, exact source, checksums and downloadable assets. Existing specialist-package artifacts are retained as prior reference artifacts, with corrected status labels.

## Validation and visual review

Fresh process execution completed 56 Python cells across three notebooks (including explicit optional skips): 12 gallery, 21 network and 23 spatial. Fifteen automated tests and the Vercel build pass. The 38-row idiom and 72-row package exports remain complete. Optional extensions and R are not certified by this run.

The following are internal teaching-output review scores, not scientific validity ratings or an external review. The wider old-gallery inventory remains a reference overview; a reader should use a selected single idiom for detail.

| Figure / role | Review and repair | Internal readiness |
|---|---|---|
| Topic counts / quantitative baseline | Long topic labels wrap; count axis begins at zero; sample and top-8 boundary visible | 94/100 |
| Paper–topic graph / relationships | Replaced colliding force labels with ordered two-column P/T IDs; shape redundancy and source dictionaries | 94/100 |
| Adjacency matrix / alternative encoding | Same 30 papers; honest 12/47 visible-topic subset; full matrix retained; rotated wrapped headers | 93/100 |
| Heritage map/timeline / paired spatial and temporal readings | Same record set, designation units, fixed extent, borough symbols and explicit counts | 94/100 |
| Heritage cube / optional depth comparison | Repaired clipped z-label; fixed all-record domains; symbols supplement colors | 92/100 |
| Original gallery / overview of visual grammar | Larger tick labels; synthetic-data footer; complete dictionaries and standalone editable source | 91/100 |

New-output label collisions found during review were repaired and the regenerated rasters inspected. This gate supports teaching preview release; interpretation, accessibility user testing, and specialist extensions retain their stated limits.


## Publication format

GitHub stores readable, editable notebook source. Saved cell outputs live in the verified HTML companion. The publisher executes the same source in a fresh process, then clears the runtime output payload in the download to keep editing lightweight. The HTML includes the exact source and receipt; the manifest binds the source checksum, output checksum and figure count. Compressed text parts in public/notebooks/packed are assembled by scripts/materialize-notebook-outputs.mjs during npm build/test/dev, with checksums checked before writing HTML and ZIP assets. Colab runs need no build step; the source already contains the lesson data.
