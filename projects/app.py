import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from loader import load_data

df = load_data()

if st.button("Refresh App"):
    st.rerun()
st.markdown("**About this Project**")
st.markdown("This interactive dashboard was developed as part of the INSY 6500" \
" Exploratory Data Analysis project at Auburn University. " \
"The goal is to explore customer purchasing behavior and sales performance using real transactional data.")

#Dashboards that could add value
#Overall sales dashboard with date and segment breakdown
#Customer spend dashboard that shows who is purchasing the most, and how many orders they are placing
#Heatmap in the shape of a US map for sales that when you click a sate it opens up a zip code based map also
#Shipping delay time to assess if any orders stand out over a threshold for KPI purposes
#Sales over time based on selection of daily, monthly quarterly, etc. Inside of a date range that is truncated so if they choose quarterly they can't accidently select 17 weeks. Or after they have selected the time interval in the side, have it change the selectable date range.

