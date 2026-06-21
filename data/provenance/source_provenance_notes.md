# Source Provenance Notes

This file supplements `malaysia_dosm_poverty_provenance.json` with the source families used by the submitted state-year panel. It records reproducibility evidence available in the submitted folder without pretending that unavailable download receipts exist.

| Source family | Submitted evidence | Version/source note | Reproducibility limitation |
|---|---|---|---|
| DOSM poverty labels | `data/raw/dosm/hh_poverty_state.csv`; `data/interim/dosm_poverty_state_clean.csv`; `outputs/qa/dosm_raw_lineage_validation.json`; `data/provenance/malaysia_dosm_poverty_provenance.json` | DOSM Open Data poverty catalogue: `https://open.dosm.gov.my/data-catalogue/hh_poverty_state`; CSV export: `https://storage.dosm.gov.my/hies/hh_poverty_state.csv` | Raw official poverty labels are retained and validated against the model-ready panel target columns. |
| Administrative boundaries | `data/boundaries/malaysia_adm1_geoboundaries.geojson` | geoBoundaries `gbOpen`, MYS ADM1, boundary ID `MYS-ADM1-15666254`, source OpenStreetMap/Wambacher | Simplified boundary geometry is redistributed under ODbL 1.0 with attribution; see `DATA_LICENSES.md`. |
| Retained geospatial feature panel | `notebooks/02_malaysia_spatial_features.ipynb`; `data/state_year_panel_modelready_2002_2022.csv`; `scripts/verify_lineage.py` | Notebook 02 validates the retained feature schema and provenance fields; the checksum script verifies the exact panel used for published results. | The original raw-raster extraction implementation and raster exports were not retained, so this repository cannot rebuild these columns from imagery. This limitation is explicit rather than reconstructed from incomplete evidence. |
| Nighttime lights | Panel columns with `ntl`, `mean_ntl_year_used`, and `wmean_ntl_sensor_code` | DMSP/OLS-CCNL and VIIRS-DNB are harmonized at state level. 2012 NTL uses 2013 VIIRS due to sensor availability. | NTL fields are excluded from the primary sensor-safe model. Full-feature models that use them are retrospective comparators only. |
| Vegetation and land cover | Panel columns with `evi`, `ndvi`, `frac_cropland`, `frac_forest`, `frac_urban` | MODIS-derived vegetation and land-cover features are aggregated to state-year rows. | Original raster exports are not included; notebook and retained panel are the reproducibility evidence. |
| Population | `pop_sum_grid`, `pop_sum_grid_log1p`, `mean_pop_year_used`, `wmean_pop_year_used` | WorldPop-derived population summaries. | 2021-2022 population is forward-filled from 2020 where needed, as disclosed in the report. |
| Topography | `wmean_elevation`, `wmean_slope` | SRTM-derived elevation/slope features. | Static terrain source is retained as derived columns, not raw raster tiles. |

## Checksums

The DOSM provenance JSON records raw, cleaned, and retained-panel evidence. Regenerate checksums whenever a source or derived data artifact changes.
