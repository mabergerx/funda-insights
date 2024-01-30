from datetime import datetime
import time
import pandas as pd
from random import random
from tqdm import tqdm
import argparse
import os

from funda_insights.preprocess import preprocess_df
from funda_insights.scrape_utils import fetch_all_links, get_house_specifics_for_url
from funda_insights.config import logger


def scrape_funda_for_query(area: str,
                           n_pages: int,
                           availability_option: str = "all",
                           page_start: int = 1,
                           min_price: str = None,
                           max_price: str = None):

    house_urls = fetch_all_links(area=area,
                                 availability_option=availability_option,
                                 page_start=page_start,
                                 n_pages=n_pages,
                                 min_price=min_price,
                                 max_price=max_price)

    house_data = []
    for url in tqdm(house_urls):
        house_data.append(get_house_specifics_for_url(url))
        time.sleep(random()*3)

    df = pd.DataFrame(house_data)
    df["gebied"] = area

    logger.info("Cleaning data")
    df = preprocess_df(df)

    logger.info("Writing data to csv file")
    date = str(datetime.now().date()).replace("-", "")

    if not os.path.exists("./data"):
        os.makedirs("./data")

    df.to_csv(f"./data/funda_data_{area}_{availability_option}_{date}.csv",
              index=False,
              sep=";")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--area", type=str, default="gouda",
        help="Specify which area you are looking for",
    )
    parser.add_argument(
        "--availability", type=str, default="all",
        help="Indicate whether you want to use historical data or not",
    )
    parser.add_argument(
        "--page_start", type=int, default=1,
        help="Specify which page to start scraping",
    )
    parser.add_argument(
        "--n_pages", type=int, default=1,
        help="Specify how many pages to scrape",
    )
    parser.add_argument(
        "--min_price", type=int, default=None,
        help="Specify the min price",
    )
    parser.add_argument(
        "--max_price", type=int, default=None,
        help="Specify the max price",
    )

    args = parser.parse_args()

    logger.info("Starting script")

    scrape_funda_for_query(
        area=args.area,
        availability_option=args.availability,
        page_start=args.page_start,
        n_pages=args.n_pages,
        min_price=args.min_price,
        max_price=args.max_price,
    )

    logger.info("End of script; scraped data")
