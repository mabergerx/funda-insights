import numpy as np
import requests


def get_average_price_for_selection(data):
    prices = data["vraagprijs"].to_list()
    return int(np.nanmean(prices))


def get_funda_avg_asking_price(location):
    return requests.get(
        f"https://marketinsights.funda.io/v1/LocalInsights/preview/{location.lower()}").json()[
        'marketInsightsMetrics']['averageAskingPrice']['value']

