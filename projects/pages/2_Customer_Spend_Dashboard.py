import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from loader import load_data   # shared data loader


# ---------- Page Config ----------
st.set_page_config(
    page_title="Customer Spend Dashboard",
    layout="wide"
)

df = load_data()

st.title("Customer Spend Dashboard")

# ---------- Sidebar Filters ----------
st.sidebar.header("Filters")

# Segment selector
all_segments = sorted(df["Segment"].dropna().unique())
default_segments = [s for s in all_segments if s in ["Corporate", "Home Office"]]

selected_segments = st.sidebar.multiselect(
    "Segments",
    options=all_segments,
    default=default_segments,
)

# Date range selector
date_range = st.sidebar.date_input(
    "Order Date Range",
    value=(df["Order Date"].min(), df["Order Date"].max())
)

# Apply date filter
mask = df["Order Date"].between(
    pd.to_datetime(date_range[0]),
    pd.to_datetime(date_range[1])
)
df_filtered = df[mask]

# ---------- Sidebar: Rank Range Slider ----------
st.sidebar.subheader("Customer Rank Range")

rank_range = st.sidebar.slider(
    "Select Customer Rank Range",
    min_value=1,
    max_value=300,
    value=(1, 10)
)

min_rank, max_rank = rank_range

# Enforce maximum of 25 customers
if (max_rank - min_rank + 1) > 25:
    max_rank = min_rank + 24
    st.sidebar.warning("Maximum display is 25 customers. Range has been limited.")

st.markdown("---")
st.subheader("Top Customers by Segment")

# ---------- Main Content ----------
if not selected_segments:
    st.info("Select at least one segment from the sidebar to see results.")
else:
    for seg in selected_segments:
        seg_df = df_filtered[df_filtered["Segment"] == seg]

        st.markdown(f"## {seg}")

        if seg_df.empty:
            st.info(f"No data for {seg} in this date range.")
            continue

        # ---- Aggregate by customer ----
        top_customers = (
            seg_df.groupby(["Customer ID", "Customer Name"], observed=True)
                  .agg(
                      Total_Sales=("Sales", "sum"),
                      Num_Orders=("Order ID", "nunique"),
                      Avg_Order_Value=("Sales", lambda x: x.sum() / max(len(x), 1)),
                  )
                  .sort_values("Total_Sales", ascending=False)
                  .reset_index()
        )

        # Add Rank column (1-based)
        top_customers["Rank"] = top_customers.index + 1

        # ---- Apply rank filter & enforce max 25 ----
        filtered_customers = top_customers[
            (top_customers["Rank"] >= min_rank) &
            (top_customers["Rank"] <= max_rank)
        ].copy()

        filtered_customers = filtered_customers.head(25)

        if filtered_customers.empty:
            st.info(f"No customers in the selected rank range for {seg}.")
            continue

        # For display: nicer column names
        display_df = filtered_customers.rename(columns={
            "Num_Orders": "Num Orders",
            "Total_Sales": "Total Sales",
            "Avg_Order_Value": "Avg Order Value",
        })

        # ---------- Charts (use filtered customers) ----------
        col1, col2 = st.columns(2)

        # Chart 1: Total Sales
        with col1:
            st.caption(
                f"Customers Rank {min_rank}–{max_rank} by Total Sales – {seg}"
            )
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.barh(display_df["Customer Name"], display_df["Total Sales"])
            ax.set_xlabel("Total Sales ($)")
            ax.invert_yaxis()
            ax.ticklabel_format(style="plain", axis="x")
            st.pyplot(fig)

        # Chart 2: Number of Orders
        with col2:
            st.caption(
                f"Customers Rank {min_rank}–{max_rank} by Number of Orders – {seg}"
            )
            fig2, ax2 = plt.subplots(figsize=(6, 4))
            ax2.barh(display_df["Customer Name"], display_df["Num Orders"])
            ax2.set_xlabel("Order Count")
            ax2.invert_yaxis()
            st.pyplot(fig2)

        # ---------- Styled Table ----------
        # Ensure column order
        display_df = display_df[
            ["Rank", "Customer ID", "Customer Name",
             "Num Orders", "Total Sales", "Avg Order Value"]
        ]

        styled_table = (
            display_df.style
                .hide(axis="index")
                .set_table_styles([
                    {"selector": "th",
                     "props": [("font-size", "24px"),
                               ("text-align", "center")]},
                    {"selector": "td",
                     "props": [("font-size", "18px")]}
                ])
                .set_properties(subset=["Total Sales"], **{"text-align": "right"})
                .set_properties(subset=["Avg Order Value"], **{"text-align": "right"})
                .set_properties(subset=["Num Orders"], **{"text-align": "center"})
                .format({
                    "Total Sales": "${:,.2f}".format,
                    "Avg Order Value": "${:,.2f}".format,
                })
        )

        st.markdown(styled_table.to_html(), unsafe_allow_html=True)
        st.markdown("---")
