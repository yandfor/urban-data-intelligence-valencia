# Urban Data Intelligence – Valencia

An interactive data application that analyses the city of Valencia through open data,
generating an **Urban Quality Index (UQI)** per neighbourhood and visualising it through
maps, dashboards, clustering and an improvement simulator.

---

##  Project structure

limpieza_datos.ipynb       # Data cleaning and feature engineering pipeline

app.py                     # Main Streamlit application

uqi_barrios.geojson        # Master dataset (output of the notebook)

uqi_barrios.csv            # Same data in tabular format

---

##  Data sources

All datasets are publicly available at [opendata.vlci.valencia.es](https://opendata.vlci.valencia.es).

| Dataset | Description |
|---|---|
| `calidad_aire.csv` | Hourly air quality measurements · 12 stations · 2016–2021 |
| `quejas.csv` | Citizen complaints registered at City Hall |
| `barris.geojson` | Administrative neighbourhood boundaries (88 neighbourhoods) |
| `mapa_soroll_dia/vesprada/nit.geojson` | Urban noise map by time slot (EU Directive 2002/49/CE) |
| `equipaments_municipals.geojson` | Municipal public services and facilities |
| `disponibilitat_valenbisi.geojson` | Valenbisi public bike stations and capacity |
| `ubicacio_estacions.geojson` | Air quality station locations and coordinates |

---

## Methodology

The UQI is a weighted composite index (0–100) built from five dimensions:

| Indicator | Weight | Description |
|---|---|---|
| Air Quality Score | 25% | Based on PM2.5, PM10, NO2 and O3 |
| Complaints Score | 20% | Inverse of citizen complaints per neighbourhood |
| Noise Score | 20% | Weighted average of day/evening/night noise levels |
| Services Score | 20% | Density of municipal facilities per neighbourhood |
| Mobility Score | 15% | Valenbisi station capacity per neighbourhood |

All scores are normalised to [0, 100] using MinMax scaling before aggregation.  
Higher score always means better urban quality.

---

## Score details & missing data handling

**Air Quality Score (25%)** - Built from PM2.5, PM10, NO2 and O3 measured across 10 monitoring stations (2016–2021). Normalised with MinMax scaling and inverted so that 100 = cleanest air. Since 10 stations cannot individually cover 88 neighbourhoods, each neighbourhood inherits the score of its nearest station via spatial join.

**Complaints Score (20%)** - Based on the number of citizen complaints registered at City Hall (~90,000 records). The scale is inverted: fewer complaints = higher score. Rafalell-Vistabella, with zero registered complaints, receives a score of 100 (absence of complaints is a positive signal).

**Noise Score (20%)** - Combines day, evening and night noise maps with weights 0.40 / 0.35 / 0.25. Real data only covers 24 of the 88 neighbourhoods (27%); the remaining 64 receive a neutral score of 50, flagged internally via `ruido_con_dato` for transparency.

**Services Score (20%)** - Density of municipal facilities (libraries, civic centres, schools…) per neighbourhood, after discarding unclassified categories. 5 neighbourhoods with no registered facilities receive a score of 0, as this reflects real absence rather than a coverage gap.

**Mobility Score (15%)** - Total Valenbisi station capacity per neighbourhood. 19 neighbourhoods without service (mostly rural hamlets) receive a score of 0.

**Missing data criteria summary**

| Indicator | Cause of missing data | Assigned value | Rationale |
|---|---|---|---|
| Complaints | No complaints registered | 100 | Absence is a positive signal |
| Noise | No coverage in the noise map | 50 | Source limitation, not a neighbourhood trait |
| Services | No facilities present | 0 | Real, verifiable absence |
| Mobility | No stations present | 0 | Real, verifiable absence |

The final **UQI** is the weighted sum of all five scores, scaled between 0 and 100. Current city-wide average across Valencia's 88 neighbourhoods: **43.7**.

---

## Known limitations

- **Air quality**: only 10 measurement stations cover 88 neighbourhoods. Each neighbourhood is assigned the score of its nearest station via spatial join.
- **Noise**: the municipal noise map covers only 24 of the 88 neighbourhoods (27%). The remaining 64 receive a neutral score of 50.
- **Analysis period**: 2016–2021. Data beyond 2021 is not included as air quality records do not extend further.

---

## How to run

**1. Install dependencies**

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**2. Run the notebook**

Open `limpieza_datos.ipynb` and run all cells. This generates `uqi_barrios.geojson` and `uqi_barrios.csv`.

**3. Launch the app**

```bash
streamlit run app.py
```

---

## Requirements

pandas
geopandas
numpy
scikit-learn
streamlit
plotly
shapely
pyogrio

---

## App sections

| Section | Description |
|---|---|
| Interactive Map | Choropleth map coloured by UQI or any individual indicator |
| Dashboard | Neighbourhood rankings and individual score breakdown |
| Clustering | KMeans grouping of similar neighbourhoods with map and scatter plot |
| Simulator | Adjust indicators and see the real-time impact on the UQI |
