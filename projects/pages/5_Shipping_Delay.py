import streamlit as st
import pandas as pd
import plotly.express as px

from loader import load_data  # shared train.csv loader


# ---------- Page config ----------
st.set_page_config(
    page_title="Shipping Delay KPI Dashboard",
    layout="wide"
)

# ---------- Load & prepare data ----------
df = load_data().copy()

# Ensure datetime types
for col in ["Order Date", "Ship Date"]:
    df[col] = pd.to_datetime(df[col])

# Compute shipping delay in days
df["Delay_Days"] = (df["Ship Date"] - df["Order Date"]).dt.days

st.title("Shipping Delay KPI Dashboard")

st.markdown(
    """
Use this dashboard to monitor shipping performance, identify late orders, and
assess whether your shipping is meeting KPI targets.
"""
)

# ---------- Sidebar filters ----------
st.sidebar.header("Filters")

# Segment filter
segments = sorted(df["Segment"].dropna().unique()) if "Segment" in df.columns else []
if segments:
    selected_segments = st.sidebar.multiselect(
        "Segments",
        options=segments,
        default=segments,
    )
else:
    selected_segments = segments  # empty list

# Region filter
regions = sorted(df["Region"].dropna().unique()) if "Region" in df.columns else []
if regions:
    selected_regions = st.sidebar.multiselect(
        "Regions",
        options=regions,
        default=regions,
    )
else:
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

# Date range filter (based on Order Date)
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
    value=min(3, max_delay),
    help="Orders with delay greater than this number of days will be flagged as late."
)

# ---------- Apply filters ----------
mask = (
    (df["Order Date"].dt.date >= start_date)
    & (df["Order Date"].dt.date <= end_date)
)

if segments:
    mask &= df["Segment"].isin(selected_segments)
if regions:
    mask &= df["Region"].isin(selected_regions)
if ship_modes:
    mask &= df["Ship Mode"].isin(selected_ship_modes)

filtered = df[mask].copy()

if filtered.empty:
    st.warning("No data available for the selected filters.")
    st.stop()

filtered["Is_Late"] = filtered["Delay_Days"] > threshold_days

# ---------- Build ORDER-LEVEL view for KPIs & % late ----------
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

# ---------- Charts row 1: distribution & by ship mode ----------
st.subheader("Delay Distributions")

c1, c2 = st.columns(2)

with c1:
    st.markdown("**Distribution of Shipping Delay (line-item level)**")
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

with c2:
    if "Ship Mode" in filtered.columns:
        st.markdown("**Delay by Ship Mode (line-item level)**")
        fig_box = px.box(
            filtered,
            x="Ship Mode",
            y="Delay_Days",
            points="all",
            labels={
                "Ship Mode": "Ship Mode",
                "Delay_Days": "Shipping Delay (days)"
            },
            title="Shipping Delay by Ship Mode"
        )
        st.plotly_chart(fig_box, use_container_width=True)
    else:
        st.info("No `Ship Mode` column found in data.")

# ---------- Charts row 2: late % and late count over time (ORDER-LEVEL) ----------
st.subheader("Late Orders Over Time (Order-level)")

order_level["OrderMonth"] = (
    order_level["OrderDate"].dt.to_period("M").dt.to_timestamp()
)

late_over_time = (
    order_level
    .groupby("OrderMonth", observed=False)
    .agg(
        total_orders=("Order ID", "nunique"),
        late_orders=("Is_Late", "sum"),
    )
    .reset_index()
)
late_over_time["pct_late"] = (
    late_over_time["late_orders"] / late_over_time["total_orders"] * 100
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

# ---------- Detailed late orders table ----------
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

    st.caption("Showing late line-items (sorted by longest delay).")

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