# ================================================
# PhonePe Pulse Dashboard — 3D Visualizations
# Rewritten from your original `streamlit.py` to use 3D plots
# ================================================
import subprocess
subprocess.check_call(["pip", "install", "streamlit", "plotly", "sqlalchemy", "psycopg2-binary", "streamlit-option-menu", "requests"])

# Libraries
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from streamlit_option_menu import option_menu
from sqlalchemy import create_engine
import psycopg2
import requests
import json
from typing import Dict, Tuple, Any, List, Optional, Union

# -----------------------------
# DB Connection (same as original)
# -----------------------------
url = "postgresql://neondb_owner:npg_bpCADu5V4PsM@ep-purple-bird-a1wedpb9.ap-southeast-1.aws.neon.tech/phonepe_pulse?sslmode=require&channel_binding=require"
engine = create_engine(url)

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(page_title="PhonePe Pulse Dashboard — 3D", layout="wide")

# -----------------------------
# Styling / helper utilities
# -----------------------------
def add_cat_index(df: pd.DataFrame, col: str, sort: bool = True, name: str = "cat_idx") -> pd.DataFrame:
    """
    Create a numeric index column from a categorical column for use in 3D plots.
    Keeps the original labels in a separate column for hover/tooltips.
    """
    out = df.copy()
    cats = sorted(out[col].astype(str).unique()) if sort else list(out[col].astype(str).unique())
    mapping = {c: i for i, c in enumerate(cats, start=1)}
    out[name] = out[col].astype(str).map(mapping)
    out[f"{col}_label"] = out[col].astype(str)
    return out

def scatter3d(
    df: pd.DataFrame,
    x: str, y: str, z: str,
    color: Optional[str] = None,
    size: Optional[str] = None,
    title: str = "",
    x_title: str = "",
    y_title: str = "",
    z_title: str = "",
    text: Optional[Union[str, List[str]]] = None,
    showlegend: bool = True
):
    """
    Generic 3D scatter builder with sensible defaults for Streamlit.
    """
    fig = px.scatter_3d(
        df, x=x, y=y, z=z, color=color, size=size, text=text,
        hover_data={x: True, y: True, z: True} if text is None else None
    )
    fig.update_traces(marker=dict(opacity=0.85))
    fig.update_layout(
        title=title,
        scene=dict(
            xaxis_title=x_title or x,
            yaxis_title=y_title or y,
            zaxis_title=z_title or z,
        ),
        legend_title_text=color if color else None,
        showlegend=showlegend,
        margin=dict(l=0, r=0, t=50, b=0),
    )
    return fig

# -----------------------------
# Simple centroid extraction for GeoJSON polygons
# (approximate; averages coordinates — good enough for column map)
# -----------------------------
def _avg_point_list(coords: List[List[float]]) -> Tuple[float, float]:
    # coords: [[lon, lat], ...]
    if not coords:
        return (0.0, 0.0)
    lons = [p[0] for p in coords]
    lats = [p[1] for p in coords]
    return (sum(lons) / len(lons), sum(lats) / len(lats))

def _flatten_polygon_coords(geom: Dict[str, Any]) -> List[List[float]]:
    # Handles Polygon and MultiPolygon
    typ = geom.get("type", "")
    coords = geom.get("coordinates", [])
    flat: List[List[float]] = []
    if typ == "Polygon":
        # coords -> [ring][[lon,lat]]
        for ring in coords:
            flat.extend(ring)
    elif typ == "MultiPolygon":
        # coords -> [polygon][ring][[lon,lat]]
        for poly in coords:
            for ring in poly:
                flat.extend(ring)
    return flat

def geojson_state_centroids(geojson: Dict[str, Any], state_key: str = "ST_NM") -> Dict[str, Tuple[float, float]]:
    centroids: Dict[str, Tuple[float, float]] = {}
    for feat in geojson.get("features", []):
        props = feat.get("properties", {})
        name = props.get(state_key)
        geom = feat.get("geometry", {})
        points = _flatten_polygon_coords(geom)
        lon, lat = _avg_point_list(points)
        if name:
            centroids[name] = (lon, lat)
    return centroids

# -----------------------------
# Nav
# -----------------------------
selected = option_menu(
    menu_title='Welcome To Phonepepulse — 3D',
    options=["🏠 Home", "📊 Pulse Insights (3D)", "📄 Docs"],
    icons=["house", "bar-chart-line", "file-earmark-text"],
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "#3d1a6e"},
        "nav-link": {"color": "white", "font-size": "16px", "margin": "0 20px"},
        "nav-link-selected": {"color": "#a370f7", "font-weight": "bold"},
    }
)

# -----------------------------
# Home
# -----------------------------
if selected == "🏠 Home":
    st.title("📱PhonePe — 3D Pulse")
    st.markdown("""
    Experience your existing PhonePe Pulse insights in **interactive 3D**.
    Rotate, zoom, and hover to explore the same metrics with added depth.
    """)
    st.success("Use the top menu to jump into the 3D dashboards.")

# -----------------------------
# Pulse Insights — 3D
# -----------------------------
elif selected == "📊 Pulse Insights (3D)":
    st.title("📊 Explore Transaction Data Insights — 3D")

    scenario = st.sidebar.selectbox("📌 Select Scenario", [
        "1. Transaction Dynamics on PhonePe (3D)",
        "2. Device Dominance and User Engagement Analysis (3D)",
        "3. Transaction Analysis (3D)",
        "4. User Registration Analysis (3D)",
        "5. Insurance Transactions Analysis (3D)"
    ])

    # -------------------------
    # 1. Transaction Dynamics
    # -------------------------
    if scenario == "1. Transaction Dynamics on PhonePe (3D)":
        q = st.selectbox("Choose a Question", [
            "I. Transaction Dynamics Across States (3D)",
            "II. Transaction Dynamics Over Quarters (3D)",
            "III. Transaction Dynamics by Payment Category (3D)",
            "IV. Growth/Stagnation Across States (3D)",
            "V. Growth/Stagnation by Transaction Type (3D)"
        ])

        # I. States
        if q == "I. Transaction Dynamics Across States (3D)":
            st.subheader("📌 Transaction Dynamics Across States (3D)")
            sql = """
            SELECT states, 
                   SUM(transaction_count) AS total_transaction_count, 
                   SUM(transaction_amount) AS total_transaction_amount 
            FROM agg_trans 
            GROUP BY states 
            ORDER BY total_transaction_amount DESC
            """
            df = pd.read_sql_query(sql, engine)

            # categorical -> numeric index for x-axis
            df = add_cat_index(df, "states", name="state_idx")
            fig = scatter3d(
                df,
                x="state_idx",
                y="total_transaction_count",
                z="total_transaction_amount",
                color="total_transaction_amount",
                size="total_transaction_count",
                title="3D: Total Transaction Amount by State",
                x_title="State (index)",
                y_title="Transaction Count",
                z_title="Transaction Amount (₹)",
                text="states_label"
            )
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df)

        # II. Quarters
        elif q == "II. Transaction Dynamics Over Quarters (3D)":
            st.subheader("📌 Transaction Dynamics Over Quarters (3D)")
            sql = """
            SELECT 
                years, 
                quarter, 
                SUM(transaction_count) AS total_transaction_count,
                SUM(transaction_amount) AS total_transaction_amount
            FROM agg_trans
            GROUP BY years, quarter
            ORDER BY years, quarter
            """
            df = pd.read_sql_query(sql, engine)
            df["period_str"] = df["years"].astype(str) + " Q" + df["quarter"].astype(str)
            df["period_idx"] = (df["years"].astype(int) - df["years"].min()) * 4 + df["quarter"].astype(int)

            fig = scatter3d(
                df,
                x="period_idx",
                y="total_transaction_count",
                z="total_transaction_amount",
                color="years",
                size="total_transaction_count",
                title="3D: Total Transaction Amount by Quarter",
                x_title="Period (indexed)",
                y_title="Transaction Count",
                z_title="Transaction Amount (₹)",
                text="period_str"
            )
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df)

        # III. By Payment Category
        elif q == "III. Transaction Dynamics by Payment Category (3D)":
            st.subheader("📌 Transaction Dynamics by Payment Category (3D)")
            sql = """
            SELECT 
                transaction_type, 
                SUM(transaction_count) AS total_trans_count, 
                SUM(transaction_amount) AS total_amount 
            FROM agg_trans 
            GROUP BY transaction_type 
            ORDER BY total_amount DESC
            """
            df = pd.read_sql_query(sql, engine)
            df = add_cat_index(df, "transaction_type", name="type_idx")

            fig = scatter3d(
                df,
                x="type_idx",
                y="total_trans_count",
                z="total_amount",
                color="total_amount",
                size="total_trans_count",
                title="3D: Total Transaction Amount by Payment Category",
                x_title="Payment Category (index)",
                y_title="Transaction Count",
                z_title="Transaction Amount (₹)",
                text="transaction_type_label"
            )
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df)

        # IV. State Trends
        elif q == "IV. Growth/Stagnation Across States (3D)":
            st.subheader("📌 Growth/Stagnation Across States (3D)")
            sql = """
            SELECT 
                states, 
                years,
                quarter,
                SUM(transaction_amount) AS total_amount 
            FROM agg_trans 
            GROUP BY states, years, quarter 
            ORDER BY states, years, quarter
            """
            df = pd.read_sql_query(sql, engine)
            df["period_idx"] = (df["years"].astype(int) - df["years"].min()) * 4 + df["quarter"].astype(int)
            df = add_cat_index(df, "states", name="state_idx")

            # line-like effect by sorting within each state
            df = df.sort_values(["states", "period_idx"])

            fig = px.scatter_3d(
                df,
                x="period_idx", y="state_idx", z="total_amount",
                color="states",
                text=None
            )
            fig.update_traces(mode="lines+markers", marker=dict(size=3, opacity=0.85))
            fig.update_layout(
                title="3D: Transaction Growth Trend Across States (Quarterly)",
                scene=dict(
                    xaxis_title="Period (indexed)",
                    yaxis_title="State (index)",
                    zaxis_title="Transaction Amount (₹)",
                ),
                margin=dict(l=0, r=0, t=50, b=0)
            )
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df)

        # V. Type Trends
        elif q == "V. Growth/Stagnation by Transaction Type (3D)":
            st.subheader("📌 Growth/Stagnation by Transaction Type (3D)")
            sql = """
            SELECT 
                transaction_type, 
                years, 
                quarter,
                SUM(transaction_amount) AS transaction_amount  
            FROM agg_trans 
            GROUP BY transaction_type, years, quarter 
            ORDER BY transaction_type, years, quarter
            """
            df = pd.read_sql_query(sql, engine)
            df["period_idx"] = (df["years"].astype(int) - df["years"].min()) * 4 + df["quarter"].astype(int)
            df = add_cat_index(df, "transaction_type", name="type_idx")
            df = df.sort_values(["transaction_type", "period_idx"])

            fig = px.scatter_3d(
                df,
                x="period_idx", y="type_idx", z="transaction_amount",
                color="transaction_type",
            )
            fig.update_traces(mode="lines+markers", marker=dict(size=3, opacity=0.85))
            fig.update_layout(
                title="3D: Transaction Trend by Payment Category Over Time",
                scene=dict(
                    xaxis_title="Period (indexed)",
                    yaxis_title="Payment Category (index)",
                    zaxis_title="Transaction Amount (₹)",
                ),
                margin=dict(l=0, r=0, t=50, b=0)
            )
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df)

    # -------------------------
    # 2. Device Dominance & Engagement
    # -------------------------
    elif scenario == "2. Device Dominance and User Engagement Analysis (3D)":
        q = st.selectbox("Choose a Question", [
            "I. Underutilized Devices (3D)",
            "II. Device Dominance (3D)",
            "III. Region-Wise Engagement (3D)",
        ])

        if q == "I. Underutilized Devices (3D)":
            st.subheader("📌 Underutilized Devices by State (3D)")
            sql = """
            SELECT 
                brand, 
                states, 
                SUM(registered_users) AS total_users, 
                SUM(app_opens) AS total_opens,
                ROUND(SUM(app_opens) * 1.0 / NULLIF(SUM(registered_users), 0), 2) AS engagement_rate 
            FROM agg_user 
            GROUP BY brand, states 
            HAVING 
                (SUM(app_opens) * 1.0 / NULLIF(SUM(registered_users), 0)) < 0.3
                AND SUM(registered_users) > 500000 
            ORDER BY engagement_rate ASC;
            """
            df = pd.read_sql_query(sql, engine)
            df = add_cat_index(add_cat_index(df, "brand", name="brand_idx"), "states", name="state_idx")

            fig = scatter3d(
                df,
                x="brand_idx",
                y="state_idx",
                z="engagement_rate",
                color="engagement_rate",
                size="total_users",
                title="3D: Underutilized Devices by State (Engagement Rate < 30%)",
                x_title="Brand (index)",
                y_title="State (index)",
                z_title="Engagement Rate",
                text=["brand_label", "states_label"]
            )
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df)

        elif q == "II. Device Dominance (3D)":
            st.subheader("📌 Top Device Brands by Registered Users (3D)")
            sql = """
            SELECT 
                brand, 
                SUM(registered_users) AS total_users 
            FROM agg_user 
            GROUP BY brand 
            ORDER BY total_users DESC;
            """
            df = pd.read_sql_query(sql, engine)
            df = add_cat_index(df, "brand", name="brand_idx")

            fig = scatter3d(
                df,
                x="brand_idx",
                y="total_users",
                z="total_users",
                color="total_users",
                size="total_users",
                title="3D: Top Device Brands by Registered Users",
                x_title="Brand (index)",
                y_title="Registered Users",
                z_title="Registered Users (as height)",
                text="brand_label"
            )
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df)

        elif q == "III. Region-Wise Engagement (3D)":
            st.subheader("📌 Region-Wise Engagement Rate by Device Brand (3D)")
            sql = """
            SELECT 
                states, 
                brand, 
                SUM(registered_users) AS total_users, 
                SUM(app_opens) AS total_opens, 
                ROUND(SUM(app_opens) * 1.0 / NULLIF(SUM(registered_users), 0), 2) AS engagement_rate 
            FROM agg_user 
            GROUP BY states, brand 
            ORDER BY states, engagement_rate DESC;
            """
            df = pd.read_sql_query(sql, engine)
            df = add_cat_index(add_cat_index(df, "states", name="state_idx"), "brand", name="brand_idx")

            fig = scatter3d(
                df,
                x="state_idx",
                y="brand_idx",
                z="engagement_rate",
                color="engagement_rate",
                size="total_users",
                title="3D: Region-Wise Engagement Rate by Brand",
                x_title="State (index)",
                y_title="Brand (index)",
                z_title="Engagement Rate",
                text=["states_label", "brand_label"]
            )
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df)

    # -------------------------
    # 3. Transaction Analysis (States / Districts / Pincodes)
    # -------------------------
    elif scenario == "3. Transaction Analysis (3D)":
        q = st.selectbox(
            "Choose a Question",
            ["I. Transaction Analysis by Top-Performing States (3D)",
             "II. Transaction Analysis by Top-Performing Districts (3D)",
             "III. Transaction Analysis by Top-Performing Pincodes (3D)"]
        )

        # Common state name map (same as original)
        state_name_map = {
            'Andaman & Nicobar': 'Andaman & Nicobar Islands',
            'Andhra Pradesh': 'Andhra Pradesh',
            'Arunachal Pradesh': 'Arunachal Pradesh',
            'Assam': 'Assam',
            'Bihar': 'Bihar',
            'Chandigarh': 'Chandigarh',
            'Chhattisgarh': 'Chhattisgarh',
            'Dadra and Nagar Haveli and Daman and Diu': 'Dadra and Nagar Haveli and Daman and Diu',
            'Delhi': 'Delhi',
            'Goa': 'Goa',
            'Gujarat': 'Gujarat',
            'Haryana': 'Haryana',
            'Himachal Pradesh': 'Himachal Pradesh',
            'Jammu & Kashmir': 'Jammu and Kashmir',
            'Jharkhand': 'Jharkhand',
            'Karnataka': 'Karnataka',
            'Kerala': 'Kerala',
            'Ladakh': 'Ladakh',
            'Lakshadweep': 'Lakshadweep',
            'Madhya Pradesh': 'Madhya Pradesh',
            'Maharashtra': 'Maharashtra',
            'Manipur': 'Manipur',
            'Meghalaya': 'Meghalaya',
            'Mizoram': 'Mizoram',
            'Nagaland': 'Nagaland',
            'Odisha': 'Odisha',
            'Puducherry': 'Puducherry',
            'Punjab': 'Punjab',
            'Rajasthan': 'Rajasthan',
            'Sikkim': 'Sikkim',
            'Tamil Nadu': 'Tamil Nadu',
            'Telangana': 'Telangana',
            'Tripura': 'Tripura',
            'Uttar Pradesh': 'Uttar Pradesh',
            'Uttarakhand': 'Uttarakhand',
            'West Bengal': 'West Bengal'
        }

        # Load India GeoJSON and compute state centroids once
        geojson_url = (
            "https://gist.githubusercontent.com/jbrobst/"
            "56c13bbbf9d97d187fea01ca62ea5112/raw/"
            "e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
        )
        india_geojson = None
        state_centroids = {}
        try:
            resp = requests.get(geojson_url, timeout=20)
            resp.raise_for_status()
            india_geojson = resp.json()
            state_centroids = geojson_state_centroids(india_geojson, state_key="ST_NM")
        except Exception as e:
            st.warning(f"Could not load GeoJSON for centroids. Map-style 3D plots will be disabled.\nError: {e}")

        # I. States
        if q == "I. Transaction Analysis by Top-Performing States (3D)":
            st.subheader("📊 Transaction Analysis by Top-Performing States (3D)")
            sql = """
            SELECT
                states,
                SUM(transaction_count)  AS total_txn,
                SUM(transaction_amount) AS total_value
            FROM agg_trans
            GROUP BY states
            ORDER BY total_value DESC, total_txn DESC
            """
            df = pd.read_sql_query(sql, engine)
            df['state_clean'] = df['states'].map(state_name_map)

            if state_centroids and not df['state_clean'].isna().all():
                # map to centroids
                df_map = df.dropna(subset=['state_clean']).copy()
                df_map['lon'] = df_map['state_clean'].map(lambda s: state_centroids.get(s, (None, None))[0])
                df_map['lat'] = df_map['state_clean'].map(lambda s: state_centroids.get(s, (None, None))[1])
                df_map = df_map.dropna(subset=['lon', 'lat'])

                fig = scatter3d(
                    df_map,
                    x="lon", y="lat", z="total_value",
                    color="total_value",
                    size="total_txn",
                    title="3D Column Map: States by Transaction Value",
                    x_title="Longitude",
                    y_title="Latitude",
                    z_title="Transaction Value (₹)",
                    text=["states", "state_clean"]
                )
                st.plotly_chart(fig, use_container_width=True)
                st.caption("Each point sits at an approximate state centroid; height encodes total value, marker size encodes total transactions.")
            else:
                # fallback to categorical 3D if centroids not available
                df = add_cat_index(df, "states", name="state_idx")
                fig = scatter3d(
                    df,
                    x="state_idx", y="total_txn", z="total_value",
                    color="total_value",
                    size="total_txn",
                    title="3D: Top Performing States by Transaction Value (Fallback)",
                    x_title="State (index)",
                    y_title="Total Transactions",
                    z_title="Total Value (₹)",
                    text="states_label"
                )
                st.plotly_chart(fig, use_container_width=True)

            st.dataframe(df.sort_values("total_value", ascending=False).head(10))

        # II. Districts
        elif q == "II. Transaction Analysis by Top-Performing Districts (3D)":
            st.subheader("🏙️ Transaction Analysis by Top-Performing Districts (3D)")
            sql = """
            SELECT 
                districts, 
                SUM(transaction_count) AS total_txn, 
                SUM(transaction_amount) AS total_value 
            FROM map_trans 
            GROUP BY districts 
            ORDER BY total_value DESC, total_txn DESC
            LIMIT 10
            """
            df = pd.read_sql_query(sql, engine)
            df = add_cat_index(df, "districts", name="district_idx")

            fig = scatter3d(
                df,
                x="district_idx", y="total_txn", z="total_value",
                color="total_value",
                size="total_txn",
                title="3D: Top 10 Districts by Total Transaction Value",
                x_title="District (index)",
                y_title="Total Transactions",
                z_title="Total Value (₹)",
                text="districts_label"
            )
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df)

        # III. Pincodes
        elif q == "III. Transaction Analysis by Top-Performing Pincodes (3D)":
            st.subheader("📮 Transaction Analysis by Top-Performing Pincodes (3D)")
            sql = """
            SELECT 
                pincodes, 
                SUM(transaction_count) AS total_txn, 
                SUM(transaction_amount) AS total_value 
            FROM top_trans 
            GROUP BY pincodes 
            ORDER BY total_value DESC, total_txn DESC 
            LIMIT 10
            """
            df = pd.read_sql_query(sql, engine)
            df = add_cat_index(df, "pincodes", name="pincode_idx")

            fig = scatter3d(
                df,
                x="pincode_idx", y="total_txn", z="total_value",
                color="total_value",
                size="total_txn",
                title="3D: Top 10 Pincodes by Transaction Value",
                x_title="Pincode (index)",
                y_title="Total Transactions",
                z_title="Total Value (₹)",
                text="pincodes_label"
            )
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df)

    # -------------------------
    # 4. User Registration Analysis (States/Districts/Pincodes)
    # -------------------------
    elif scenario == "4. User Registration Analysis (3D)":
        q = st.selectbox("Choose a Question", [
            "I. User Registration Analysis by Top States (3D)",
            "II. User Registration Analysis by Top Districts (3D)",
            "III. User Registration Analysis by Top Pincodes (3D)"
        ])

        # Common state name map
        state_name_map = {
            'Andaman & Nicobar': 'Andaman & Nicobar Islands',
            'Andhra Pradesh': 'Andhra Pradesh',
            'Arunachal Pradesh': 'Arunachal Pradesh',
            'Assam': 'Assam',
            'Bihar': 'Bihar',
            'Chandigarh': 'Chandigarh',
            'Chhattisgarh': 'Chhattisgarh',
            'Dadra and Nagar Haveli and Daman and Diu': 'Dadra and Nagar Haveli and Daman and Diu',
            'Delhi': 'Delhi',
            'Goa': 'Goa',
            'Gujarat': 'Gujarat',
            'Haryana': 'Haryana',
            'Himachal Pradesh': 'Himachal Pradesh',
            'Jammu & Kashmir': 'Jammu and Kashmir',
            'Jharkhand': 'Jharkhand',
            'Karnataka': 'Karnataka',
            'Kerala': 'Kerala',
            'Ladakh': 'Ladakh',
            'Lakshadweep': 'Lakshadweep',
            'Madhya Pradesh': 'Madhya Pradesh',
            'Maharashtra': 'Maharashtra',
            'Manipur': 'Manipur',
            'Meghalaya': 'Meghalaya',
            'Mizoram': 'Mizoram',
            'Nagaland': 'Nagaland',
            'Odisha': 'Odisha',
            'Puducherry': 'Puducherry',
            'Punjab': 'Punjab',
            'Rajasthan': 'Rajasthan',
            'Sikkim': 'Sikkim',
            'Tamil Nadu': 'Tamil Nadu',
            'Telangana': 'Telangana',
            'Tripura': 'Tripura',
            'Uttar Pradesh': 'Uttar Pradesh',
            'Uttarakhand': 'Uttarakhand',
            'West Bengal': 'West Bengal'
        }

        if q == "I. User Registration Analysis by Top States (3D)":
            st.subheader("📈 User Registration Analysis by Top States (3D)")
            selected_year = st.selectbox("Select Year", [2018, 2019, 2020, 2021, 2022, 2023, 2024])
            selected_quarter = st.selectbox("Select Quarter", [1, 2, 3, 4])

            sql = f"""
            SELECT
                states,
                SUM(registered_users) AS total_users
            FROM agg_user
            WHERE years = '{selected_year}' AND quarter = '{selected_quarter}'
            GROUP BY states
            ORDER BY total_users DESC;
            """
            df = pd.read_sql_query(sql, engine)
            df['state_clean'] = df['states'].map(state_name_map)

            # Try 3D column map using centroids
            geojson_url = (
                "https://gist.githubusercontent.com/jbrobst/"
                "56c13bbbf9d97d187fea01ca62ea5112/raw/"
                "e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
            )
            try:
                resp = requests.get(geojson_url, timeout=20)
                resp.raise_for_status()
                india_geojson = resp.json()
                centroids = geojson_state_centroids(india_geojson, state_key="ST_NM")

                df_map = df.dropna(subset=['state_clean']).copy()
                df_map['lon'] = df_map['state_clean'].map(lambda s: centroids.get(s, (None, None))[0])
                df_map['lat'] = df_map['state_clean'].map(lambda s: centroids.get(s, (None, None))[1])
                df_map = df_map.dropna(subset=['lon', 'lat'])

                if not df_map.empty:
                    fig = scatter3d(
                        df_map,
                        x="lon", y="lat", z="total_users",
                        color="total_users",
                        size="total_users",
                        title=f"3D Column Map: Top States by User Registrations (Year {selected_year}, Q{selected_quarter})",
                        x_title="Longitude",
                        y_title="Latitude",
                        z_title="Registered Users",
                        text=["states", "state_clean"]
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    st.dataframe(df.head(10))
                else:
                    raise ValueError("Missing centroids after mapping")
            except Exception as e:
                st.warning(f"Centroid-based 3D map unavailable. Falling back to 3D categorical view. ({e})")
                df = add_cat_index(df, "states", name="state_idx")
                fig = scatter3d(
                    df,
                    x="state_idx", y="total_users", z="total_users",
                    color="total_users",
                    size="total_users",
                    title=f"3D: Top States by User Registrations (Year {selected_year}, Q{selected_quarter})",
                    x_title="State (index)",
                    y_title="Registered Users",
                    z_title="Registered Users (height)",
                    text="states_label"
                )
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(df.head(10))

        elif q == "II. User Registration Analysis by Top Districts (3D)":
            st.subheader("🏙️ User Registration Analysis by Top Districts (3D)")
            year = st.selectbox("Select Year", [2021, 2022, 2023, 2024])
            quarter = st.selectbox("Select Quarter", [1, 2, 3, 4])

            sql = f"""
            SELECT 
                districts, 
                SUM(registered_users) AS total_users 
            FROM map_user 
            WHERE years ='{year}' AND quarter = '{quarter}'
            GROUP BY districts 
            ORDER BY total_users DESC ;
            """
            df = pd.read_sql_query(sql, engine)
            df = add_cat_index(df, "districts", name="district_idx")

            fig = scatter3d(
                df,
                x="district_idx", y="total_users", z="total_users",
                color="total_users",
                size="total_users",
                title=f"3D: Top Districts by Registered Users ({year} Q{quarter})",
                x_title="District (index)",
                y_title="Registered Users",
                z_title="Registered Users (height)",
                text="districts_label"
            )
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df.head(10))

        elif q == "III. User Registration Analysis by Top Pincodes (3D)":
            st.subheader("📍 User Registration Analysis by Top Pincodes (3D)")
            year = st.selectbox("Select Year", [2021, 2022, 2023, 2024])
            quarter = st.selectbox("Select Quarter", [1, 2, 3, 4])

            sql = f"""
            SELECT 
                pincodes, 
                SUM(registered_users) AS total_users 
            FROM top_user 
            WHERE years = '{year}' AND quarter = '{quarter}'
            GROUP BY pincodes 
            ORDER BY total_users DESC ;
            """
            df = pd.read_sql_query(sql, engine)
            df = add_cat_index(df, "pincodes", name="pincode_idx")

            fig = scatter3d(
                df,
                x="pincode_idx", y="total_users", z="total_users",
                color="total_users",
                size="total_users",
                title=f"3D: Top Pincodes by Registered Users ({year} Q{quarter})",
                x_title="Pincode (index)",
                y_title="Registered Users",
                z_title="Registered Users (height)",
                text="pincodes_label"
            )
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df.head(10))

    # -------------------------
    # 5. Insurance Transactions Analysis (States/Districts/Pincodes)
    # -------------------------
    elif scenario == "5. Insurance Transactions Analysis (3D)":
        q = st.selectbox("Choose a Question", [
            "I. Insurance Transactions Analysis Top States (3D)",
            "II. Insurance Transactions Analysis by Top Districts (3D)",
            "III. Insurance Transactions Analysis by Top Pincodes (3D)"
        ])

        # Common state name map
        state_name_map = {
            'Andaman & Nicobar': 'Andaman & Nicobar Islands',
            'Andhra Pradesh': 'Andhra Pradesh',
            'Arunachal Pradesh': 'Arunachal Pradesh',
            'Assam': 'Assam',
            'Bihar': 'Bihar',
            'Chandigarh': 'Chandigarh',
            'Chhattisgarh': 'Chhattisgarh',
            'Dadra and Nagar Haveli and Daman and Diu': 'Dadra and Nagar Haveli and Daman and Diu',
            'Delhi': 'Delhi',
            'Goa': 'Goa',
            'Gujarat': 'Gujarat',
            'Haryana': 'Haryana',
            'Himachal Pradesh': 'Himachal Pradesh',
            'Jammu & Kashmir': 'Jammu and Kashmir',
            'Jharkhand': 'Jharkhand',
            'Karnataka': 'Karnataka',
            'Kerala': 'Kerala',
            'Ladakh': 'Ladakh',
            'Lakshadweep': 'Lakshadweep',
            'Madhya Pradesh': 'Madhya Pradesh',
            'Maharashtra': 'Maharashtra',
            'Manipur': 'Manipur',
            'Meghalaya': 'Meghalaya',
            'Mizoram': 'Mizoram',
            'Nagaland': 'Nagaland',
            'Odisha': 'Odisha',
            'Puducherry': 'Puducherry',
            'Punjab': 'Punjab',
            'Rajasthan': 'Rajasthan',
            'Sikkim': 'Sikkim',
            'Tamil Nadu': 'Tamil Nadu',
            'Telangana': 'Telangana',
            'Tripura': 'Tripura',
            'Uttar Pradesh': 'Uttar Pradesh',
            'Uttarakhand': 'Uttarakhand',
            'West Bengal': 'West Bengal'
        }

        if q == "I. Insurance Transactions Analysis Top States (3D)":
            st.subheader("🏥 Insurance Transactions Analysis by Top States (3D)")
            selected_year = st.selectbox("Select Year", [2020, 2021, 2022, 2023, 2024])
            selected_quarter = st.selectbox("Select Quarter", [1, 2, 3, 4])

            sql = f"""
            SELECT
                states,
                SUM(transaction_count) AS total_txn,
                SUM(transaction_amount) AS total_value
            FROM agg_ins
            WHERE years = '{selected_year}' AND quarter = '{selected_quarter}'
            GROUP BY states
            ORDER BY total_value DESC, total_txn DESC;
            """
            df = pd.read_sql_query(sql, engine)
            df['state_clean'] = df['states'].map(state_name_map)

            # 3D column map via centroids
            geojson_url = (
                "https://gist.githubusercontent.com/jbrobst/"
                "56c13bbbf9d97d187fea01ca62ea5112/raw/"
                "e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
            )
            try:
                resp = requests.get(geojson_url, timeout=20)
                resp.raise_for_status()
                india_geojson = resp.json()
                centroids = geojson_state_centroids(india_geojson, state_key="ST_NM")

                df_map = df.dropna(subset=['state_clean']).copy()
                df_map['lon'] = df_map['state_clean'].map(lambda s: centroids.get(s, (None, None))[0])
                df_map['lat'] = df_map['state_clean'].map(lambda s: centroids.get(s, (None, None))[1])
                df_map = df_map.dropna(subset=['lon', 'lat'])

                if not df_map.empty:
                    fig = scatter3d(
                        df_map,
                        x="lon", y="lat", z="total_value",
                        color="total_value",
                        size="total_txn",
                        title=f"3D Column Map: Top States by Insurance Transaction Value ({selected_year}, Q{selected_quarter})",
                        x_title="Longitude",
                        y_title="Latitude",
                        z_title="Total Value (₹)",
                        text=["states", "state_clean"]
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    st.dataframe(df.head(10))
                else:
                    raise ValueError("Missing centroids after mapping")
            except Exception as e:
                st.warning(f"Centroid-based 3D map unavailable. Falling back to 3D categorical view. ({e})")
                df = add_cat_index(df, "states", name="state_idx")
                fig = scatter3d(
                    df,
                    x="state_idx", y="total_txn", z="total_value",
                    color="total_value",
                    size="total_txn",
                    title=f"3D: Top States by Insurance Transaction Value ({selected_year}, Q{selected_quarter})",
                    x_title="State (index)",
                    y_title="Total Transactions",
                    z_title="Total Value (₹)",
                    text="states_label"
                )
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(df.head(10))

        elif q == "II. Insurance Transactions Analysis by Top Districts (3D)":
            st.subheader("🏥 Insurance Transactions Analysis by Top Districts (3D)")
            year = st.selectbox("Select Year", [2020, 2021, 2022, 2023, 2024])
            quarter = st.selectbox("Select Quarter", [1, 2, 3, 4])

            sql = f"""
            SELECT 
                districts, 
                SUM(transaction_count) AS total_txn, 
                SUM(transaction_amount) AS total_value 
            FROM map_ins 
            WHERE years = '{year}' AND quarter = '{quarter}'
            GROUP BY districts 
            ORDER BY total_value DESC, total_txn DESC ;
            """
            df = pd.read_sql_query(sql, engine)
            df = add_cat_index(df, "districts", name="district_idx")

            fig = scatter3d(
                df,
                x="district_idx", y="total_txn", z="total_value",
                color="total_value",
                size="total_txn",
                title=f"3D: Top Districts by Insurance Transaction Value ({year} Q{quarter})",
                x_title="District (index)",
                y_title="Total Transactions",
                z_title="Total Value (₹)",
                text="districts_label"
            )
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df.head(10))

        elif q == "III. Insurance Transactions Analysis by Top Pincodes (3D)":
            st.subheader("🏥 Insurance Transactions Analysis by Top Pincodes (3D)")
            year = st.selectbox("Select Year", [2018, 2019, 2020, 2021, 2022, 2023, 2024])
            quarter = st.selectbox("Select Quarter", [1, 2, 3, 4])

            sql = f"""
            SELECT 
                pincodes, 
                SUM(transaction_count) AS total_txn, 
                SUM(transaction_amount) AS total_value 
            FROM top_ins 
            WHERE years = '{year}' AND quarter = '{quarter}'
            GROUP BY pincodes 
            ORDER BY total_value DESC, total_txn DESC;
            """
            df = pd.read_sql_query(sql, engine)
            df = add_cat_index(df, "pincodes", name="pincode_idx")

            fig = scatter3d(
                df,
                x="pincode_idx", y="total_txn", z="total_value",
                color="total_value",
                size="total_txn",
                title=f"3D: Top Pincodes by Insurance Transaction Value ({year} Q{quarter})",
                x_title="Pincode (index)",
                y_title="Total Transactions",
                z_title="Total Value (₹)",
                text="pincodes_label"
            )
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df.head(10))

# -----------------------------
# Docs
# -----------------------------
elif selected == "📄 Docs":
    st.title("📄 Project Documentation (3D Edition)")
    st.markdown("""
    ### 📦 Dataset Info
    - **Source:** PhonePe Pulse GitHub (https://github.com/PhonePe/pulse)
    - **Data Format:** JSON
    - **Tools Used for ETL:** Python, Pandas
    - **Database:** PostgreSQL (via Neon Cloud)
    - **Visualization:** Plotly 3D, Streamlit
    
    ### 🧩 Tables Used
    - `agg_trans` – Aggregated Transactions
    - `agg_user` – Aggregated User Metrics
    - `map_ins` – Insurance Metrics (District)
    - `top_user` – User by Top Pincodes
    - `top_ins` – Insurance by Top Pincodes

    ### 🧠 What Changed (2D ➜ 3D)
    - Replaced bar/line/choropleth with **3D scatter-based** visuals.
    - Introduced **categorical indices** for axes that require numbers.
    - For maps, computed **approximate state centroids** from GeoJSON to create **3D column maps**.

    ### ⚙️ Notes
    - Plotly has no native 3D bar; we emulate with scatter_3d where **marker size** and **Z height** carry the values.
    - Categorical names appear as **hover labels**; X/Y axes show indices to keep 3D stable and fast.
    - If GeoJSON fails to load, code falls back to **categorical 3D** automatically.

    ---

    **📌 Developed by:** Bilk Edison Xavier
    **📧 Email:** edisonxavier44@gmail.com  
    **LinkedIn:** [linkedin.com/in/bilk-edison-xavier](https://www.linkedin.com/in/bilk-edison-xavier)
    **GitHub:** [github.com/bilk-edison-xavier](

    Built with ❤️ using **Python, Pandas, Plotly 3D, Streamlit, PostgreSQL**.
    """)

