from funda_scraper import FundaScraper
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import pandas as pd
from random import random
from tqdm import tqdm
import argparse
from funda_scraper.utils import logger

from config import HOUSE_FEATURES


headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}


def retrieve_feature_value(soup, feature_name):
    try:
        # Find the <dt> element with the text 'Ligging tuin'
        dt_element = soup.find('dt', string=feature_name)

        # Find the next <dd> element which is the sibling of <dt>
        dd_element = dt_element.find_next_sibling('dd')

        # Extract and print the text from the <dd> element
        feature_text = dd_element.get_text(strip=True)

    except AttributeError as e:
        feature_text = "n.v.t."

    return feature_text


def get_house_popularity_stats(soup):
    try:
        object_statistics_html = soup.select(".object-statistics")[0]
        house_global_id = object_statistics_html.find('app-object-insights-card')[
            "global-id"]
        published_date = object_statistics_html.find('app-object-insights-card')[
            "published-date"]
        insights = requests.get(
            f"https://marketinsights.funda.io/v1/objectinsights/{house_global_id}").json()
        views = insights["nrOfViews"]
        saves = insights["nrOfSaves"]
        return {"views": views, "saves": saves, "published_at": published_date}
    except:
        return {"published_at": datetime.today().strftime("%d-%m-%Y"),
                'views': "n.v.t.", 'saves': "n.v.t."}


def get_house_specifics_for_url(house_url, features_set=HOUSE_FEATURES["features_combined"]):
    response = requests.get(house_url, headers=headers)
    soup = BeautifulSoup(response.text, "lxml")

    house_features = {item: retrieve_feature_value(soup, item) for item in
                      features_set}

    popularity_stats = get_house_popularity_stats(soup)

    return dict({'url': house_url}, **house_features, **popularity_stats)


def get_funda_avg_asking_price(location):
    url = f"https://marketinsights.funda.io/v1/LocalInsights/preview/{location.lower()}"
    return requests.get(url).json()['marketInsightsMetrics']['averageAskingPrice']['value']


def scrape_funda_for_query(area, n_pages, find_past=False, page_start=1):
    scraper = FundaScraper(area=area,
                           want_to="buy",
                           find_past=find_past,
                           page_start=page_start,
                           n_pages=n_pages
                        )

    scraper.fetch_all_links(page_start=page_start, n_pages=n_pages)
    house_data = []
    for url in tqdm(scraper.links):
        house_data.append(get_house_specifics_for_url(url))
        time.sleep(random()*3)

    df = pd.DataFrame(house_data)

    logger.info("Writing data to csv file")
    date = str(datetime.now().date()).replace("-", "")
    status = "unavailable" if find_past else "available"
    df.to_csv(f"./data/funda_data_{area}_{status}_{date}.csv", index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--area",
        type=str,
        help="Specify which area you are looking for",
        default="amsterdam",
    )
    parser.add_argument(
        "--find_past",
        type=bool,
        help="Indicate whether you want to use historical data or not",
        default=False,
    )
    parser.add_argument(
        "--page_start", type=int, help="Specify which page to start scraping", default=1
    )
    parser.add_argument(
        "--n_pages", type=int, help="Specify how many pages to scrape", default=1
    )
    parser.add_argument(
        "--min_price", type=int, help="Specify the min price", default=None
    )
    parser.add_argument(
        "--max_price", type=int, help="Specify the max price", default=None
    )

    args = parser.parse_args()

    logger.info("Starting script")

    scrape_funda_for_query(
        area=args.area,
        n_pages=args.n_pages,
        page_start=args.page_start,
    )

    logger.info("End of script; scraped data")
