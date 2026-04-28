# Raster data

This folder contains the four pre-processed SkySat scenes used in the study, covering the 2015–16 winter crop cycle in Bihar, India.

| File | Acquisition date |
|---|---|
| `T1_SkySat.tif` | 11 May 2015 |
| `T2_SkySat.tif` | 29 September 2015 |
| `T3_SkySat.tif` | 16 November 2015 |
| `T4_SkySat.tif` | 10 February 2016 |

Each file is a 3-band false-colour composite (Blue, Green, NIR) at 0.8 m resolution, pansharpened from the native 2 m multispectral bands using the 0.8 m panchromatic band, byte-scaled to 0–255 between the 2nd and 98th percentiles per band, and clipped to the study area in UTM zone 45N (EPSG:32645). All four scenes were manually co-registered to T1 in QGIS using ground control points.

## Original source

The raw SkySat Public Orthorectified Multispectral imagery is provided by Planet Labs Inc. and available through Google Earth Engine:

<https://developers.google.com/earth-engine/datasets/catalog/SKYSAT_GEN-A_PUBLIC_ORTHO_MULTISPECTRAL>

Refer to the article (see the repository [README](../../README.md)) for full pre-processing details.

## License and attribution

The original SkySat Public Orthorectified Multispectral imagery is © Planet Labs Inc. and is released on Google Earth Engine under the **Creative Commons Attribution 4.0 International License (CC BY 4.0)**. The pre-processed files in this folder are derivative works of that imagery and are therefore subject to the same Planet Labs terms — any rights granted here cannot exceed the restrictions imposed by Planet on the source dataset.

If you use any file in this folder, please check the updated citation format and usage guidelines at the [Google Earth Engine data catalog](https://developers.google.com/earth-engine/datasets/catalog/SKYSAT_GEN-A_PUBLIC_ORTHO_MULTISPECTRAL) and cite this article (see citation guidelines [here](../../README.md#citation)).

These derivatives are otherwise made available under CC BY 4.0, consistent with the upstream Planet licence, but in case of any conflict, **Planet Labs' terms govern**.
