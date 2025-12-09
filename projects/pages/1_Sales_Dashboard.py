import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from loader import load_data


#setup the page
st.set_page_config(
    page_title="Sales",
    layout="wide"
)

#Page title
st.title("Sales")

#Load data
df = load_data()

#Filters
st.sidebar.title("Filters")

#segments
segments = st.sidebar.multiselect(
    "Segment", #title it
    options=sorted(df["Segment"].dropna().unique()), #drop the non unique values
    default=sorted(df["Segment"].dropna().unique()) #default all selected
)
#regions
regions = st.sidebar.multiselect(
    "Region", #title it
    options=sorted(df["Region"].dropna().unique()), #drop the non unique values
    default=sorted(df["Region"].dropna().unique()) #default all selected
)
#date range
date_range = st.sidebar.date_input( #add a dateinput that selects date range
    "Order Date range", #title it
    value=(df["Order Date"].min(), df["Order Date"].max()) #default it to the min and max of the date range
)

#apply filters
filtered = df[ #us isin and and between combined with & to stack the variety of filters.
    df["Segment"].isin(segments) 
    & df["Region"].isin(regions)
    & (df["Order Date"].between(pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])))
]

#KPIs
st.title("Sales") 

col1, col2, col3 = st.columns(3) #set it up with columns

with col1: #target column 1
    st.metric(
        "Total Sales",
        f"${filtered['Sales'].sum():,.2f}" #use the filtered data frame to make sure it is the right subset.
    )

with col2: #target column 2
    st.metric(
        "Total Orders",
        f"{filtered['Order ID'].nunique():,}" #use the filtered data frame to make sure it is the right subset.
    )

with col3: #target column 3
    st.metric(
        "Average Order Value",
        f"${(filtered['Sales'].sum() / max(filtered['Order ID'].nunique(), 1)):,.2f}" #use the filtered data frame to make sure it is the right subset.
    )

st.markdown("---")

#charts
left_col, right_col = st.columns(2) #create two columns for 2 charts side by side

#sales by category
with left_col: #target left colum 
    st.subheader("Sales by Category")
    sales_by_cat = (
        filtered.groupby("Category", observed=True)["Sales"]
        .sum()
        .sort_values(ascending=False)
    )

    fig1, ax1 = plt.subplots() #need to use subplot to return the figure and axes
    sales_by_cat.plot(kind="bar", ax=ax1)

    ax1.set_xlabel("Category")
    ax1.set_ylabel("Sales ($)")
    ax1.ticklabel_format(style="plain", axis="y")
    ax1.tick_params(axis="x", rotation=0) # Rotate x-tick labels to horizontal

    st.pyplot(fig1)

#sales by region
with right_col: #target right column
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
    ax2.tick_params(axis="x", rotation=0) # Rotate x-tick labels to horizontal

    st.pyplot(fig2)

