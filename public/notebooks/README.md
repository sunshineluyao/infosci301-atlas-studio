# INFOSCI 301 Week 4 Advanced Idiom Tutorial

This folder is a drop-in replacement for the current `notebooks/idiom-algorithm-preview.html` resource. It narrows the required path to two advanced studios while retaining a broad package crosswalk.

## Files

- `idiom-algorithm-preview.html`: replacement landing page.
- `INFOSCI301_Week4_Network_Studio_Colab.ipynb`: editable Google Colab notebook.
- `INFOSCI301_Week4_Spatiotemporal_Studio_Colab.ipynb`: editable Google Colab notebook.
- `*_Executed.html`: executed, read-only previews with outputs.
- `data/`: simplified real-data snapshots and provenance.
- `outputs/`: static and interactive outputs created during verification.

## Deployment

1. Copy this folder into the existing Hugging Face Space `notebooks/` directory.
2. Replace the previous `idiom-algorithm-preview.html` with the file of the same name.
3. Keep the two notebooks, executed HTML files, `data/`, and `outputs/` beside the landing page so relative links continue to work.
4. Rebuild the Space and test every link in a private or preview deployment before publishing.

The existing public URL can remain unchanged after deployment. This package does not itself modify the public Space.

## Teaching route

- **Required:** run all cells in one notebook, save one relevant output, and complete the final-project transfer task.
- **Extension:** change one algorithm, parameter, or package only when it improves a named user task.
- **Verification:** students submit the output, captioned claim and boundary, code location, data/provenance note, accessibility fallback, and next test.

## Reproducibility

The notebook outputs were executed against the bundled snapshots. Live API, OpenStreetMap, and basemap cells have transparent fallbacks because external services can change or fail. Students must not present fallback data as live service output.
