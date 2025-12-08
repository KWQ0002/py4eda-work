import streamlit as st
import pandas as pd
import plotly.express as px

from loader import load_data  # shared train.csv loader


# ---------- Page config ----------
st.set_page_config(
    page_title="Sales Over Time",
    layout="wide"
)

# ---------- Load & prepare data ----------
df = load_data().copy()

# Make sure Order Date is datetime
df["Order Date"] = pd.to_datetime(df["Order Date"])

st.title("Sales Over Time")

st.markdown(
    """
Use this page to explore how sales change over time at different aggregation
levels (daily, weekly, monthly, quarterly, yearly). You can also filter and
break down results by product category.
"""
)

# ---------- Sidebar controls ----------
st.sidebar.header("Filters")

# Aggregation level
agg_label_to_freq = {
    "Daily": "D",
    "Weekly": "W",
    "Monthly": "M",
    "Quarterly": "Q",
    "Yearly": "Y",
}

agg_choice = st.sidebar.selectbox(
    "Aggregation level",
    options=list(agg_label_to_freq.keys()),
    index=2  # default to Monthly
)
freq = agg_label_to_freq[agg_choice]

# Segment filter (if present)
segments = sorted(df["Segment"].dropna().unique()) if "Segment" in df.columns else []
if segments:
    selected_segments = st.sidebar.multiselect(
        "Segments",
        options=segments,
        default=segments,
    )
else:
    selected_segments = segments  # empty list

# Region filter (if present)
regions = sorted(df["Region"].dropna().unique()) if "Region" in df.columns else []
if regions:
    selected_regions = st.sidebar.multiselect(
        "Regions",
        options=regions,
        default=regions,
    )
else:
    selected_regions = regions

# Category filter (if present)
categories = sorted(df["Category"].dropna().unique()) if "Category" in df.columns else []
if categories:
    selected_categories = st.sidebar.multiselect(
        "Product Categories",
        options=categories,
        default=categories,
    )
else:
    selected_categories = categories

# Checkbox to choose whether to break out lines by category
show_by_category = st.sidebar.checkbox(
    "Show separate lines by Category",
    value=False
)

# ---------- Date range selection ----------
min_date = df["Order Date"].min().date()
max_date = df["Order Date"].max().date()

date_range = st.sidebar.date_input(
    "Order Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

# Handle single-date vs range input
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date_raw, end_date_raw = date_range
else:
    start_date_raw = end_date_raw = date_range

# Align the selected dates to full periods for the chosen aggregation
start_ts_raw = pd.to_datetime(start_date_raw)
end_ts_raw = pd.to_datetime(end_date_raw)

start_period = pd.Period(start_ts_raw, freq=freq)
end_period = pd.Period(end_ts_raw, freq=freq)

aligned_start = start_period.start_time
aligned_end = end_period.end_time

# Clip to dataset bounds just in case
aligned_start = max(aligned_start, df["Order Date"].min())
aligned_end = min(aligned_end, df["Order Date"].max())

if (aligned_start.date() != start_date_raw) or (aligned_end.date() != end_date_raw):
    st.caption(
        f"Date range aligned to full **{agg_choice.lower()}** periods: "
        f"{aligned_start.date()} → {aligned_end.date()}."
    )

# ---------- Apply filters ----------
mask = (df["Order Date"] >= aligned_start) & (df["Order Date"] <= aligned_end)

if segments:
    mask &= df["Segment"].isin(selected_segments)
if regions:
    mask &= df["Region"].isin(selected_regions)
if categories:
    mask &= df["Category"].isin(selected_categories)

filtered = df[mask].copy()

if filtered.empty:
    st.warning("No data available for the selected filters and date range.")
    st.stop()

# ---------- Aggregate sales over time ----------
filtered = filtered.set_index("Order Date")

if show_by_category and "Category" in filtered.columns:
    # Group by Category and resample
    sales_over_time = (
        filtered
        .groupby("Category")["Sales"]
        .resample(freq)
        .sum()
        .reset_index()
    )

    # Add a nice Period label
    if agg_choice == "Daily":
        sales_over_time["Period"] = sales_over_time["Order Date"]
    else:
        period = sales_over_time["Order Date"].dt.to_period(freq)
        sales_over_time["Period"] = period.dt.to_timestamp()

else:
    # Aggregate across all categories (single line)
    sales_over_time = (
        filtered["Sales"]
        .resample(freq)
        .sum()
        .to_frame(name="Sales")
        .reset_index()
    )

    if agg_choice == "Daily":
        sales_over_time["Period"] = sales_over_time["Order Date"]
    else:
        period = sales_over_time["Order Date"].dt.to_period(freq)
        sales_over_time["Period"] = period.dt.to_timestamp()
    # Add a dummy Category column so plotting code can stay simple
    sales_over_time["Category"] = "All Categories"

# ---------- KPIs ----------
st.subheader("Summary")

total_sales = sales_over_time["Sales"].sum()
n_periods = sales_over_time["Period"].nunique()
avg_per_period = total_sales / n_periods if n_periods > 0 else 0

col1, col2, col3 = st.columns(3)
col1.metric("Total Sales", f"${total_sales:,.2f}")
col2.metric(f"Avg {agg_choice} Sales", f"${avg_per_period:,.2f}")
col3.metric("Number of Periods", f"{n_periods:,}")

# ---------- Plot ----------
st.subheader(f"Sales Over Time ({agg_choice})")

if show_by_category and "Category" in filtered.columns:
    fig = px.line(
        sales_over_time,
        x="Period",
        y="Sales",
        color="Category",
        markers=True,
        labels={
            "Period": "Date",
            "Sales": "Sales ($)",
            "Category": "Category"
        },
        title=f"Sales Over Time by Category ({agg_choice} Aggregation)"
    )
else:
    fig = px.line(
        sales_over_time,
        x="Period",
        y="Sales",
        markers=True,
        labels={
            "Period": "Date",
            "Sales": "Sales ($)"
        },
        title=f"Total Sales Over Time ({agg_choice} Aggregation)"
    )

fig.update_xaxes(showgrid=False)
fig.update_yaxes(tickprefix="$", showgrid=True)

st.plotly_chart(fig, use_container_width=True)

# ---------- Optional: show raw aggregated data ----------
with st.expander("Show aggregated data table"):
    show_cols = ["Period", "Sales"]
    if show_by_category:
        show_cols.insert(1, "Category")
    

    sales_over_time["Period"] = sales_over_time["Period"].dt.date
    styled_table = (
    sales_over_time[show_cols]
    .reset_index(drop=True)
    .style.format({"Sales": "${:,.2f}"})
    .set_properties(subset=["Sales"], **{"text-align": "right"})
    )

    st.dataframe(
        styled_table,
        use_container_width=True,
        hide_index=True
    )
