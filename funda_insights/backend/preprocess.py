import re
import pandas as pd
from funda_scraper.preprocess import find_n_room, find_n_bedroom, find_n_bathroom
from datetime import datetime
import locale


def extract_number(input_string):
    # Define the regex pattern to match numbers
    pattern = r'\b\d+(?:[,.]\d+){0,}\b'

    # Find all matches in the input string
    match = re.search(pattern, input_string)
    if match:
        # Convert the matched string to a float
        number = float(match.group().replace(".", "").replace(",", "."))
        return number
    else:
        return None


def clean_energy_label(input_string):
    # Define the regex pattern
    pattern = r'^([A-G])(\++)?'

    # Match the pattern in the input string
    match = re.match(pattern, input_string)
    if match:
        # Extract the first character and the plus signs (if any)
        first_char = match.group(1)
        plus_signs = match.group(2) or ''
        return first_char + plus_signs
    else:
        return None


def _combine_columns(df: pd.DataFrame) -> pd.DataFrame:
    verkocht_filter = df["Status"].isin(["Verkocht", "n.v.t."])
    df.loc[verkocht_filter, "aangeboden_sinds"] = df.loc[verkocht_filter][
        "aangeboden_sinds_pagina"]
    df.loc[verkocht_filter, "vraagprijs"] = df.loc[verkocht_filter][
        "laatste_vraagprijs"]
    nieuwbouw_filter = df["Soort bouw"] == "Nieuwbouw"
    df.loc[(nieuwbouw_filter) & (df["aangeboden_sinds"] == datetime.today().strftime(
        "%d-%m-%Y")), "aangeboden_sinds"] = None
    return df


def preprocess_df(df: pd.DataFrame) -> pd.DataFrame:
    # Info
    df["huis_id"] = df["url"].apply(lambda x: int(x.split("/")[-2].split("-")[1]))
    df["huis_type"] = df["url"].apply(lambda x: x.split("/")[-2].split("-")[0])

    # Numbers
    df["woon_oppervlakte"] = df["Wonen"].apply(extract_number)
    df["externe_bergruimte"] = df["Externe bergruimte"].apply(extract_number)
    df["periodieke_bijdrage"] = df["Periodieke bijdrage"].apply(extract_number)
    df["gebouwgebonden_buitenruimte"] = df["Gebouwgebonden buitenruimte"].apply(
        extract_number)
    df["achtertuin"] = df["Achtertuin"].apply(extract_number)
    df["vraagprijs"] = df["Vraagprijs"].apply(extract_number)
    df["laatste_vraagprijs"] = df["Laatste vraagprijs"].apply(extract_number)
    df["inhoud"] = df["Inhoud"].apply(extract_number)
    df["bijdrage_vve"] = df["Bijdrage VvE"].apply(extract_number)
    df["perceel_oppervlakte"] = df["Perceel"].apply(extract_number)
    df["oppervlakte"] = df["Oppervlakte"].apply(extract_number)
    df["bouwjaar"] = df["Bouwjaar"].apply(extract_number)
    df["huis_leeftijd"] = datetime.now().year - df["bouwjaar"]

    df["aantal_kamers"] = df["Aantal kamers"].apply(find_n_room)
    df["aantal_slaapkamers"] = df["Aantal kamers"].apply(find_n_bedroom)
    df["aantal_badkamers"] = df["Aantal badkamers"].apply(find_n_bathroom)

    df["energie_label"] = df["Energielabel"].apply(clean_energy_label)
    df["prijs_m2"] = round(df.vraagprijs / df.woon_oppervlakte, 1)

    # Location
    df["postcode"] = df["postcode"].apply(lambda x: x[:7])

    # date
    # Set the locale to Dutch
    locale.setlocale(locale.LC_TIME, 'nl_NL')

    df["aangeboden_sinds"] = pd.to_datetime(df['aangeboden_sinds'],
                                            errors='coerce',
                                            dayfirst=True,
                                            ).dt.strftime('%d-%m-%Y')

    df["verkoop_datum"] = pd.to_datetime(df['Verkoopdatum'],
                                         errors='coerce',
                                         format='%d %B %Y',
                                         ).dt.strftime('%d-%m-%Y')

    df["aangeboden_sinds_pagina"] = pd.to_datetime(df['Aangeboden sinds'],
                                                   errors='coerce',
                                                   format='%d %B %Y'
                                                   ).dt.strftime('%d-%m-%Y')

    locale.setlocale(locale.LC_TIME, '')
    df = _combine_columns(df)
    df.replace({'n.v.t.': None})
    return df


def select_columns_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df[
        [
            "url",
            "huis_id",
            "funda_global_house_id",
            "aangeboden_sinds",
            "verkoop_datum",
            "huis_type",
            "vraagprijs",
            "woon_oppervlakte",
            "perceel_oppervlakte",
            "oppervlakte",
            "inhoud",
            "prijs_m2",
            "Status",
            "gebied",
            "postcode",
            "buurt",
            "energie_label",
            "bouwjaar",
            "huis_leeftijd",
            "bekeken",
            "opgeslagen",
            "aantal_kamers",
            "aantal_slaapkamers",
            "aantal_badkamers",
            "Badkamervoorzieningen",
            "Soort woonhuis",
            "Soort bouw",
            "Eigendomssituatie",
            "Aantal woonlagen",
            "Gelegen op",
            "Ligging",
            "Balkon/dakterras",
            "Tuin",
            "Ligging tuin",
            "achtertuin",
            "Soort parkeergelegenheid",
            "gebouwgebonden_buitenruimte",
            "externe_bergruimte",
            "Schuur/berging",
            "Voorzieningen",
            "Soort dak",
            "Isolatie",
            "Cv-ketel",
            "Verwarming",
            "Warm water",
            "Aanvaarding",
            "Specifiek",
            "Opstalverzekering",
            "Inschrijving KvK",
            "Soort appartement",
            "bijdrage_vve",
            "periodieke_bijdrage",
            "Jaarlijkse vergadering",
            "Reservefonds aanwezig",
            "Onderhoudsplan",
            "omschrijving",
        ]
    ]

    formatted_cols = [col.replace(" ", "_").replace("/", "_").replace("-", "_").lower()
                      for col in df.columns]
    df.columns = formatted_cols

    return df


def create_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    preprocessed_df = preprocess_df(df)
    df_selected_columns = select_columns_df(preprocessed_df)

    df_final = df_selected_columns.sort_values(by="aangeboden_sinds",
                                               ascending=False)
    return df_final
