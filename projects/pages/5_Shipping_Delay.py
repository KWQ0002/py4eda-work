import streamlit as st
import pandas as pd
import plotly.express as px

from loader import load_data  # shared train.csv loader


#setup the page
st.set_page_config(
    page_title="Shipping Delay KPI Dashboard",
    layout="wide"
)

#Page title
st.title("Shipping Delay KPI Dashboard")

#Load data
df = load_data()

#clean up datetime
for col in ["Order Date", "Ship Date"]:
    df[col] = pd.to_datetime(df[col])

#Compute shipping delay in days
df["Delay_Days"] = (df["Ship Date"] - df["Order Date"]).dt.days



st.markdown(
    """
Use this dashboard to monitor shipping performance, identify late orders, and
assess whether your shipping is meeting KPI targets.
"""
)

#Filters
st.sidebar.header("Filters")

# Segment filter
segments = sorted(df["Segment"].dropna().unique()) if "Segment" in df.columns else [] #if regions is not a column set as empty list
if segments:#if regions is not an empty list set selected regions based on this
    selected_segments = st.sidebar.multiselect(
        "Segments",
        options=sorted(df["Segment"].dropna().unique()),
        default=sorted(df["Segment"].dropna().unique())
    )
else:#if it is an empty list, set it to empty
    selected_segments = segments  # empty list

# Region filter
regions = sorted(df["Region"].dropna().unique()) if "Region" in df.columns else [] #if regions is not a column set as empty list
if regions: #if regions is not an empty list set selected regions based on this
    selected_regions = st.sidebar.multiselect(
        "Regions",
        options=regions,
        default=regions,
    )
else: #if it is an empty list, set it to empty
    selected_regions = regions

# Ship Mode filter
ship_modes = sorted(df["Ship Mode"].dropna().unique()) if "Ship Mode" in df.columns else []
if ship_modes:
    selected_ship_modes = st.sidebar.multiselect(
        "Ship Modes",
        options=ship_modes,
        default=ship_modes,
    )
else:
    selected_ship_modes = ship_modes

# Date range filter
min_date = df["Order Date"].min().date()
max_date = df["Order Date"].max().date()

date_range = st.sidebar.date_input(
    "Order Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

# KPI threshold slider (late if Delay_Days > threshold)
max_delay = int(df["Delay_Days"].max()) if not df["Delay_Days"].isna().all() else 0
if max_delay < 1:
    max_delay = 1  # avoid zero-range slider

threshold_days = st.sidebar.slider(
    "Late order threshold (days)",
    min_value=0,
    max_value=max_delay,
    value=min(3, max_delay), #set the default to 3
    help="Orders with delay greater than this number of days will be flagged as late."
)

#apply filters
mask = (
    (df["Order Date"].dt.date >= start_date)
    & (df["Order Date"].dt.date <= end_date)
)

if segments: #if there is a filter for segments not an empty list
    mask &= df["Segment"].isin(selected_segments)
if regions: #if there is a filter for regions not an empty
    mask &= df["Region"].isin(selected_regions)
if ship_modes: #if there is a filter for ship modes, not an empty list
    mask &= df["Ship Mode"].isin(selected_ship_modes)

filtered = df[mask].copy()

if filtered.empty: #don't leave the user hanging on information
    st.warning("No data available for the selected filters.")
    st.stop()

filtered["Is_Late"] = filtered["Delay_Days"] > threshold_days #set is late to a boolean on the number of days elapsed

#tabular view
# Each order counted once; an order is late if ANY line is late.
if "Order ID" in filtered.columns:
    order_level = (
        filtered
        .groupby("Order ID", as_index=False)
        .agg(
            OrderDate=("Order Date", "min"),
            Delay_Days=("Delay_Days", "max"),   # worst delay in the order
            Is_Late=("Is_Late", "max")          # True if any line is late
        )
    )
else:
    order_level = pd.DataFrame(columns=["Order ID", "OrderDate", "Delay_Days", "Is_Late"])

if order_level.empty:
    st.warning("No valid order-level records found after filtering.")
    st.stop()

# ---------- High-level KPIs ----------
st.subheader("Shipping KPI Overview")

# KPIs based on unique orders
total_orders = len(order_level)
late_orders_count = int(order_level["Is_Late"].sum())
avg_delay = order_level["Delay_Days"].mean()
p95_delay = order_level["Delay_Days"].quantile(0.95)
pct_late = late_orders_count / total_orders * 100 if total_orders > 0 else 0.0

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Orders", f"{total_orders:,}")
col2.metric("Average Delay (days)", f"{avg_delay:.2f}")
col3.metric("95th Percentile Delay (days)", f"{p95_delay:.2f}")
col4.metric("Late Orders", f"{late_orders_count:,}")       # absolute count
col5.metric("% Orders Late", f"{pct_late:.1f}%")           # order-level %

#charts
st.subheader("Delay Distributions")

c1, c2 = st.columns(2)

with c1:
    st.markdown("**Distribution of Shipping Delay (line-item level)**") #histogram of number of orders and how many days. Colored based on late or not.
    fig_hist = px.histogram(
        filtered,
        x="Delay_Days",
        color="Is_Late",
        nbins=20,
        barmode="overlay",
        labels={
            "Delay_Days": "Shipping Delay (days)",
            "Is_Late": f"Late (> {threshold_days} days)"
        },
        title="Shipping Delay Distribution",
        color_discrete_map={
            False: "#ADD8E6",   # light blue for NOT late
            True:  "#00008B"    # dark blue for LATE
        }
    )
    fig_hist.update_layout(legend_title_text="Late?")
    st.plotly_chart(fig_hist, use_container_width=True)

with c2: #show a box plot with tails and also plot the occurences next to it.
    if "Ship Mode" in filtered.columns:
        st.markdown("**Delay by Ship Mode (line-item level)**")
        fig_box = px.box(
            filtered,
            x="Ship Mode",
            y="Delay_Days",
            points="all", #add the overlaid dots
            labels={
                "Ship Mode": "Ship Mode",
                "Delay_Days": "Shipping Delay (days)"
            },
            title="Shipping Delay by Ship Mode"
        )
        st.plotly_chart(fig_box, use_container_width=True)
    else:
        st.info("No `Ship Mode` column found in data.")

#second row of charts
st.subheader("Late Orders Over Time (Order-level)")

order_level["OrderMonth"] = (
    order_level["OrderDate"].dt.to_period("M").dt.to_timestamp()
)

late_over_time = ( #pull out number of orders that were late and the total number of orders
    order_level
    .groupby("OrderMonth", observed=False)
    .agg(
        total_orders=("Order ID", "nunique"),
        late_orders=("Is_Late", "sum"),
    )
    .reset_index()
)
late_over_time["pct_late"] = (
    late_over_time["late_orders"] / late_over_time["total_orders"] * 100 #create the percentage
)

c3, c4 = st.columns(2)

# % Late over time (line)
with c3:
    fig_time_pct = px.line(
        late_over_time,
        x="OrderMonth",
        y="pct_late",
        markers=True,
        labels={
            "OrderMonth": "Order Month",
            "pct_late": "% Orders Late",
        },
        title="% of Late Orders Over Time (Order-level)",
    )
    st.plotly_chart(fig_time_pct, use_container_width=True)

# Late orders by absolute count (bar)
with c4:
    fig_time_count = px.bar(
        late_over_time,
        x="OrderMonth",
        y="late_orders",
        labels={
            "OrderMonth": "Order Month",
            "late_orders": "Late Orders (count)",
        },
        title="Late Orders (Count) Over Time (Order-level)",
    )
    st.plotly_chart(fig_time_count, use_container_width=True)

# table
st.subheader(f"Orders Exceeding Threshold (> {threshold_days} days)")

late_orders_df = filtered[filtered["Is_Late"]].copy()
if late_orders_df.empty:
    st.success("Great! No orders exceed the late threshold for the current filters.")
else:
    # Choose a set of useful columns if they exist
    cols = []
    for col in [
        "Order ID",
        "Order Date",
        "Ship Date",
        "Delay_Days",
        "Customer ID",
        "Customer Name",
        "Region",
        "State",
        "City",
        "Ship Mode",
        "Sales"
    ]:
        if col in late_orders_df.columns:
            cols.append(col)

    table = late_orders_df[cols].sort_values("Delay_Days", ascending=False).copy()

    # Show only date (no time) for Order Date / Ship Date
    for dcol in ["Order Date", "Ship Date"]:
        if dcol in table.columns:
            table[dcol] = table[dcol].dt.date

    st.caption("Showing late line-items (sorted by longest delay).") #this does not dynamically update if the user changes sort

    # Use Styler to format Sales as dollars and right-align
    styled_table = (
        table
        .reset_index(drop=True)
        .style
        .format({"Sales": "${:,.2f}"})                # dollar format
        .set_properties(subset=["Sales"],
                        **{"text-align": "right"})    # right-align Sales
    )

    st.dataframe(
        styled_table,
        use_container_width=True,
        hide_index=True,
    )