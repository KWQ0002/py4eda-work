import streamlit as st
import pandas as pd
import plotly.express as px

from loader import load_data  # shared train.csv loader


# ---------- Page config ----------
st.set_page_config(
    page_title="US Sales Heatmap – State",
    layout="wide"
)

# ---------- Load data ----------
df = load_data()

st.title("US Sales Heatmap – State")

# ---------- Sidebar filters ----------
st.sidebar.header("Filters")

# Segment filter
all_segments = sorted(df["Segment"].dropna().unique())
default_segments = [s for s in all_segments if s in ["Corporate", "Home Office"]]

selected_segments = st.sidebar.multiselect(
    "Segments",
    options=all_segments,
    default=default_segments or all_segments,
)

# Date range filter
date_range = st.sidebar.date_input(
    "Order Date Range",
    value=(df["Order Date"].min(), df["Order Date"].max())
)

df["Order Date"] = pd.to_datetime(df["Order Date"])

mask = df["Order Date"].between(
    pd.to_datetime(date_range[0]),
    pd.to_datetime(date_range[1])
)

if selected_segments:
    mask &= df["Segment"].isin(selected_segments)

df_filtered = df[mask].copy()

if df_filtered.empty:
    st.info("No data for the current filters.")
    st.stop()

# ---------- Manual state mapping (full name -> abbreviation) ----------
state_to_abbrev = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
    "California": "CA", "Colorado": "CO", "Connecticut": "CT",
    "Delaware": "DE", "District of Columbia": "DC", "Florida": "FL",
    "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL",
    "Indiana": "IN", "Iowa": "IA", "Kansas": "KS", "Kentucky": "KY",
    "Louisiana": "LA", "Maine": "ME", "Maryland": "MD", "Massachusetts": "MA",
    "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO",
    "Montana": "MT", "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH",
    "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY",
    "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH",
    "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA",
    "Rhode Island": "RI", "South Carolina": "SC", "South Dakota": "SD",
    "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT",
    "Virginia": "VA", "Washington": "WA", "West Virginia": "WV",
    "Wisconsin": "WI", "Wyoming": "WY"
}

# ---------- State-level aggregation ----------
state_sales = (
    df_filtered
        .dropna(subset=["State"])
        .groupby("State", observed=True)["Sales"]
        .sum()
        .reset_index()
)

# Map to 2-letter abbreviations
state_sales["state_abbrev"] = state_sales["State"].map(state_to_abbrev)

# Keep ONLY contiguous 48 + DC in the visualization
contiguous_states = [
    "AL","AZ","AR","CA","CO","CT","DE","DC","FL","GA","ID","IL","IN","IA","KS","KY",
    "LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ","NM","NY","NC",
    "ND","OH","OK","OR","PA","RI","SC","SD","TN","TX","UT","VT","VA","WA","WV","WI","WY"
]

state_sales = state_sales[state_sales["state_abbrev"].isin(contiguous_states)].copy()
state_sales["Sales"] = state_sales["Sales"].astype(float)

if state_sales.empty:
    st.info("No mappable state-level data for current filters.")
    st.stop()

# ---------- Choropleth map ----------
st.subheader("US State Heatmap (Total Sales) – Contiguous 48 Only")

fig_states = px.choropleth(
    state_sales,
    locations="state_abbrev",
    locationmode="USA-states",
    color="Sales",
    hover_name="State",
    color_continuous_scale="Reds",
    labels={"Sales": "Total Sales ($)"},
    range_color=(state_sales["Sales"].min(), state_sales["Sales"].max())
)

# Show ONLY the lower 48 by restricting lat/lon
fig_states.update_geos(
    projection_type="mercator",
    scope="north america",
    lataxis_range=[24, 50],     # lat range for lower 48
    lonaxis_range=[-125, -66],  # lon range for lower 48
    showcountries=False,
    showsubunits=True
)

fig_states.update_layout(
    margin=dict(l=0, r=0, t=30, b=0),
    height=500,
    coloraxis_colorbar=dict(title="Sales ($)")
)

st.plotly_chart(fig_states, use_container_width=True)
