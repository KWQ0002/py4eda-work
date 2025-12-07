import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from loader import load_data


#page config
st.title("Sales Dashboard")

# load data
df = load_data()




st.sidebar.title("Filters")

# Example filters (adapt to your columns)
segments = st.sidebar.multiselect(
    "Segment",
    options=sorted(df["Segment"].dropna().unique()),
    default=sorted(df["Segment"].dropna().unique())
)

regions = st.sidebar.multiselect(
    "Region",
    options=sorted(df["Region"].dropna().unique()),
    default=sorted(df["Region"].dropna().unique())
)

date_range = st.sidebar.date_input(
    "Order Date range",
    value=(df["Order Date"].min(), df["Order Date"].max())
)

# Apply filters
filtered = df[
    df["Segment"].isin(segments)
    & df["Region"].isin(regions)
    & (df["Order Date"].between(pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])))
]

# ---------- Top section: KPIs ----------
st.title("Sales EDA Dashboard")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Total Sales",
        f"${filtered['Sales'].sum():,.2f}"
    )

with col2:
    st.metric(
        "Total Orders",
        f"{filtered['Order ID'].nunique():,}"
    )

with col3:
    st.metric(
        "Average Order Value",
        f"${(filtered['Sales'].sum() / max(filtered['Order ID'].nunique(),1)):,.2f}"
    )

st.markdown("---")

# ---------- Middle section: charts ----------
left_col, right_col = st.columns(2)

# Sales by Category
with left_col:
    st.subheader("Sales by Category")
    sales_by_cat = (
        filtered.groupby("Category", observed=True)["Sales"]
        .sum()
        .sort_values(ascending=False)
    )

    fig1, ax1 = plt.subplots()
    sales_by_cat.plot(kind="bar", ax=ax1)
    ax1.set_xlabel("Category")
    ax1.set_ylabel("Sales ($)")
    ax1.ticklabel_format(style="plain", axis="y")
    st.pyplot(fig1)

# Sales by Region
with right_col:
    st.subheader("Sales by Region")
    sales_by_region = (
        filtered.groupby("Region", observed=True)["Sales"]
        .sum()
        .sort_values(ascending=False)
    )

    fig2, ax2 = plt.subplots()
    sales_by_region.plot(kind="bar", ax=ax2)
    ax2.set_xlabel("Region")
    ax2.set_ylabel("Sales ($)")
    ax2.ticklabel_format(style="plain", axis="y")
    st.pyplot(fig2)

# ---------- Bottom: raw data preview ----------
st.markdown("---")
st.subheader("Filtered Data Preview")
st.dataframe(filtered.head(100))