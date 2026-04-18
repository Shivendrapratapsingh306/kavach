import streamlit as st
import pandas as pd
import pydeck as pdk
import json

# ----------------------------
# Load Data
# ----------------------------
df = pd.read_csv("ghaziabad_20_regions.csv", low_memory=False)

df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
df['lng'] = pd.to_numeric(df['lng'], errors='coerce')

# ----------------------------
# Title
# ----------------------------
st.title("🔥 Ghaziabad Crime Intelligence Map")

# ----------------------------
# Sidebar (Google-like Search)
# ----------------------------
st.sidebar.header("Search & Filters")

areas = sorted(df['area'].dropna().unique())

search_area = st.sidebar.text_input("🔍 Search Area")

selected_area = st.sidebar.selectbox(
    "Or Select Area",
    ["All"] + areas
)

zoom = st.sidebar.slider("Zoom", 5, 15, 10)

# ----------------------------
# Apply Filters
# ----------------------------
if search_area:
    df = df[df['area'].str.contains(search_area, case=False, na=False)]

elif selected_area != "All":
    df = df[df['area'] == selected_area]

# ----------------------------
# Dynamic Centering
# ----------------------------
if len(df) > 0:
    lat_center = df['lat'].mean()
    lng_center = df['lng'].mean()
else:
    lat_center = 28.67
    lng_center = 77.42

view_state = pdk.ViewState(
    latitude=lat_center,
    longitude=lng_center,
    zoom=13 if (search_area or selected_area != "All") else zoom,
)

# ----------------------------
# Heatmap Layer
# ----------------------------
df['weight'] = df['crime_count']

heatmap = pdk.Layer(
    "HeatmapLayer",
    data=df,
    get_position='[lng, lat]',
    get_weight="weight",
    radiusPixels=60,
)

# ----------------------------
# Scatter Points (small + clean)
# ----------------------------
def get_color(risk):
    return [255, 0, 0] if risk == 1 else [0, 255, 0]

df['color'] = df['risk_label'].apply(get_color)

scatter = pdk.Layer(
    "ScatterplotLayer",
    data=df,
    get_position='[lng, lat]',
    get_color='color',
    get_radius=50,
    radius_min_pixels=2,
    radius_max_pixels=8,
    pickable=True,
)

# ----------------------------
# Area Labels (Text Layer)
# ----------------------------
area_centers = df.groupby("area")[["lat", "lng"]].mean().reset_index()

text_layer = pdk.Layer(
    "TextLayer",
    data=area_centers,
    get_position='[lng, lat]',
    get_text='area',
    get_size=14,
    get_color=[255, 255, 255],
    text_anchor="middle",
    alignment_baseline="center",
)

# ----------------------------
# Polygon Boundaries (Auto Grid-based)
# ----------------------------
# We generate approximate polygons per area

polygons = []

for area in df['area'].unique():
    sub = df[df['area'] == area]
    if len(sub) > 3:
        coords = list(zip(sub['lng'], sub['lat']))
        polygons.append({
            "area": area,
            "polygon": coords
        })

polygon_layer = pdk.Layer(
    "PolygonLayer",
    data=polygons,
    get_polygon="polygon",
    get_fill_color=[0, 0, 255, 30],
    get_line_color=[255, 255, 255],
    line_width_min_pixels=1,
    pickable=True,
)

# ----------------------------
# Render Map
# ----------------------------
st.pydeck_chart(pdk.Deck(
    map_style='mapbox://styles/mapbox/dark-v10',
    layers=[polygon_layer, heatmap, scatter, text_layer],
    initial_view_state=view_state,
    tooltip={
        "html": """
        <b>Area:</b> {area} <br/>
        <b>Crime:</b> {crime_count}
        """,
        "style": {"color": "white"},
    },
))

# ----------------------------
# Data Table
# ----------------------------
st.subheader("📊 Data Preview")
st.dataframe(df.head(50))