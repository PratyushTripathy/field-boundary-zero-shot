# field-boundary-zero-shot

Code accompanying the journal article **"Zero-shot inference strategies for smallholder (<0.1 ha) agriculture field delineation with the Segment Anything foundation model"** (Tripathy et al., 2026, *Science of Remote Sensing*).

The paper benchmarks the Segment Anything Model (SAM) for delineating smallholder agricultural field boundaries in Bihar, India, using 2 m SkySat imagery pansharpened to 0.8 m. Without fine-tuning, SAM identifies 57% of reference fields (mean IoU 0.73). The repository contains the post-processing and evaluation pipeline that converts raw SAM masks into vector field boundaries and benchmarks them against 8176 manually digitized reference polygons.

![Reference field sizes in the study area](figures/ground_truth_map_hist.png)

*Field sizes in our study area (mean 0.07 ha, median 0.05 ha) — substantially smaller than the parcels most prior studies retain after filtering.*

## What this repo contains

The pipeline is organised as five sequential Jupyter notebooks under `scripts/` that take raw SAM masks through hierarchical merging across checkpoints, tile sizes, acquisition dates, and image variants, plus shared geometry utilities and the plotting code used for the manuscript figures. See [`scripts/README.md`](scripts/README.md) for the workflow table, dependencies, and a step-by-step description of each notebook.

## Data

All inputs live under [`data/`](data/):

* **Imagery.** Four pre-processed SkySat scenes are in [`data/raster/`](data/raster/); see [`data/raster/README.md`](data/raster/README.md) for acquisition dates, pre-processing details, and the original Planet/GEE source.
* **Fishnet tiles.** GeoPackage tile grids used to chip the imagery for SAM inference are in [`data/vector/`](data/vector/) (`Fishnet_3by3.gpkg`, `Fishnet_4by4.gpkg`, `Fishnet_6by6.gpkg`, `Fishnet_12by12.gpkg`).
* **Reference field boundaries.** 8176 polygons (≈6 km²) in Bihar, India, manually digitized for this study. Mean parcel size 0.07 ha (median 0.05 ha); 82.68% of parcels are smaller than 0.1 ha.

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
Department of Geography, University of California, Santa Barbara

## Funding

This work was supported by the Benioff Scholars Program in Applied Environmental Science scholarship and the Schmidt Family Foundation Research Accelerator award.
