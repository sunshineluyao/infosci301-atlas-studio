# Atlas Studio: configure, teach and deploy

INFOSCI 301 · Week 4 · prepared 14 September 2026

## 1. What you have

| Edition | Starting experience | Deployment |
|---|---|---|
| Guided classroom | Light interface; four-level walkthrough; 2D first; optional 3D | Hugging Face Static HTML Space |
| Immersive research | Dark interface; selectable 3D network and space–time scenes; 2D alternative | Vercel, connected to your GitHub repository |

Both editions share the same curriculum, datasets, configuration and evidence record. These are working static applications, not mock-up images. They do not run hosted Python, LLMs, GeoAI models or drone reconstruction. The notebooks are the executable Python route.

The release is **not yet published** to your HF, GitHub or Vercel account. Build/data/interface-logic checks were performed locally; the environment blocked browser access to its local preview. Complete the live visual/WebGL/mobile acceptance checklist in Section 8 after deployment.

## 2. What was retained and improved

| Previous tutorial function | New route |
|---|---|
| Choose an idiom from the broader decision tree | Code & packages → Original idiom atlas; all 38 original idioms retained |
| Inspect data, marks and computation together | Explore → live workbench, legend, source inspection and active algorithm recipe |
| Python and R implementation guidance | Code & packages → Python / R / browser recipes; R adaptations explicitly unexecuted |
| Algorithm/package selection and output previews | Package gallery → purpose, execution status, documentation and saved artifacts |
| Run a notebook | Download either self-contained notebook → upload to Colab; configure GitHub for a direct link |
| Justify the choice | Four-level walkthrough → decision, validation, evidence note and final-project addition |

The previous `notebooks/idiom-algorithm-preview.html` path is preserved as a small entry page to the new application. The original full page is archived at `notebooks/legacy-idiom-atlas.html`. Retain both when replacing the tutorial in an existing static Space.

## 3. The classroom route

### Network: scientific communication of emerging technology

1. **Domain:** select an audience and a communication decision. What misunderstanding could the visual create? What audience evidence is still needed?
2. **Data/Task:** inspect real OpenAlex paper records. Paper–topic links mean provider classification—not citation, scientific truth or a verified NLP relationship.
3. **Idiom:** hold the dataset fixed; compare a basic topic-count chart, force-directed view, bipartite view and matrix. Give a peer a relationship-tracing task. Record errors and interpretation.
4. **Algorithm:** inspect seeded layout, BFS and PageRank parameters; run the notebook and checks. State what sample sensitivity changes. Export the communication brief and validation record.

### Place and time: human-centered intelligence / digital humanities

1. **Domain:** ask a heritage interpretation question that matters to people. Distinguish an administrative archive from lived experience and consent.
2. **Data/Task:** inspect designation IDs, date meaning, representative coordinates and missingness. The new core example uses NYC landmarks—not invented Jinxi observations. NASA EONET is a separate extension with a different unit.
3. **Idiom:** compare a basic timeline, point map, grid aggregation and 3D space–time view. Height encodes time, not cultural importance. Test interpretation against the simpler 2D alternative.
4. **Algorithm:** validate coordinates, IDs, dates, projections, counts and aggregation. No satellite/model output should be interpreted as a community-impact measure without additional evidence.

Every level has a different validation test. **Validation is not a fifth level.** A correct algorithm cannot establish that the audience question or data abstraction is valid. Framework: [Munzner's nested model](https://www.cs.ubc.ca/labs/imager/tr/2009/NestedModel/).

**Suggested pacing:** instructor models one route first; pairs complete one task in each studio; advanced tools remain optional. End with the team claim, not a requirement to master every package. This addresses tool overload and unclear purpose raised in the course feedback.

## 4. Configuration

Open **Configure** to test settings and download `config.json`. The dialog changes the current session only. To preserve a change, replace `public/config.json` in the source and rebuild, or replace root `config.json` in the prebuilt HF files.

| Setting | Meaning / example |
|---|---|
| `courseTitle`, `semester`, `instructor` | Public course labels |
| `defaultStudio` | `network` or `spatial` |
| `defaultTheme` | `light` or `dark`; immersive edition starts dark on first load |
| `enable3D` | `true` or `false`; turn off for lower-powered classrooms |
| `maxVisiblePapers` | Integer 5–60; start with 20–30 for legibility |
| `allowLocalData` | Enable local non-sensitive spatial JSON import |
| `githubRepo` | `YOUR_GITHUB_NAME/YOUR_REPOSITORY`, without `https://` |
| `githubBranch` | Usually `main`; use an actual branch |
| `notebookPath` | `public/notebooks` for this source repository |
| `spaceUrl`, `vercelUrl` | Optional release metadata; not credentials |

After setting a real public `githubRepo`, the notebook cards show a direct Colab link. Until then, the UI gives honest download/upload instructions instead of a fabricated “Open in Colab” URL. Private repositories may require additional Colab access; do not assume students have it.

Imported data format: a JSON array of `id`, `title`, `group`, `date` (`YYYY-MM-DD`), `lon`, `lat`, optional `url`. Maximum 5,000 records / 2 MB. It stays in browser memory. The downloadable schema contains placeholder coordinates and is clearly **not real data**. Do not import identifiable travel histories, private homes, restricted heritage locations or sensitive field notes.

Evidence notes and team drafts are stored on the learner's own device. No server collects submissions. Students must export, review and post through the course platform. Browser privacy settings may prevent local persistence; the UI warns them to export.

## 5. Create the Hugging Face Space — easiest route

1. Unzip **INFOSCI301_HuggingFace_Ready.zip** on your computer. Upload its contents, not the ZIP file itself.
2. Sign in to Hugging Face and create a new Space under the intended account or organization. Choose the **Static** SDK. Choose visibility deliberately after checking data/course-material sharing rights. Do not activate paid hardware for this static lesson.
3. In the Space's Files area, upload the extracted root files and folders while preserving their hierarchy. `index.html` and `README.md` must be at the repository root—not inside an extra outer folder. For many files, the CLI route below is more reliable.
4. Keep this root README metadata (already included in the prepared ZIP):

```yaml
---
title: INFOSCI 301 Atlas Studio
emoji: 🌐
colorFrom: blue
colorTo: green
sdk: static
app_file: index.html
fullWidth: true
header: mini
pinned: false
---
```

5. Open the App tab. Confirm both studios, source links, note export and notebook downloads. Open the app in its full-page view for teaching; an embedded frame may give the controls less room.
6. Edit root `config.json` if needed. No secrets are required. The configuration file is public; never put an HF token in it.
7. If replacing only the tutorial inside the existing Week 2 Space, preserve its other course files. Keep a recoverable copy/version first. Deploy this project in a dedicated Space if the current app's root/build architecture is different; do not overwrite an unrelated landing page blindly.

HF supports HTML/static assets directly; a static SDK is sufficient here. [Official Static HTML Spaces documentation](https://huggingface.co/docs/hub/spaces-sdks-static), [configuration reference](https://huggingface.co/docs/hub/spaces-config-reference).

### HF upload from the source project

After installing Node.js 22.12+ and extracting the source project:

```bash
npm ci
npm test
npm run build:hf
```

This prepares `dist-hf/`, including the correct HF README metadata. Install the official Hugging Face CLI in your own environment if needed, then authenticate interactively. Replace the example account/Space below with the exact destination you created:

```bash
hf auth login
hf upload YOUR_HF_NAME/YOUR_SPACE dist-hf . --repo-type space
```

Use the normal credential flow; do not paste a token into source files, chat, a Git remote or a public command log. Do not use deletion flags or mirror commands against an existing Space. [Official HF CLI guide](https://huggingface.co/docs/huggingface_hub/guides/cli).

## 6. Deploy the 3D edition to Vercel with Git

1. Extract **INFOSCI301_Atlas_Studio_Source.zip**. Open that project folder. It contains `package.json`, `src/`, `public/`, `vercel.json` and the test workflow.
2. Run the local checks and immersive build:

```bash
npm ci
npm test
npm run build:vercel
```

3. Create an empty GitHub repository under your chosen account. Public sharing should follow the attribution/permission review; choose private if necessary. If this folder is already inside a repository, use that repository's normal workflow rather than initializing or replacing it.
4. For a genuinely new, unversioned project folder, initialize and push:

```bash
git init -b main
git add .
git commit -m "Add INFOSCI301 Atlas Studio"
git remote add origin https://github.com/YOUR_GITHUB_NAME/YOUR_REPOSITORY.git
git push -u origin main
```

The ignore file excludes dependencies, build folders, local caches and environment files. No credentials are needed in the app.

5. In Vercel, choose **Add New → Project**, connect the intended GitHub account, and import only this repository. Review the integration permissions before granting access.
6. Keep the repository root as Root Directory. `vercel.json` sets:

| Field | Value |
|---|---|
| Framework | Vite |
| Install command | `npm ci` |
| Build command | `npm run build:vercel` |
| Output directory | `dist-vercel` |
| Node.js | 22.x or newer compatible runtime |
| Environment variables | None required |

7. Deploy, then complete Section 8 on the actual URL. This edition starts in dark/3D mode. Use 2D if WebGL is unavailable, hardware is slow, or the comparison task is clearer without depth.
8. Set the real repository path in `public/config.json`, commit and push. Vercel's Git integration deploys changes; non-production branches can be used for review previews, while the configured production branch controls the public course release. Use a PR to review instructional changes before merging. [Vercel GitHub documentation](https://vercel.com/docs/git/vercel-for-github), [Vite deployment guide](https://vite.dev/guide/static-deploy.html).

The included GitHub Actions workflow tests and builds both editions on pushes to `main` and on pull requests. It **does not publish to Hugging Face**. For each HF release, build/upload the reviewed version separately; this avoids an undisclosed credential-bearing workflow.

## 7. Design precedents reviewed

These are representative references, not a league table of “best” Spaces. Live designs and availability can change. Patterns are adapted, not copied.

| Reference | What informed this design | What was intentionally not imported |
|---|---|---|
| [HF InstantMesh](https://huggingface.co/spaces/TencentARC/InstantMesh) | Example-first workflow, progressive processing views, separate result/export | Model weights, inference cost, branding |
| [HF TRELLIS](https://huggingface.co/spaces/trellis-community/TRELLIS) | Collapsible advanced controls and clear output states | Its generative pipeline; Microsoft’s URL redirects to the community instance |
| [DeepSite](https://deepsite.hf.co/) | Obvious starting action and focused onboarding | Editor behavior was not tested; only the public landing experience was inspected |
| [React Three Next](https://react-three-next.vercel.app/) | Coordinated DOM and 3D manipulation | Starter code or assets; this project uses direct Three.js |
| [Threejs-Punk](https://threejspunk.vercel.app/) | Restrained depth/atmosphere inspiration | Heavy cinematic effects that could obscure teaching data |
| [Vercel's 3D event badge](https://vercel.com/blog/building-an-interactive-3d-event-badge-with-react-three-fiber) | Direct manipulation and clear interaction affordances | Badge physics, personal event data or visual assets |

The result uses a restrained navy/teal system with amber distinctions, progressive controls, source-aware inspection, a lazy-loaded 3D engine, no autoplay and a 2D/data-table alternative. It does not claim formal accessibility certification.

## 8. Acceptance checklist before class

- Open the deployed URL in a fresh/incognito browser. Confirm no console errors or missing local assets.
- Test desktop and a narrow/mobile viewport. Check wrapping, zoom, table scrolling and keyboard focus.
- Network: change paper count, year, layout, metric and neighborhood; select a paper and open its source. Compare graph and matrix on the same subset.
- Spatial: change year window and borough; compare points/grid; switch to NASA; compare world projections; inspect the record and timeline.
- 3D: orbit, zoom and select records. Verify axes and date range interpretation. Test 2D fallback on a low-powered device. Spatial axes stay fixed to the full selected dataset across filters; longitude/latitude are still independently normalized, so screen distance is not metric distance.
- Notes: type a non-sensitive test note, reload, export it, and confirm its contents. Confirm that no automatic submission is implied.
- Configuration: test a valid change and invalid input; reload deployed defaults. If enabled, test local data import with a public sample and an invalid file.
- Notebooks: download both, upload to a fresh Colab runtime, and run the required lesson cells. Live external tiles/CDN-dependent legacy previews may need internet; optional Graphviz/GeoAI/Earth Engine paths have distinct requirements.
- Have two students complete a task without instructor help. Record where they get stuck and revise before requiring the activity. Build correctness is not a usability study.

## 9. Before students leave

One team post: title/shared question; members and complementary strengths; individual-project evidence contributed; bounded SDG/local-community/open-science contribution; basic idiom, network and spatial–temporal design ideas with real sources and relationship/time semantics; Week 5 MVP scope and Week 6 user-study task.

Students export the draft in **Evidence & team claim**. Each added view must change an interpretation, research question or decision. By the end of the course, the goal is not tool collecting: it is evidence-led design capability, interdisciplinary innovation and responsible global leadership.
