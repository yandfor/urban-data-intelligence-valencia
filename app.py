"""
Urban Data Intelligence - Valencia
app.py · Main Streamlit application

Structure:
    - Data loading (cached)
    - Sidebar: navigation + contextual filters
    - Section 1: Interactive map (UQI + individual indicators)
    - Section 2: Dashboard (rankings + neighbourhood breakdown)
    - Section 3: Clustering (KMeans + map + scatter)
    - Section 4: Simulator (sliders + before/after + updated map)

Data source: uqi_barrios.geojson (generated in limpieza_datos.ipynb)
"""

import streamlit as st
import geopandas as gpd
import plotly.express as px
import json
import pandas as pd

st.set_page_config(
    page_title="Urban Data Intelligence - Valencia",
    page_icon="https://cdn-icons-png.flaticon.com/128/32/32226.png",
    layout="wide",
)


@st.cache_data
def load_data():
    gdf = gpd.read_file("uqi_barrios.geojson")
    # Convert to WGS84 so Plotly can render it
    gdf = gdf.to_crs("EPSG:4326")
    # Convert to standard GeoJSON (format accepted by Plotly)
    geojson = json.loads(gdf.to_json())
    return gdf, geojson

gdf, geojson = load_data()


# -------------- INDICATOR DEFINITIONS -----------

INDICATORS = {
    "UQI": {
        "col"  : "UQI",
        "label": "Urban Quality Index (UQI)",
        "desc" : "Composite index combining air quality, complaints, noise, services and mobility.",
    },
    "Air": {
        "col"  : "Air_Quality_Score",
        "label": "Air Quality",
        "desc" : "Score based on PM2.5, PM10, NO2 and O3. Higher score = cleaner air.",
    },
    "Complaints": {
        "col"  : "Complaints_Score",
        "label": "Citizen Complaints",
        "desc" : "Number of incidents registered at City Hall. Higher score = fewer complaints.",
    },
    "Noise": {
        "col"  : "Noise_Score",
        "label": "Urban Noise",
        "desc" : "Weighted noise level (day/evening/night). Higher score = quieter neighbourhood.",
    },
    "Services": {
        "col"  : "Services_Score",
        "label": "Municipal Services",
        "desc" : "Density of public services per neighbourhood. Higher score = better equipped.",
    },
    "Mobility": {
        "col"  : "Mobility_Score",
        "label": "Sustainable Mobility (Valenbisi)",
        "desc" : "Valenbisi station capacity per neighbourhood. Higher score = more accessible.",
    },
}

COL_LABELS = {
    "Air_Quality_Score" : "Air",
    "Complaints_Score"  : "Complaints",
    "Noise_Score"       : "Noise",
    "Services_Score"    : "Services",
    "Mobility_Score"    : "Mobility",
}

#------------- SIDEBAR -----------

with st.sidebar:
    st.title("Urban Data Intelligence")
    st.caption("Valencia, 2016-2021")
    st.divider()

    section = st.radio(
        "Section",
        options=["Interactive Map", "Dashboard", "Clustering", "Simulator"],
    )
    st.divider()

    if section == "Interactive Map":
        st.subheader("Map options")

        indicator_key = st.selectbox(
            "Indicator",
            options=list(INDICATORS.keys()),
            index=0,
        )

        palette = st.selectbox(
            "Colour palette",
            options=["RdYlGn", "Blues", "Plasma", "Viridis"],
            index=0,
            help="RdYlGn: red (worst), green (best)"
        )

        opacity = st.slider("Map opacity", 0.3, 1.0, 0.75, 0.05)
    
    elif section == "Clustering":
        st.subheader("Clustering options")

        n_clusters = st.slider(
            "Number of clusters", min_value=2, max_value=8, value=4,
            help="Higher values produce more granular groups."
        )
        x_axis = st.selectbox(
            "Scatter X axis", options=list(COL_LABELS.values()), index=0
        )
        y_axis = st.selectbox(
            "Scatter Y axis", options=list(COL_LABELS.values()), index=2
        )


# -------------- SECTION 1 – INTERACTIVE MAP ------------


if section == "Interactive Map":

    ind   = INDICATORS[indicator_key]
    col   = ind["col"]
    label = ind["label"]
    desc  = ind["desc"]

   
    st.title("Valencia Interactive Map")
    st.caption(f"**{label}** - {desc}")
    st.divider()

    c1, c2, c3, c4 = st.columns(4) #summary metrics 

    neighbourhood_max = gdf.loc[gdf[col].idxmax(), "barrio"]
    neighbourhood_min = gdf.loc[gdf[col].idxmin(), "barrio"]

    c1.metric("Valencia average", f"{gdf[col].mean():.1f}")
    c2.metric("Highest",          f"{gdf[col].max():.1f}", neighbourhood_max)
    c3.metric("Lowest",           f"{gdf[col].min():.1f}", neighbourhood_min)
    c4.metric("Neighbourhoods without data",
              int(gdf[col].isna().sum()),
              help="Neighbourhoods with neutral score due to missing coverage in the source data")

    st.divider()

    # choroplete map 
    fig = px.choropleth_mapbox(
        gdf,
        geojson=geojson,
        locations=gdf.index,
        color=col,
        color_continuous_scale=palette,
        mapbox_style="carto-positron",
        zoom=11,
        center={"lat": 39.469, "lon": -0.376},
        opacity=opacity,
        hover_name="barrio",
        hover_data={
            col                   : ":.1f",
            "Air_Quality_Score"   : ":.1f",
            "Complaints_Score"    : ":.1f",
            "Noise_Score"         : ":.1f",
            "Services_Score"      : ":.1f",
            "Mobility_Score"      : ":.1f",
        },
        labels={
            col                   : label,
            "Air_Quality_Score"   : "Air",
            "Complaints_Score"    : "Complaints",
            "Noise_Score"         : "Noise",
            "Services_Score"      : "Services",
            "Mobility_Score"      : "Mobility",
        },
    )

    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        coloraxis_colorbar=dict(
            title=indicator_key,
            thickness=15,
            len=0.6,
        ),
        height=580,
    )

    st.plotly_chart(fig, use_container_width=True)

    with st.expander("View neighbourhood ranking"):    # ranking table 
        df_ranking = (
            gdf[["barrio", col]]
            .sort_values(col, ascending=False)
            .reset_index(drop=True)
        )
        df_ranking.index += 1
        df_ranking.columns = ["Neighbourhood", label]
        st.dataframe(df_ranking, use_container_width=True)

# -------------- SECTION 2 – DASHBOARD ------------

elif section == "Dashboard":

    import plotly.graph_objects as go

    st.title("Dashboard")
    st.caption("Explore neighbourhood rankings and individual score breakdowns.")
    st.divider()

    #Bar chart: top/bottom  
    st.subheader("Neighbourhood Ranking")

    col_left, col_right = st.columns([2, 1])

    with col_right:
        rank_indicator = st.selectbox(
            "Indicator",
            options=list(INDICATORS.keys()),
            key="dash_indicator"
        )
        n_bars = st.slider("Number of neighbourhoods", 5, 20, 10)
        show = st.radio("Show", ["Top", "Bottom", "Both"], horizontal=True)

    rank_col   = INDICATORS[rank_indicator]["col"]
    rank_label = INDICATORS[rank_indicator]["label"]

    df_sorted = (
        gdf[["barrio", rank_col]]
        .dropna()
        .sort_values(rank_col, ascending=False)
        .reset_index(drop=True)
    )
    df_sorted.columns = ["Neighbourhood", rank_label]

    with col_left:
        if show == "Top":
            df_plot = df_sorted.head(n_bars)
            title   = f"Top {n_bars} neighbourhoods · {rank_label}"
        elif show == "Bottom":
            df_plot = df_sorted.tail(n_bars).sort_values(rank_label)
            title   = f"Bottom {n_bars} neighbourhoods · {rank_label}"
        else:
            df_top    = df_sorted.head(n_bars).copy()
            df_top["Group"] = "Top"
            df_bottom = df_sorted.tail(n_bars).sort_values(rank_label).copy()
            df_bottom["Group"] = "Bottom"
            df_plot = pd.concat([df_bottom, df_top])
            title   = f"Top & Bottom {n_bars} neighbourhoods · {rank_label}"

        if show != "Both":
            fig_bar = px.bar(
                df_plot,
                x=rank_label,
                y="Neighbourhood",
                orientation="h",
                color=rank_label,
                color_continuous_scale="RdYlGn",
                title=title,
            )
        else:
            fig_bar = px.bar(
                df_plot,
                x=rank_label,
                y="Neighbourhood",
                orientation="h",
                color="Group",
                color_discrete_map={"Top": "#2ecc71", "Bottom": "#e74c3c"},
                title=title,
            )

        fig_bar.update_layout(
            height=420,
            showlegend=show == "Both",
            coloraxis_showscale=show != "Both",
            yaxis={"categoryorder": "total ascending"},
            margin={"t": 40, "b": 0, "l": 0, "r": 0},
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()

    #radar chart: individual neighbourhood breakdown 
    st.subheader("Neighbourhood Breakdown")

    radar_cols = [
        ("Air_Quality_Score", "Air"),
        ("Complaints_Score",  "Complaints"),
        ("Noise_Score",       "Noise"),
        ("Services_Score",    "Services"),
        ("Mobility_Score",    "Mobility"),
    ]

    col_sel, col_radar = st.columns([1, 2])

    with col_sel:
        selected = st.selectbox(
            "Select a neighbourhood",
            options=sorted(gdf["barrio"].dropna().tolist()),
            key="radar_barrio"
        )

        # Score table for the selected neighbourhood
        row = gdf[gdf["barrio"] == selected].iloc[0]
        st.markdown(f"**UQI: {row['UQI']:.1f}**")
        st.markdown("---")
        for col_name, col_display in radar_cols:
            val = row[col_name]
            st.metric(col_display, f"{val:.1f}")

    with col_radar:
        row        = gdf[gdf["barrio"] == selected].iloc[0]
        categories = [d for _, d in radar_cols]
        values     = [row[c] for c, _ in radar_cols]

        # Close the polygon by repeating the first value
        categories_closed = categories + [categories[0]]
        values_closed     = values     + [values[0]]

        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=values_closed,
            theta=categories_closed,
            fill="toself",
            fillcolor="rgba(46, 204, 113, 0.2)",
            line=dict(color="#2ecc71", width=2),
            name=selected,
        ))
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100])
            ),
            showlegend=False,
            title=f"{selected.title()} · Score breakdown",
            height=400,
            margin={"t": 60, "b": 20, "l": 40, "r": 40},
        )
        st.plotly_chart(fig_radar, use_container_width=True)

# ------- SECTION 3 – CLUSTERING ---------------

elif section == "Clustering":

    from sklearn.preprocessing import StandardScaler
    from sklearn.cluster import KMeans
    import plotly.graph_objects as go
    import pandas as pd

    st.title("Neighbourhood Clustering")
    st.caption("Group neighbourhoods by similarity across all urban indicators using KMeans.")
    st.divider()

    SCORE_COLS = [
        "Air_Quality_Score",
        "Complaints_Score",
        "Noise_Score",
        "Services_Score",
        "Mobility_Score",
    ]

    
    df_cluster = gdf[["barrio"] + SCORE_COLS].dropna().copy()   #KMeans 

    scaler   = StandardScaler()
    X_scaled = scaler.fit_transform(df_cluster[SCORE_COLS])

    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    df_cluster["Cluster"] = kmeans.fit_predict(X_scaled).astype(str)

    gdf_plot = gdf.merge(df_cluster[["barrio", "Cluster"]], on="barrio", how="left")

    # Cluster summary table 
    st.subheader("Cluster profiles")
    st.caption("Mean score per indicator for each cluster.")

    df_summary = (
        df_cluster
        .groupby("Cluster")[SCORE_COLS]
        .mean()
        .round(1)
        .rename(columns=COL_LABELS)
        .reset_index()
    )
    df_summary.columns = ["Cluster"] + list(COL_LABELS.values())
    st.dataframe(df_summary, use_container_width=True, hide_index=True)

    st.divider()

    # Cluster interpretation 
    st.subheader("Cluster interpretation")

    df_cluster_uqi = gdf_plot[["Cluster", "UQI"]].dropna()

    metric_cols = st.columns(n_clusters)
    for i, col_m in enumerate(metric_cols):
        cluster_id = str(i)
        n_barrios  = len(df_cluster[df_cluster["Cluster"] == cluster_id])
        uqi_mean   = df_cluster_uqi[df_cluster_uqi["Cluster"] == cluster_id]["UQI"].mean()
        col_m.metric(
            label=f"Cluster {i}",
            value=f"UQI {uqi_mean:.1f}" if not pd.isna(uqi_mean) else "UQI —",
            delta=f"{n_barrios} neighbourhoods",
            delta_color="off",
        )

    def interpret_cluster(row):
        """
        Generates an automatic text interpretation of a cluster
        based on the mean scores of its five indicators.
        Returns a tuple (title, description).
        """
        air        = row["Air_Quality_Score"]
        complaints = row["Complaints_Score"]
        noise      = row["Noise_Score"]
        services   = row["Services_Score"]
        mobility   = row["Mobility_Score"]

        scores = {
            "air quality"   : air,
            "few complaints": complaints,
            "low noise"     : noise,
            "services"      : services,
            "mobility"      : mobility,
        }
        strengths  = [k for k, v in scores.items() if v >= 60]
        weaknesses = [k for k, v in scores.items() if v <= 40]

        uqi = (air * 0.25 + complaints * 0.20 +
               noise * 0.20 + services * 0.20 + mobility * 0.15)

        if uqi >= 60:
            title = "🟢 High urban quality"
        elif uqi >= 45:
            title = "🟡 Moderate urban quality"
        else:
            title = "🔴 Low urban quality"

        parts = []
        if strengths:
            parts.append(f"Strong in **{', '.join(strengths)}**.")
        if weaknesses:
            parts.append(f"Needs improvement in **{', '.join(weaknesses)}**.")
        if not strengths and not weaknesses:
            parts.append("Balanced across all indicators, close to the city average.")

        if mobility <= 35 and services <= 35:
            parts.append("Profile typical of peripheral or rural neighbourhoods.")
        elif air <= 35 and noise <= 35:
            parts.append("Profile typical of dense urban or high-traffic areas.")
        elif services >= 65 and mobility >= 65:
            parts.append("Well-connected central neighbourhood with good public infrastructure.")

        return title, " ".join(parts)

    card_cols = st.columns(n_clusters)
    for i, col_c in enumerate(card_cols):
        cluster_id = str(i)
        row        = df_summary[df_summary["Cluster"] == cluster_id].iloc[0]

        row_scores = pd.Series({
            "Air_Quality_Score" : row["Air"],
            "Complaints_Score"  : row["Complaints"],
            "Noise_Score"       : row["Noise"],
            "Services_Score"    : row["Services"],
            "Mobility_Score"    : row["Mobility"],
        })

        title, desc = interpret_cluster(row_scores)

        with col_c:
            st.markdown(f"**Cluster {i} · {title}**")
            st.caption(desc)

    st.divider()

    #  Map + Scatter 
    map_col, scatter_col = st.columns(2)

    CLUSTER_COLORS = [
        "#2ecc71", "#e74c3c", "#3498db", "#f39c12",
        "#9b59b6", "#1abc9c", "#e67e22", "#e91e63"
    ]
    color_map = {str(i): CLUSTER_COLORS[i] for i in range(n_clusters)}

    with map_col:
        st.markdown("**Map coloured by cluster**")

        geojson_cluster = json.loads(gdf_plot.to_json())

        fig_map = px.choropleth_mapbox(
            gdf_plot,
            geojson=geojson_cluster,
            locations=gdf_plot.index,
            color="Cluster",
            color_discrete_map=color_map,
            mapbox_style="carto-positron",
            zoom=10.5,
            center={"lat": 39.469, "lon": -0.376},
            opacity=0.75,
            hover_name="barrio",
            hover_data={"Cluster": True, "UQI": ":.1f"},
        )
        fig_map.update_layout(
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            height=450,
            legend=dict(title="Cluster", orientation="v"),
        )
        st.plotly_chart(fig_map, use_container_width=True)

    with scatter_col:
        st.markdown(f"**{x_axis} vs {y_axis}**")

        labels_inv = {v: k for k, v in COL_LABELS.items()}
        x_col = labels_inv[x_axis]
        y_col = labels_inv[y_axis]

        fig_scatter = px.scatter(
            df_cluster,
            x=x_col,
            y=y_col,
            color="Cluster",
            color_discrete_map=color_map,
            hover_name="barrio",
            hover_data={
                "Cluster"           : True,
                "Air_Quality_Score" : ":.1f",
                "Complaints_Score"  : ":.1f",
                "Noise_Score"       : ":.1f",
                "Services_Score"    : ":.1f",
                "Mobility_Score"    : ":.1f",
            },
            labels={x_col: x_axis, y_col: y_axis},
        )
        fig_scatter.update_traces(marker=dict(size=9, opacity=0.85))
        fig_scatter.update_layout(
            height=450,
            margin={"t": 20, "b": 0, "l": 0, "r": 0},
            legend=dict(title="Cluster"),
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    st.divider()

    #  Neighbourhood list per cluster 
    st.subheader("Neighbourhoods per cluster")

    tabs = st.tabs([f"Cluster {i}" for i in range(n_clusters)])

    for i, tab in enumerate(tabs):
        with tab:
            df_tab = (
                df_cluster[df_cluster["Cluster"] == str(i)][["barrio"] + SCORE_COLS]
                .rename(columns={"barrio": "Neighbourhood", **COL_LABELS})
                .sort_values("Neighbourhood")
                .reset_index(drop=True)
            )
            st.dataframe(df_tab, use_container_width=True, hide_index=True)
 
# ---------------------- SECTION 4 – SIMULATOR ---------------------

elif section == "Simulator":

    import plotly.graph_objects as go
    import pandas as pd

    st.title("Urban Improvement Simulator")
    st.caption("Adjust individual indicators and see the impact on the Urban Quality Index in real time.")
    st.divider()

    # Configuration 
    WEIGHTS = {
        "Air_Quality_Score" : 0.25,
        "Complaints_Score"  : 0.20,
        "Noise_Score"       : 0.20,
        "Services_Score"    : 0.20,
        "Mobility_Score"    : 0.15,
    }

    LABELS = {
        "Air_Quality_Score" : "Air Quality",
        "Complaints_Score"  : "Complaints",
        "Noise_Score"       : "Noise",
        "Services_Score"    : "Services",
        "Mobility_Score"    : "Mobility",
    }

    #target selection 
    st.subheader(" Select target")

    target_mode = st.radio(
        "Apply improvements to",
        options=["Single neighbourhood", "All neighbourhoods"],
        horizontal=True,
    )

    if target_mode == "Single neighbourhood":
        selected_barrio = st.selectbox(
            "Neighbourhood",
            options=sorted(gdf["barrio"].dropna().tolist()),
        )
        df_sim = gdf[gdf["barrio"] == selected_barrio].copy()
    else:
        selected_barrio = None
        df_sim = gdf.copy()

    st.divider()

    st.subheader("Set improvement targets")
    st.caption("Each slider adds percentage points to the current score (capped at 100).")

    slider_cols = st.columns(5)
    improvements = {}

    for i, (col_name, col_label) in enumerate(LABELS.items()):
        with slider_cols[i]:
            improvements[col_name] = st.slider(
                f"**{col_label}**",
                min_value=0,
                max_value=50,
                value=0,
                step=5,
                format="+%d pts",
                key=f"sim_{col_name}",
            )

    st.divider()

    # compute simulated scores 
    df_sim = df_sim.copy()

    for col_name, delta in improvements.items():
        df_sim[f"{col_name}_sim"] = (df_sim[col_name] + delta).clip(upper=100)

    df_sim["UQI_sim"] = sum(
        df_sim[f"{col_name}_sim"] * weight
        for col_name, weight in WEIGHTS.items()
    ).round(2)

    df_sim["UQI_delta"] = (df_sim["UQI_sim"] - df_sim["UQI"]).round(2)

    st.subheader("Impact summary")

    if target_mode == "Single neighbourhood":
        row = df_sim.iloc[0]
        m1, m2, m3 = st.columns(3)
        m1.metric("Current UQI",   f"{row['UQI']:.1f}")
        m2.metric("Simulated UQI", f"{row['UQI_sim']:.1f}",
                  delta=f"{row['UQI_delta']:+.1f} pts")
        m3.metric("City average UQI", f"{gdf['UQI'].mean():.1f}",
                  help="Current city average for reference")
    else:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Current avg UQI",   f"{gdf['UQI'].mean():.1f}")
        m2.metric("Simulated avg UQI", f"{df_sim['UQI_sim'].mean():.1f}",
                  delta=f"{df_sim['UQI_delta'].mean():+.1f} pts")
        m3.metric("Most improved",
                  df_sim.loc[df_sim["UQI_delta"].idxmax(), "barrio"].title(),
                  delta=f"{df_sim['UQI_delta'].max():+.1f} pts")
        m4.metric("Neighbourhoods improved",
                  int((df_sim["UQI_delta"] > 0).sum()))

    st.divider()

    #  Before / After comparison 
    st.subheader(" Before / After comparison")

    if target_mode == "Single neighbourhood":
        # Radar chart before vs after for the selected neighbourhood
        row        = df_sim.iloc[0]
        categories = list(LABELS.values())
        before     = [row[c] for c in LABELS]
        after      = [row[f"{c}_sim"] for c in LABELS]

        categories_closed = categories + [categories[0]]
        before_closed     = before     + [before[0]]
        after_closed      = after      + [after[0]]

        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=before_closed, theta=categories_closed,
            fill="toself", name="Current",
            fillcolor="rgba(231, 76, 60, 0.15)",
            line=dict(color="#e74c3c", width=2),
        ))
        fig_radar.add_trace(go.Scatterpolar(
            r=after_closed, theta=categories_closed,
            fill="toself", name="Simulated",
            fillcolor="rgba(46, 204, 113, 0.15)",
            line=dict(color="#2ecc71", width=2, dash="dash"),
        ))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            title=f"{selected_barrio.title()} · Current vs Simulated",
            height=420,
            margin={"t": 60, "b": 20, "l": 40, "r": 40},
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    else:
        # Bar chart of UQI delta for all neighbourhoods
        df_delta = (
            df_sim[["barrio", "UQI", "UQI_sim", "UQI_delta"]]
            .sort_values("UQI_delta", ascending=False)
            .reset_index(drop=True)
        )
        fig_bar = px.bar(
            df_delta,
            x="UQI_delta",
            y="barrio",
            orientation="h",
            color="UQI_delta",
            color_continuous_scale="RdYlGn",
            labels={"UQI_delta": "UQI change", "barrio": "Neighbourhood"},
            title="UQI improvement per neighbourhood",
            hover_data={"UQI": ":.1f", "UQI_sim": ":.1f", "UQI_delta": ":.1f"},
        )
        fig_bar.update_layout(
            height=700,
            margin={"t": 40, "b": 0, "l": 0, "r": 0},
            yaxis={"categoryorder": "total ascending"},
            coloraxis_showscale=False,
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()

    # Updated map 
    st.subheader("Simulated UQI map")

    # Merge simulated UQI back into the full GeoDataFrame for the map
    gdf_map_sim = gdf.merge(
        df_sim[["barrio", "UQI_sim"]],
        on="barrio",
        how="left"
    )
    # Neighbourhoods not in the simulation keep their original UQI
    gdf_map_sim["UQI_display"] = gdf_map_sim["UQI_sim"].fillna(gdf_map_sim["UQI"])

    geojson_sim = json.loads(gdf_map_sim.to_json())

    fig_map = px.choropleth_mapbox(
        gdf_map_sim,
        geojson=geojson_sim,
        locations=gdf_map_sim.index,
        color="UQI_display",
        color_continuous_scale="RdYlGn",
        mapbox_style="carto-positron",
        zoom=11,
        center={"lat": 39.469, "lon": -0.376},
        opacity=0.75,
        hover_name="barrio",
        hover_data={
            "UQI"        : ":.1f",
            "UQI_display": ":.1f",
            "UQI_sim"    : ":.1f",
        },
        labels={
            "UQI_display": "Simulated UQI",
            "UQI"        : "Current UQI",
            "UQI_sim"    : "Simulated UQI",
        },
    )
    fig_map.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        height=520,
        coloraxis_colorbar=dict(title="UQI", thickness=15, len=0.6),
    )
    st.plotly_chart(fig_map, use_container_width=True)