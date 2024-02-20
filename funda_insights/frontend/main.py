import streamlit as st
import pandas as pd

from utils import (
    get_average_price_for_selection,
    get_funda_avg_asking_price,
)
from funda_insights.frontend.visualizations import (
    create_bar_chart_number_of_houses_per_month,
)
from funda_insights.frontend.filters import (
    FilterFunctionality
)


@st.cache_data()
def load_data(file_path):
    return pd.read_csv(file_path, sep=";")


df = load_data("./data/funda_data_gouda_all_20240209_1_1548.csv")
df["aangeboden_sinds"] = pd.to_datetime(df["aangeboden_sinds"],
                                        dayfirst=True)

filter_functionality = FilterFunctionality(
    original_data=df,
    filtered_data=df
)

with st.sidebar:
    st.header("Filters")
    use_filters = st.toggle("Use filters?")
    if use_filters:
        filter_functionality.show_filters()
        filter_functionality.filter_data()


st.header(f"Filtered data")
st.write(f"Number of houses before filters: "
         f"{filter_functionality.original_data.shape[0]}")
st.write(f"Number of houses after filters: "
         f"{filter_functionality.filtered_data.shape[0]}")
st.write(filter_functionality.filtered_data)

st.header(f"Average prices for filtered data")
st.write(
    f"Average house price in selection: "
    f"{get_average_price_for_selection(filter_functionality.filtered_data)}")
st.write(
    f"Average house price in {filter_functionality.locations[0]} according to funda: "
    f"{get_funda_avg_asking_price(filter_functionality.locations[0])}")

st.header(f"Statistics over time on all data")
create_bar_chart_number_of_houses_per_month(filter_functionality.original_data)



