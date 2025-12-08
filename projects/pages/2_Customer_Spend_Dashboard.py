import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from loader import load_data   # shared data loader


#setup the page
st.set_page_config(
    page_title="Customer Spend Dashboard",
    layout="wide"
)
#Load data
df = load_data()

#page title
st.title("Customer Spend Dashboard")

#filters
st.sidebar.header("Filters")

#segment selector
all_segments = sorted(df["Segment"].dropna().unique())
default_segments = [s for s in all_segments if s in ["Corporate", "Home Office"]]

selected_segments = st.sidebar.multiselect(
    "Segments",
    options=all_segments,
    default=default_segments,
)

#date range
date_range = st.sidebar.date_input(
    "Order Date Range",
    value=(df["Order Date"].min(), df["Order Date"].max())
)

#generate the mask for use later
mask = df["Order Date"].between(
    pd.to_datetime(date_range[0]),
    pd.to_datetime(date_range[1])
)
df_filtered = df[mask]

#give the range of customer ranks and ability to select upper and lower bound
st.sidebar.subheader("Customer Rank Range")

rank_range = st.sidebar.slider(
    "Select Customer Rank Range",
    min_value=1,
    max_value=300,
    value=(1, 10)
)

min_rank, max_rank = rank_range

#only set 25, if they pick more than 25 go from the min (who spent the most in their range) back 24.
if (max_rank - min_rank + 1) > 25:
    max_rank = min_rank + 24
    st.sidebar.warning("Maximum display is 25 customers. Range has been limited.")

st.markdown("---") #draw a line to visually break
st.subheader("Top Customers by Segment") 

#plots
if not selected_segments:
    st.info("Select at least one segment from the sidebar to see results.") #if they haven't made a selection have them make one
else:
    for seg in selected_segments:
        seg_df = df_filtered[df_filtered["Segment"] == seg] #take the already date filtered data set and then mask off by segment

        st.markdown(f"## {seg}") #heading level 2 with segment listed

        if seg_df.empty:
            st.info(f"No data for {seg} in this date range.") #another warning so the user doesn't view nothing
            continue

        
        top_customers = ( #generate the top customers table from the datafram put together for the segments
            seg_df.groupby(["Customer ID", "Customer Name"], observed=True)
                  .agg(
                      Total_Sales=("Sales", "sum"),
                      Num_Orders=("Order ID", "nunique"),
                      Avg_Order_Value=("Sales", lambda x: x.sum() / max(len(x), 1)),
                  )
                  .sort_values("Total_Sales", ascending=False)
                  .reset_index()
        )

        
        top_customers["Rank"] = top_customers.index + 1 #humans don't think from 0 index traditionally, display from 1

    
        filtered_customers = top_customers[ #go between the two ranks and pull out the 25
            (top_customers["Rank"] >= min_rank) &
            (top_customers["Rank"] <= max_rank)
        ].copy()

        filtered_customers = filtered_customers.head(25) #print 25 filtered customers, which is all of them, 25 could have been put in as a variable to make the code more robust if I wanted to change this later like num_top_cust

        if filtered_customers.empty:
            st.info(f"No customers in the selected rank range for {seg}.")
            continue

        
        display_df = filtered_customers.rename(columns={ #remove _ from names
            "Num_Orders": "Num Orders",
            "Total_Sales": "Total Sales",
            "Avg_Order_Value": "Avg Order Value",
        })

        # ---------- Charts (use filtered customers) ----------
        col1, col2 = st.columns(2)

        #chart 1: Total Sales
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

        #chart 2: Number of Orders
        with col2:
            st.caption(
                f"Customers Rank {min_rank}–{max_rank} by Number of Orders – {seg}"
            )
            fig2, ax2 = plt.subplots(figsize=(6, 4))
            ax2.barh(display_df["Customer Name"], display_df["Num Orders"])
            ax2.set_xlabel("Order Count")
            ax2.invert_yaxis()
            st.pyplot(fig2)

        #table
        display_df = display_df[ #put things in the right order
            ["Rank", "Customer ID", "Customer Name",
             "Num Orders", "Total Sales", "Avg Order Value"]
        ]

        styled_table = ( #format so it looks nice
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
