import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from loader import load_data

df = load_data()

if st.button("Refresh App"):
    st.rerun()