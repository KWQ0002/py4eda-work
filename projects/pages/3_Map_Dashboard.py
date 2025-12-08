import streamlit as st
import pandas as pd
import plotly.express as px

from loader import load_data  # shared train.csv loader


#setup the page
st.set_page_config(
    page_title="State Breakdown",
    layout="wide"
)

#Load data
df = load_data()

st.title("State Breakdown")

#Filters
st.sidebar.header("Filters")

#segments
selected_segments = st.sidebar.multiselect(
    "Segment", #title it
    options=sorted(df["Segment"].dropna().unique()), #drop the non unique values
    default=sorted(df["Segment"].dropna().unique()) #default all selected
)

#date range
date_range = st.sidebar.date_input( #add a dateinput that selects date range
    "Order Date range", #title it
    value=(df["Order Date"].min(), df["Order Date"].max()) #default it to the min and max of the date range
)
df["Order Date"] = pd.to_datetime(df["Order Date"])

mask = df["Order Date"].between(
    pd.to_datetime(date_range[0]),
    pd.to_datetime(date_range[1])
)

if selected_segments:
    mask &= df["Segment"].isin(selected_segments)

df_filtered = df[mask].copy() #make sure it is it's own data frame and no objects inside it are editing objects in other places

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
state_agg = (
    df_filtered
        .dropna(subset=["State"])
        .groupby("State", observed=True)
        .agg(
            Total_Sales=("Sales", "sum"),
            Num_Sales=("Order ID", "nunique"),
            Num_Customers=("Customer ID", "nunique")
        )
        .reset_index()
)

state_agg["Avg_Sale"] = state_agg["Total_Sales"] / state_agg["Num_Sales"].replace(0, 1)
state_agg["state_abbrev"] = state_agg["State"].map(state_to_abbrev)

# Keep only contiguous 48 + DC
contiguous_states = [
    "AL","AZ","AR","CA","CO","CT","DE","DC","FL","GA","ID","IL","IN","IA","KS","KY",
    "LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ","NM","NY","NC",
    "ND","OH","OK","OR","PA","RI","SC","SD","TN","TX","UT","VT","VA","WA","WV","WI","WY"
]

state_agg = state_agg[state_agg["state_abbrev"].isin(contiguous_states)].copy()

# Format labels for tooltip
state_agg["Total_Sales_Label"] = state_agg["Total_Sales"].map(lambda x: f"${x:,.2f}")
state_agg["Avg_Sale_Label"] = state_agg["Avg_Sale"].map(lambda x: f"${x:,.2f}")


#heatmap total sales
st.subheader("US State Heatmap (Total Sales) – Contiguous 48 Only")

fig_sales = px.choropleth(
    state_agg,
    locations="state_abbrev",
    locationmode="USA-states",
    color="Total_Sales",
    color_continuous_scale="Reds",
    hover_name="State",
    labels={"Total_Sales_Label": "Total Sales ($)",
            "Num_Sales": "Number of Sales",
            "Avg_Sale_Label": "Average Sale",
            "Num_Customers": "Number of Customers",
            },
    hover_data={
        "Num_Sales": True,
        "Num_Customers": True,
        "Avg_Sale_Label": True,
        "Total_Sales_Label": True,
        "Total_Sales": False
    }
)

fig_sales.update_geos(
    projection_type="mercator",
    scope="north america",
    lataxis_range=[24, 50],
    lonaxis_range=[-125, -66],
    showcountries=False,
    showsubunits=True
)

fig_sales.update_layout(
    margin=dict(l=0, r=0, t=30, b=0),
    height=500
)

st.plotly_chart(fig_sales, use_container_width=True)


#heatmap number of sales
st.subheader("US State Heatmap (Number of Sales) – Contiguous 48 Only")

fig_orders = px.choropleth(
    state_agg,
    locations="state_abbrev",
    locationmode="USA-states",
    color="Num_Sales",
    color_continuous_scale="Blues",
    hover_name="State",
    labels={"Total_Sales_Label": "Total Sales ($)",
            "Num_Sales": "Number of Sales",
            "Avg_Sale_Label": "Average Sale",
            "Num_Customers": "Number of Customers",
            },
    hover_data={ #unify the hover data
        "Num_Sales": True,
        "Num_Customers": True,
        "Avg_Sale_Label": True,
        "Total_Sales_Label": True
    }
)

fig_orders.update_geos(
    projection_type="mercator",
    scope="north america",
    lataxis_range=[24, 50],
    lonaxis_range=[-125, -66],
    showcountries=False,
    showsubunits=True
)

fig_orders.update_layout(
    margin=dict(l=0, r=0, t=30, b=0),
    height=500
)

st.plotly_chart(fig_orders, use_container_width=True)


#state detail dropwdown
st.markdown("---")
st.subheader("State Detail – Sales & Ordering Habits")

available_states = state_agg["State"].sort_values().unique().tolist()

selected_state = st.selectbox(
    "Select a state for detailed statistics:",
    options=available_states
)

state_df = df_filtered[df_filtered["State"] == selected_state].copy()

if state_df.empty:
    st.info("No data for the selected state with the current filters.")
    st.stop()


#state KPI
total_sales = state_df["Sales"].sum()
num_sales = state_df["Order ID"].nunique()
num_customers = state_df["Customer ID"].nunique()
avg_sale = total_sales / max(num_sales, 1)
avg_orders_per_customer = num_sales / max(num_customers, 1)
avg_sales_per_customer = total_sales / max(num_customers, 1)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Sales", f"${total_sales:,.2f}")
with col2:
    st.metric("Number of Sales", f"{num_sales:,}")
with col3:
    st.metric("Unique Customers", f"{num_customers:,}")

col4, col5, col6 = st.columns(3)
with col4:
    st.metric("Avg Sale per Order", f"${avg_sale:,.2f}")
with col5:
    st.metric("Avg Orders per Customer", f"{avg_orders_per_customer:,.2f}")
with col6:
    st.metric("Avg Sales per Customer", f"${avg_sales_per_customer:,.2f}")


#segment breakdwon in state
st.markdown("#### Segment Breakdown for Selected State")

seg_stats = (
    state_df
    .groupby("Segment", observed=True)
    .agg(
        Total_Sales=("Sales", "sum"),
        Num_Sales=("Order ID", "nunique"),
        Num_Customers=("Customer ID", "nunique")
    )
    .reset_index()
)

seg_stats["Avg_Sale"] = seg_stats["Total_Sales"] / seg_stats["Num_Sales"].replace(0, 1)
seg_stats["Avg_Orders_per_Customer"] = seg_stats["Num_Sales"] / seg_stats["Num_Customers"].replace(0, 1)

# Format for display
seg_display = seg_stats.copy()
seg_display["Total_Sales"] = seg_display["Total_Sales"].map(lambda x: f"${x:,.2f}")
seg_display["Avg_Sale"] = seg_display["Avg_Sale"].map(lambda x: f"${x:,.2f}")
seg_display["Avg_Orders_per_Customer"] = seg_display["Avg_Orders_per_Customer"].map(lambda x: f"{x:,.2f}")

# Rename columns
seg_display = seg_display.rename(columns={
    "Segment": "Segment",
    "Num_Sales": "Num Sales",
    "Num_Customers": "Num Customers",
    "Avg_Orders_per_Customer": "Avg Orders per Customer",
    "Total_Sales": "Total Sales",
    "Avg_Sale": "Avg Sale"
})

# Column order
seg_display = seg_display[
    ["Segment", "Num Sales", "Num Customers",
     "Avg Orders per Customer", "Total Sales", "Avg Sale"]
]

# Style the table
styled = (
    seg_display.style
    .hide(axis="index")
    .set_table_styles([
        {"selector": "th", "props": [("text-align", "center"), ("font-size", "18px")]}
    ])
    .set_properties(
        subset=["Num Sales", "Num Customers", "Avg Orders per Customer"],
        **{"text-align": "center"}
    )
    .set_properties(
        subset=["Total Sales", "Avg Sale"],
        **{"text-align": "right"}
    )
)

st.markdown(styled.to_html(), unsafe_allow_html=True)
