import streamlit as st
import pandas as pd
import altair as alt


def count_records_per_year_month(dataframe, date_column):
    # Convert the date column to datetime format
    dataframe[date_column] = pd.to_datetime(dataframe[date_column],
                                            dayfirst=True)

    # Create a new column for year-month combination
    dataframe[f'year_month'] = dataframe[date_column].dt.to_period('M')

    # Count the number of records per year-month combination
    counts = dataframe['year_month'].value_counts().sort_index().reset_index()
    counts["year_month"] = counts["year_month"].astype(str)

    return counts


def create_grouped_count_bar_chart(counts_offered, counts_sold):
    counts_combined = pd.merge(counts_offered, counts_sold, on="year_month", how='left')

    counts_combined.fillna(0, inplace=True)
    counts_combined.columns = ["year_month", "count_offered", "count_sold"]

    # Plot grouped bar chart
    df_melted = counts_combined.melt(id_vars='year_month',
                                     var_name='count_type',
                                     value_name='count')

    chart = (
        alt.Chart(df_melted)
        .mark_bar()
        .encode(x=alt.X('count_type', axis=alt.Axis(title='')),
                y="count",
                color="count_type",
                column=alt.Column('year_month', title='Year-Month'))
    ).properties(width=50, height=400)
    st.altair_chart(chart)


def create_bar_chart_number_of_houses_per_month(data):

    # Offered houses
    st.subheader('Number of offered houses per year-month')
    counts_per_year_month_offered = count_records_per_year_month(data,
                                                                 'aangeboden_sinds')

    st.bar_chart(data=counts_per_year_month_offered,
                 x="year_month",
                 y="count",
                 use_container_width=True,
                 )

    # sold houses
    st.subheader('Number of sold houses per year-month')
    counts_per_year_month_sold = count_records_per_year_month(data,
                                                              'verkoop_datum')

    st.bar_chart(data=counts_per_year_month_sold,
                 x="year_month",
                 y="count"
                 )

    st.subheader('Number of offered and sold houses per year-month')

    # offered and sold houses
    create_grouped_count_bar_chart(counts_per_year_month_offered,
                                   counts_per_year_month_sold,
                                   )

