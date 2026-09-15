# Atlas Studio release checks

Date: 14 September 2026. This is a deployable teaching package, not a claim of a published or classroom-validated release.

## Executed checks

- Both Vite production targets build: guided HF and immersive Vercel. The HF build writes the required static-SDK README automatically.
- `npm audit --omit=dev` reported zero known production-dependency vulnerabilities at the check time. This is not a security certification and does not cover every development tool or future advisory.
- **12 automated tests pass:** graph ID/edge integrity; degree reconciliation; normalized PageRank and dangling-node handling; BFS depth; search/year/empty filtering; source-data IDs/coordinates/dates; inclusive spatial filtering; public configuration validation; local import validation; bundled resource presence; stable 3D spatial coordinates across filters; singleton/empty spatial model; and the UI integration test. Several checks are grouped within one test.
- The DOM-emulated UI test loads the real datasets, changes studio and sections, switches the spatial dataset, filters a category, opens both notebook downloads, chooses the R recipe, opens reference sources and applies configuration. **DOM emulation is not browser layout, WebGL or usability validation.**
- Six new Python notebook cells (three per notebook) were executed in the supplied Python environment. They load the newly embedded real snapshots, generate baseline/advanced plots and run data/graph checks. Earlier executed package cells and outputs are retained; a fresh end-to-end Colab runtime has not been retested in this release.
- Static SVG/PNG references generated from the actual React/D3 view components were visually inspected. The initial network label collisions were corrected with collision-aware label placement. These files are **not screenshots of the complete UI**.
- External research/provider documentation and design references were checked. The live UI of InstantMesh, TRELLIS, the React Three Next example and DeepSite's public landing page was inspected. Threejs-Punk and Vercel's event-badge article were reviewed as reference sources, not copied implementations.

## Data audit

| Dataset | Retained evidence | Important boundary |
|---|---|---|
| OpenAlex emerging geospatial AI | 60 retrieved works; default view first 30; up to three assigned topics per work | Not a systematic review. Edges are classification, not citations or verified NLP relations. |
| NYC individual landmarks | 2,065 input building records; 74 excluded for missing/invalid coordinate/date fields; 1,457 unique designation IDs after deduplication | First valid building coordinate retained. Date = designation, not construction or community value. |
| NASA EONET | 272 dated point geometries from the prior documented category snapshots | Not unique event count, a complete inventory or people affected. |

Raw OpenAlex and NYC responses are included under `source_data/`. `scripts/prepare-data.mjs` reproduces the data transformations. Source queries, snapshot dates and exclusions are retained in `public/data/provenance.json`.

## Network figure contract

- Question: which publication–topic connections can support an evidence-bounded emerging-technology communication task?
- Nodes: papers (cyan circles) and provider-assigned topics (amber rounded squares in 2D).
- Edges: unweighted, undirected paper–topic classification links. Provider topic scores are retained as metadata but not used as edge weights.
- Time: publication year on paper records; 3D paper height uses year. Topic nodes sit at the base plane and do not have an inferred publication date.
- Size: degree or PageRank in 2D. In 3D, degree-based scaling is fixed; the 2D metric control explicitly returns to 2D.
- Layout: force for an overview, bipartite for type separation, circular for ordering comparison, matrix for adjacency. Layout position is not semantic distance or authority.
- Dense labels: show only selected/frequent-topic candidates that fit without estimated label/node collisions; full labels remain in source inspection/table. Layout comparison is a task hypothesis, not a demonstrated usability result.

## 3D contract

The immersive edition uses real Three.js instanced geometry, orbit controls and raycast record selection. Spatial X/Z encode normalized longitude/latitude; Y encodes year. Bounds stay fixed to the full selected dataset when filters change. This prevents filtering from silently moving a place in the cube. Axes are not metric distances. There is no autoplay animation, and the engine is lazy-loaded.

## Unresolved release gates

The environment's browser rejected the local preview URL. No alternate browser or unauthorized deployment was used to bypass that restriction. Therefore the following remain **pending**:

1. Live HF/Vercel deployment and asset/iframe verification.
2. Browser rendering, responsive layout, keyboard/focus behavior and WebGL performance/picking.
3. Fresh Colab “run required cells” checks on student accounts.
4. Actual student task comparison and instructor/community review of domain and abstraction choices.
5. Instructor approval of public-sharing rights, license choice and final course wording.

Until those checks pass, treat the package as a release candidate. The network-visualization review requirement is not represented as a completed independent human review or a formal accessibility certification. The deployment guide contains the acceptance procedure.

## Known extension boundaries

R snippets are adaptations, not executed outputs. Graphviz DOT is retained but its executable was unavailable in the previous notebook run. Legacy Plotly/PyVis/Folium exports can depend on third-party scripts or basemap tiles. The core new app bundles its D3/Three.js code, map context and real data. Earth Engine, geemap, Cesium, Prithvi, NLP relation extraction and drone reconstruction are optional extension routes—not invisible computations performed by the demo.
