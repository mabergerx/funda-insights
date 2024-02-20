import streamlit as st
import pandas as pd
import numpy as np


class FilterFunctionality:
    def __init__(self,
                 original_data: pd.DataFrame,
                 filtered_data: pd.DataFrame = None):
        self.original_data = original_data
        self.filtered_data = filtered_data
        self.locations = self.original_data.gebied.unique()
        self.status = self.original_data.status.unique()
        self.max_ask_price = 1000000
        self.square_meters_living_range = (
            int(self.original_data.woon_oppervlakte.min()),
            int(self.original_data.woon_oppervlakte.max())
        )
        self.from_date = self.original_data.aangeboden_sinds.min()
        self.energy_label = ["A (of hoger)", "B", "C", "D", "E", "F", "G", np.nan]
        self.property_type = ["huis", "appartement"]
        self.house_type = ["2-onder-1-kapwoning", "Eindwoning", "Grachtenpand",
                           "Geschakelde woning", "Herenhuis", "Hoekwoning",
                           "Tussenwoning", "Vrijstaand", "Villa"]
        self.kind_of_building = ["Bestaande bouw", "Nieuwbouw"]
        self.bouwjaar = (
            int(self.original_data.bouwjaar.min()),
            int(self.original_data.bouwjaar.max())
        )
        self.number_of_bedrooms = 1
        self.has_garden = "Doesn't matter"

    def show_filters(self):
        self.locations = st.multiselect(
            "Cities you want to analyse :earth_africa:",
            self.original_data.gebied.unique(),
            self.original_data.gebied.unique()
        )

        self.status = st.multiselect(
            "Status :sparkles:",
            self.original_data.status.unique(),
            self.original_data.status.unique()
        )

        self.max_ask_price = st.number_input(
            label="Maximum ask price in euro's :moneybag:",
            min_value=int(self.original_data.vraagprijs.min()),
            max_value=int(self.original_data.vraagprijs.max()),
            value=int(self.original_data.vraagprijs.max()),
            step=1000,
        )

        self.square_meters_living_range = st.slider(
            label="Living area in square meters",
            min_value=int(self.original_data.woon_oppervlakte.min()),
            max_value=int(self.original_data.woon_oppervlakte.max()),
            value=(
                int(self.original_data.woon_oppervlakte.min()),
                int(self.original_data.woon_oppervlakte.max())
            ),
            step=1,
        )

        self.from_date = st.date_input(
            "FROM date :date:",
            value=self.original_data.aangeboden_sinds.min()
        )

        self.energy_label = st.multiselect(
            "Energy label :zap:",
            ["A++++", "A+++", "A++", "A+", "A", "B", "C", "D", "E", "F", "G", np.nan],
            ["A++++", "A+++", "A++", "A+", "A", "B", "C", "D", "E", "F", "G", np.nan],
        )

        self.property_type = st.multiselect(
            "Property type :house:",
            self.original_data.huis_type.unique(),
            ["huis", "appartement"]
        )

        self.house_type = st.multiselect(
            "Type of house :classical_building:",
            ["2-onder-1-kapwoning", "Eindwoning", "Grachtenpand", "Geschakelde woning",
             "Herenhuis", "Hoekwoning", "Tussenwoning", "Vrijstaand", "Villa", "n.v.t."],
            ["2-onder-1-kapwoning", "Eindwoning", "Grachtenpand", "Geschakelde woning",
             "Herenhuis", "Hoekwoning", "Tussenwoning", "Vrijstaand", "Villa", "n.v.t."]
        )

        self.kind_of_building = st.multiselect(
            "Kind of building",
            ["Bestaande bouw", "Nieuwbouw"],
            ["Bestaande bouw", "Nieuwbouw"],
        )

        self.bouwjaar = st.slider(
            label="Construction year :building_construction:",
            min_value=int(self.original_data.bouwjaar.min()),
            max_value=int(self.original_data.bouwjaar.max()),
            value=(
                int(self.original_data.bouwjaar.min()),
                int(self.original_data.bouwjaar.max())
            ),
            step=1,
        )

        self.number_of_bedrooms = st.number_input(
            label="Minimum number of bedrooms :bed:",
            min_value=int(self.original_data.aantal_slaapkamers.min()),
            max_value=int(self.original_data.aantal_slaapkamers.max()),
            step=1,
        )

        self.has_garden = st.radio(
            "Has a garden :house_with_garden:",
            ["Doesn't matter", "Yes", "No"]
        )

    def _filter_house_type(self):
        temp_column = self.filtered_data["soort_woonhuis"].str.lower()
        substrings = [substring.lower() for substring in self.house_type]
        self.filtered_data = self.filtered_data[
            temp_column.str.contains('|'.join(substrings))]

    def _filter_has_garden(self):
        if self.has_garden == "Yes":
            self.filtered_data = self.filtered_data[
                self.filtered_data.tuin.str.contains("tuin")]
        if self.has_garden == "No":
            self.filtered_data = self.filtered_data[
                ~self.filtered_data.tuin.str.contains("tuin")]

    def filter_data(self):
        self.filtered_data = self.original_data[self.original_data.gebied.isin(
            self.locations)]

        self.filtered_data = self.filtered_data[self.filtered_data.status.isin(
            self.status)]

        self.filtered_data = self.filtered_data[self.filtered_data.vraagprijs <
            self.max_ask_price]

        self.filtered_data = self.filtered_data[(
                (self.original_data.woon_oppervlakte >=
                 self.square_meters_living_range[0]) &
                (self.original_data.woon_oppervlakte <=
                 self.square_meters_living_range[1])
            )
        ]

        self.filtered_data = self.filtered_data[self.original_data.aangeboden_sinds >=
                                                pd.to_datetime(self.from_date)]

        self.filtered_data = self.filtered_data[self.original_data.huis_type.isin(
            self.property_type)]

        self.filtered_data = self.filtered_data[self.original_data.huis_type.isin(
            self.property_type)]

        self.filtered_data = self.filtered_data[self.original_data.soort_bouw.isin(
            self.kind_of_building)]

        self.filtered_data = self.filtered_data[(
                (self.original_data.bouwjaar >= self.bouwjaar[0]) &
                (self.original_data.bouwjaar <= self.bouwjaar[1])
            )
        ]

        self.filtered_data = self.filtered_data[self.original_data.aantal_slaapkamers >=
                                                self.number_of_bedrooms]

        self.filtered_data = self.filtered_data[self.original_data.energie_label.isin(
            self.energy_label)]

        self._filter_house_type()
        self._filter_has_garden()
