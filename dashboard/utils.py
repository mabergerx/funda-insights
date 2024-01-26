import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import requests

def get_previous_date(delta_days=7):
    
    # get today
    today = datetime.today()
    
    # Create a timedelta object representing 5 days
    delta = timedelta(days=delta_days)
    
    return today - delta


def filter_on_dates(data, from_date, to_date):
    # Convert the 'date_column' from object type to datetime type
    data['published_at'] = pd.to_datetime(data['published_at'])
    
    # Define start and end datetimes
    start_date = pd.to_datetime(from_date)
    end_date = pd.to_datetime(to_date)
    
    filtered_data = data[(data['published_at'] >= start_date) & (data['published_at'] <= end_date)]
    
    return filtered_data


def get_average_price_for_selection(data):
    prices = data["Vraagprijs"].to_list()
    
    def clean_price(price):
        return int("".join(char for char in price if char.isdigit()))
    
    return int(np.mean([clean_price(price) for price in prices]))


def get_funda_avg_asking_price(location):
    return requests.get(f"https://marketinsights.funda.io/v1/LocalInsights/preview/{location.lower()}").json()['marketInsightsMetrics']['averageAskingPrice']['value']
    
    
def get_price_per_sq_m():
    pass

def get_average_price_per_energielabel(data, label="C"):
    
    def clean_label(label):
        return label.replace("Wat betekent dit?", "")
    
    data["Energielabel"] = data.Energielabel.apply(clean_label)
    
    data_for_label = data[data["Energielabel"].str.contains(label)]
    
    return data_for_label