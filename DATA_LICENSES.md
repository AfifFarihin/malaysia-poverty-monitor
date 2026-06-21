# Data Licenses and Attribution

The repository-level MIT license covers original code and documentation only. Data files retain the terms of their source providers.

## DOSM Poverty Data

- Dataset: `hh_poverty_state`
- Provider: Department of Statistics Malaysia (DOSM)
- Catalogue: https://open.dosm.gov.my/data-catalogue/hh_poverty_state
- Retained files: `data/raw/dosm/hh_poverty_state.csv` and cleaned derivatives
- License: Creative Commons Attribution 4.0 International (CC BY 4.0)
- Attribution: Department of Statistics Malaysia, `hh_poverty_state`, accessed through OpenDOSM/data.gov.my.

The OpenDOSM catalogue identifies this dataset as CC BY 4.0. The license text is available at https://creativecommons.org/licenses/by/4.0/.

## Malaysia Administrative Boundaries

- Dataset: geoBoundaries `gbOpen`, MYS ADM1
- Boundary ID: `MYS-ADM1-15666254`
- Source: OpenStreetMap and Wambacher, distributed by geoBoundaries
- API metadata: https://www.geoboundaries.org/api/current/gbOpen/MYS/ADM1/
- Retained file: `data/boundaries/malaysia_adm1_geoboundaries.geojson`
- License: Open Data Commons Open Database License 1.0 (ODbL 1.0)
- Attribution: `© OpenStreetMap contributors`, with boundary packaging from geoBoundaries/Wambacher.

The ODbL text is available at https://opendatacommons.org/licenses/odbl/1-0/.

## Derived Satellite and Geospatial Features

`data/state_year_panel_modelready_2002_2022.csv` contains state-level aggregates derived from public nighttime-light, MODIS vegetation/land-cover, WorldPop population, and SRTM terrain products accessed during the original research workflow. Raw raster imagery is not included.

The derived panel is provided for research reproducibility. Reusers are responsible for reviewing the original providers' current attribution, redistribution, and commercial-use terms before republishing derived data or rebuilding the extraction pipeline.
