# 🛰️ EUMETSAT International Autumn School — Satellite Data Applications 2025
**Athens, Greece · 3 - 7 November 2025**

Hands-on week applying satellite data to weather, climate, and environmental monitoring. This repository contains exercises, datasets, and scripts organized by training day.

---

## Quick links
- Repository: `EUMETSAT_autumn_school_2025/`  
- Course root (local): `~/autumn_school2025/`  
- WEkEO workspace URL: https://wekeo.copernicus.eu/my-wekeo

---

## Agenda (overview)
| Day       | Focus                     | Main topics |
|-----------|---------------------------|-------------|
| Monday    | EUMETView & Data Access   | Remote‑sensing fundamentals, RGB products, WEkEO |
| Tuesday   | MTG Lightning Imager      | LI data access, visualization, parallax correction |
| Wednesday | HSAF Products             | Precipitation, rain‑rate visualization, ADAGUC |
| Thursday  | LSA‑SAF & Fire Products   | LST, fire detection & monitoring, LSASAF tools |
| Friday    | DUST Monitoring           | Dust products, visualization, wrap‑up & discussion |

---

## Repository structure
```
EUMETSAT_autumn_school_2025/
├── Day_Monday/        # EUMETView, ADAGUC, RGB, WEkEO setup
├── Day_Tuesday/       # MTG Lightning Imager labs
├── Day_Wednesday/     # HSAF products & exercises
├── Day_Thursday/      # LSA‑SAF, fire detection
├── Day_Friday/        # Dust monitoring & final exercises
└── setup/             # Utility scripts and documentation
```

---

## Quick setup

### 1) Create virtual environments
Open a terminal and run:

```bash
# eumdac_data_store environment
cd $HOME/eumdac_data_store/
conda env create -f environment.yml
conda activate eumdac_data_store
python -m ipykernel install --user --name eumdac_data_store

# MTG environment for imagery generation
cd $HOME/Lab10_FCI_data_display/
conda env create -f environment.yml
conda activate MTG
python -m ipykernel install --user --name MTG
```

---

### 2) Download static files
Run the script and unpack the downloaded archives:

```bash
cd ~/autumn_school2025/               # course root
python download.py                    # download static files
cd static-files
for f in *.zip; do unzip "$f"; done   # unpack all zips
```

---

### 3) Generating image visualizations from EUMETView (WEkEO)
1. Log in to WEkEO: https://wekeo.copernicus.eu/my-wekeo and open WEkEO Workspace.  
2. Start the server (may take a few minutes), then navigate to `autumn_school2025/EUMETVIEW/`.  
3. Open `RetrieveFCIImagesFromEumetview.ipynb` and follow the notebook cells.

Available image products:
- `rgb_truecolour`, `rgb_cloudphase`, `rgb_dust`, `rgb_geocolour`
- `li_afa`, `rgb_cloudtype`, `rgb_fog`
- `vis06_hrfi`, `ir105_hrfi`

Resulting images are stored in:
`$HOME/autumn_school2025/EUMETVIEW/EUMETVIEW_IMAGERY/`

To package for local download:
```bash
cd $HOME/autumn_school2025/EUMETVIEW/EUMETVIEW_IMAGERY/
tar -cvf images.tar *
bzip2 images.tar
# download images.tar.bz2 from the workspace
```

---

### 4) Generating images from EUMETSAT Data Store data

a) Download satellite data via WEkEO workspace:
- Open `autumn_school2025/eumdac_data_store/` and run `1_5_MTG_FCI_data_access.ipynb` using the `eumdac_data_store` kernel to retrieve data for the chosen region/time.

b) Generate imagery locally:
```bash
# prepare environment and navigate to script folder
cd $HOME/autumn_school2025/IMAGERY/
conda deactivate
conda activate MTG
cd script/

# run imagery creation (adjust path and parameters)
./create_imagery.sh "path/to/eumdac_data_store/" \
    true_color,cloud_phase,cloud_type,colouredIR_Setvak,IR_105,VIS_06 \
    2025-01-12T15:00:00Z 2025-01-12T16:00:00Z 10 "10,56,24,32" 2000
```

Possible composites:
- `true_color`, `cloud_phase`, `cloud_type`, `convection`, `colouredIR_Setvak`
- `night_microphysics`, `dust`, `natural_color`, `airmass`
- `IR_105`, `VIS_06`

Output directory:
`$HOME/autumn_school2025/IMAGERY/script/plots`

To compress for download:
```bash
cd $HOME/autumn_school2025/IMAGERY/script/plots
tar -cvf images.tar *
bzip2 images.tar
# download images.tar.bz2 from the workspace
```

Note: As a reference, generating 12 composites for 6 time slots at 2 km resolution takes ~20 minutes.

---

## Key contents
- `download.py` — utilities for retrieving data from EUMETSAT / WEkEO APIs  
- `Lab10_FCI_data_display/` — FCI RGB visualization lab  
- `Lab11_LI_data_display/` — MTG Lightning Imager visualization  
- `fire-monitoring/` — fire detection exercises and case studies  
- `lsa-saf/` — Land Surface Analysis (LST, DUST) products  
- `HSAF/` — Precipitation & Hydrology SAF products  
- `dust-monitoring/` — dust optical depth & visualization exercises

---

## About the school
The Autumn School brings together students and professionals to apply satellite remote sensing to operational and research problems in meteorology, hydrology, and climate. The program balances concise theory with hands‑on labs using tools like EUMETView, ADAGUC, LSASAF, and HSAF.

---

## Author
Niklas Viebig  
MSc Physics, ETH Zürich  
Interests: climate modelling, exoplanet atmospheres, differentiable Earth‑system simulations.
