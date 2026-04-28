# Data

All inputs used in the study live in this folder.

* **Imagery** — four pre-processed SkySat scenes are in [`raster/`](raster/); see [`raster/README.md`](raster/README.md) for acquisition dates, pre-processing details, original Planet/GEE source, and licensing.
* **Fishnet tiles** — GeoPackage tile grids used to chip the imagery for SAM inference are in [`vector/`](vector/) (`Fishnet_3by3.gpkg`, `Fishnet_4by4.gpkg`, `Fishnet_6by6.gpkg`, `Fishnet_12by12.gpkg`). Each is a plain rectangular grid in EPSG:32645 with no attributes other than geometry.
