# Atlas Studio · INFOSCI 301

Two deployable editions of the same evidence-led visualization tutorial.

- **Hugging Face:** guided classroom interface, light default, 2D first, optional 3D.
- **Vercel:** immersive dark interface, genuine selectable Three.js scenes, 2D alternative.
- **Network studio:** emerging-technology scientific communication through paper–topic relationships.
- **Place/time studio:** human-centered digital humanities using NYC heritage designations, plus NASA EONET context.

Both editions preserve the original idiom atlas and add four-level teaching, executable notebook routes, evidence exports, source inspection, team-claim drafting and public JSON configuration.

## Local start

Use Node.js 22.12+ (tested build runtime: Node 24.19).

```bash
npm ci
npm test
npm run dev
```

If the host environment cannot enumerate network interfaces, run `npm run dev -- --host 127.0.0.1`.

## Build either target

```bash
npm run build:hf
npm run build:vercel
```

Output: `dist-hf/` or `dist-vercel/`. Serve over HTTP; do not double-click index.html through file://. These are static applications, not Python inference services. No API keys, hosted database or user tracking are needed.

## Configure

Edit `public/config.json`, then rebuild. The UI **Configure** dialog also lets you test and download the file. Session changes alone do not alter deployed defaults. See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for HF and Vercel instructions.

## Repository contents

| Path | Purpose |
|---|---|
| `src/engine.js` | Graph construction, degree, PageRank, BFS, filtering, input validation |
| `src/Visuals.jsx` | D3/SVG network, adjacency matrix, map and linked basic charts |
| `src/Scene3D.jsx` | Lazy-loaded Three.js graph/time and place/time scenes |
| `src/content.js` | Four-level curriculum, sources, package gallery and team template |
| `public/data/` | Real snapshots and provenance manifest |
| `public/notebooks/` | Executed notebooks, original atlas and retained outputs |
| `tests/` | Deterministic data, graph and validation tests |
| `.github/workflows/quality.yml` | Test and build both editions on pushes / PRs |
| `vercel.json` | Git-integrated Vercel deployment settings |

## Teaching and evidence boundaries

Domain → Data/Task → Idiom → Algorithm. **Each level has its own validation; validation is not a fifth level.** Correct code does not prove a useful or ethical domain framing.

Topic assignments are not citations or verified NLP relations. Administrative heritage designation is not cultural value. NASA event geometries are not people affected. The 3D height is year, not importance; the 3D place axes are normalized longitude/latitude, not metric distances. No GeoAI inference, drone reconstruction or Earth Engine computation is performed in this browser app.

Use only non-sensitive local JSON data. Imported data remain in memory. Evidence notes remain in the user's browser storage until exported; the app does not collect submissions. An exported note may contain what the student typed, so they should review it before sharing.

## Provenance and rights

See `public/data/provenance.json`, the source links in the app and `THIRD_PARTY_NOTICES.md`. Original course materials are retained for the course owner's use; no blanket license is asserted over third-party data or the legacy atlas. Select your intended license before public release of newly authored course code. Dependencies keep their respective licenses.

## Release status

This source package is deployable but not published to a live HF Space, GitHub repository or Vercel project. Account permissions, deployed-browser checks and student acceptance tests remain release gates. Consult `QA_REPORT.md` for executed checks and limitations.
