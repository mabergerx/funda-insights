import streamlit as st
import pandas as pd

from utils import (filter_on_dates, get_previous_date, get_average_price_for_selection, 
                   get_funda_avg_asking_price, get_average_price_per_energielabel)

with st.sidebar:
    
    location = st.text_input(
        "Where?",
        value="Weesp"
    )
    
    from_date = st.date_input(
        "Choose FROM date",
        value=get_previous_date()
    )
    to_date = st.date_input(
        "Choose THROUGH date",
        value="today"
    )
    
    energy_label = st.selectbox(
        "Energy label",
        options=["A", "B", "C", 
                 "D", "E", "F", "G"]
    )

st.header("Houses within the selected date range")

funda_examples = pd.read_csv("data/funda_data_gouda_available_20240126.csv")

filtered = filter_on_dates(funda_examples, from_date, to_date)

st.write(filtered)

"---"

st.subheader(f"Average house price in selection: {get_average_price_for_selection(filtered)}")
st.subheader(f"Average house price in {location} according to funda: {get_funda_avg_asking_price(location)}")

"---"

st.write(get_average_price_per_energielabel(filtered, label=energy_label))