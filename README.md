# field-boundary-zero-shot

Code accompanying the journal article **"Zero-shot inference strategies for smallholder (<0.1 ha) agriculture field delineation with the Segment Anything foundation model"** (Tripathy et al., 2026, *Science of Remote Sensing*).

The paper benchmarks the Segment Anything Model (SAM) for delineating smallholder agricultural field boundaries in Bihar, India, using 2 m SkySat imagery pansharpened to 0.8 m. Without fine-tuning, SAM identifies 57% of reference fields (mean IoU 0.73). The repository contains the post-processing and evaluation pipeline that converts raw SAM masks into vector field boundaries and benchmarks them against 8176 manually digitized reference polygons.

![Reference field sizes in the study area](figures/ground_truth_map_hist.png)

*Field sizes in our study area (mean 0.07 ha, median 0.05 ha) — substantially smaller than the parcels most prior studies retain after filtering.*

## What this repo contains

The pipeline is organised as five sequential Jupyter notebooks under `scripts/`, each merging predictions at a different level of aggregation, plus shared geometry utilities and the plotting code used for the manuscript figures.

| Stage | Notebook | What it does |
|---|---|---|
| Workflow 1 | `Workflow1_v4.ipynb` | Merge adjacent SAM polygons within a tile set; area, NDVI, and compactness filtering. |
| Workflow 2 | `Workflow2_v3.ipynb` | Merge predictions across SAM checkpoints (ViT-B, ViT-L, ViT-H). |
| Workflow 3 | `Workflow3_v2.ipynb` | Merge predictions across input tile sizes within an acquisition date. |
| Workflow 4 | `Workflow4_v1.ipynb` | Merge predictions across the four acquisition dates (T1–T4). |
| Workflow 5 | `Workflow5_v1.ipynb` | Merge original and edge-enhanced image predictions. |
| Plots | `PlotsForPaper_Share_v3.ipynb`, `ReviewersPlots_v1.ipynb` | Manuscript and reviewer-response figures. |
| Utilities | `utils.py` | Geometry merging, overlap resolution, accuracy metrics. |

A more detailed step-by-step description of each workflow lives in [`scripts/README.md`](scripts/README.md).

## Data

* **Imagery.** SkySat Public Orthorectified multispectral imagery, available via Google Earth Engine: <https://developers.google.com/earth-engine/datasets/catalog/SKYSAT_GEN-A_PUBLIC_ORTHO_MULTISPECTRAL>.
* **Reference field boundaries.** 8176 polygons (≈6 km²) in Bihar, India, manually digitized for this study. Mean parcel size 0.07 ha (median 0.05 ha); 82.68% of parcels are smaller than 0.1 ha.

## Dependencies

The notebooks rely on `geopandas`, `shapely`, `geoplanar`, `numpy`, `pandas`, `rasterio`, and `matplotlib`. SAM inference itself uses [`samgeo`](https://samgeo.gishub.org/). A complete environment file may be added in a future revision; for now, install the listed packages into a fresh Python environment.

## Citation

If you use this code or build on the analysis, please cite the article:

> Tripathy, P., Baylis, K., Wu, K., Watson, J., & Jiang, R. (2026). Zero-shot inference strategies for smallholder (<0.1 ha) agriculture field delineation with the Segment Anything foundation model. *Science of Remote Sensing*, 100425. <https://doi.org/10.1016/j.srs.2026.100425>

### BibTeX

```bibtex
@article{tripathy2026zeroshot,
  author  = {Tripathy, Pratyush and Baylis, Kathy and Wu, Kyle and Watson, Jyles and Jiang, Ruizhe},
  title   = {Zero-shot inference strategies for smallholder ({$<$}0.1~ha) agriculture field delineation with the {Segment} {Anything} foundation model},
  journal = {Science of Remote Sensing},
  year    = {2026},
  pages   = {100425},
  doi     = {10.1016/j.srs.2026.100425},
  url     = {https://doi.org/10.1016/j.srs.2026.100425}
}
```

## License

Released under the [MIT License](LICENSE).

## Contact

Pratyush Tripathy — <ptripathy@ucsb.edu>

## Funding

This work was supported by the Benioff Scholars Program in Applied Environmental Science scholarship and the Schmidt Family Foundation Research Accelerator award.
