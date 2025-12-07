# data_load.py
import pandas as pd
import streamlit as st

@st.cache_data
def load_data():
    df = pd.read_csv(
        "Data/train.csv",
        parse_dates=["Order Date", "Ship Date"],
        dayfirst=True,
        dtype={
            "Order ID": "category",
            "Ship Mode": "category",
            "Customer ID": "category",
            "Segment": "category",
            "Country": "category",
            "City": "category",
            "State": "category",
            "Postal Code": "category",
            "Region": "category",
            "Product ID": "category",
            "Category": "category",
            "Sub-Category": "category",
            "Product Name": "category",
        },
    )
    return df