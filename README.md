# Urban Data Intelligence – Valencia

An interactive data application that analyses the city of Valencia through open data,
generating an **Urban Quality Index (UQI)** per neighbourhood and visualising it through
maps, dashboards, clustering and an improvement simulator.

---

##  Project structure

├── limpieza_datos.ipynb       # Data cleaning and feature engineering pipeline
├── app.py                     # Main Streamlit application
├── uqi_barrios.geojson        # Master dataset (output of the notebook)
├── uqi_barrios.csv            # Same data in tabular format
└── README.md

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

## Known limitations

- **Air quality**: only 10 measurement stations cover 88 neighbourhoods. Each neighbourhood is assigned the score of its nearest station via spatial join.
- **Noise**: the municipal noise map covers only 24 of the 88 neighbourhoods (27%). The remaining 64 receive a neutral score of 50.
- **Complaints**: 16 peripheral neighbourhoods have no registered complaints, receiving a neutral score via median imputation.
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

---

## Author

Built as part of a data engineering and visualisation project at **Universitat Politècnica de València (UPV)**.  
Data period: 2016 – 2021.