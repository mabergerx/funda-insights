from datetime import datetime
import time
import pandas as pd
from random import random
from tqdm import tqdm
import argparse
import glob
import os
from typing import List

from funda_insights.preprocess import create_dataframe
from funda_insights.scrape_utils import fetch_all_links, get_house_specifics_for_url
from funda_insights.config import logger


def write_data(data,
               area: str,
               availability_option: str,
               start_index: int,
               end_index: int):
    df = pd.DataFrame(data)
    df["gebied"] = area

    logger.info("Cleaning data")
    df = create_dataframe(df)

    logger.info("Writing (temp) data to csv file")
    date = str(datetime.now().date()).replace("-", "")

    if not os.path.exists("./data"):
        os.makedirs("./data")

    df.to_csv(f"./data/funda_data_{area}_{availability_option}_{date}_{start_index}_{end_index}.csv",
              index=False,
              sep=";")


def get_most_recent_file_in_dir(area, availability_option):
    try:
        list_of_files = glob.glob(
            f"./data/url_data_{area}_{availability_option}*")
        return max(list_of_files, key=os.path.getctime)
    except ValueError:
        return None


def get_house_urls(area: str,
                   n_pages: int,
                   load_urls_from_file: bool = True,
                   availability_option: str = "all",
                   page_start: int = 1,
                   min_price: str = None,
                   max_price: str = None,
                   start_index: int = 1) -> List[str]:

    if load_urls_from_file:
        file_path = get_most_recent_file_in_dir(area, availability_option)
        if file_path:
            house_urls = list(pd.read_csv(file_path)['url'][start_index:])
            return house_urls
        else:
            logger.info(f"Urls not available for {area} and {availability_option}, "
                        f"scraping them now")

    house_urls = fetch_all_links(area=area,
                                 availability_option=availability_option,
                                 page_start=page_start,
                                 n_pages=n_pages,
                                 min_price=min_price,
                                 max_price=max_price)

    logger.info("Writing url data to csv file")
    date = str(datetime.now().date()).replace("-", "")
    df_house_urls = pd.DataFrame({'url': house_urls})
    df_house_urls.to_csv(f"./data/url_data_{area}_{availability_option}_{date}.csv",
                         index=False,
                         sep=";")

    return house_urls


def scrape_funda_for_query(area: str,
                           n_pages: int,
                           availability_option: str = "all",
                           page_start: int = 1,
                           min_price: str = None,
                           max_price: str = None,
                           start_index: int = 1,
                           load_urls_from_file: bool = False,
                           ):

    house_url_list = get_house_urls(area=area,
                                    n_pages=n_pages,
                                    load_urls_from_file=load_urls_from_file,
                                    availability_option=availability_option,
                                    page_start=page_start,
                                    min_price=min_price,
                                    max_price=max_price,
                                    start_index=start_index,
                                    )
    house_data = []

    for i, url in enumerate(tqdm(house_url_list)):
        house_data.append(get_house_specifics_for_url(url))
        time.sleep(random()*2)
        # save results for every 100 rows
        if i % 100 == 0 and i > 0:
            write_data(data=house_data,
                       area=area,
                       availability_option=availability_option,
                       start_index=start_index,
                       end_index=start_index+i)

    write_data(data=house_data,
               area=area,
               availability_option=availability_option,
               start_index=start_index,
               end_index=start_index + i
               )


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
        "--n_pages", type=int, default=250,
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
    parser.add_argument(
        "--start_index", type=int, default=1,
        help="Index of the url to start with",
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
        start_index=args.start_index,
        load_urls_from_file=True,
    )

    logger.info("End of script; scraped data")
