import requests
from bs4 import BeautifulSoup
from typing import List, Optional
import json
from datetime import datetime
from tqdm import tqdm

from funda_insights.config import HOUSE_FEATURES, logger

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
        return {"bekeken": views,
                "opgeslagen": saves,
                "aangeboden_sinds": published_date}
    except:
        return {"aangeboden_sinds": datetime.today().strftime("%d-%m-%Y"),
                'bekeken': "n.v.t.",
                'opgeslagen': "n.v.t."}


def get_value_from_css(soup: BeautifulSoup, selector: str) -> Optional[str]:
    """Use CSS selector to find certain features."""
    result = soup.select(selector)
    if len(result) > 0:
        return result[0].text


def get_house_specifics_for_url(house_url,
                                features_set=HOUSE_FEATURES["features_combined"]):
    response = requests.get(house_url, headers=headers)
    soup = BeautifulSoup(response.text, "lxml")

    house_features = {item: retrieve_feature_value(soup, item) for item in
                      features_set}

    popularity_stats = get_house_popularity_stats(soup)
    house_basics = {'url': house_url,
                    "omschrijving": get_value_from_css(soup, ".object-description-body"),
                    "postcode": get_value_from_css(soup, ".object-header__subtitle"),
                    "buurt": get_value_from_css(soup, ".fd-display-inline--bp-m"),
                    }

    return dict(**house_basics, **house_features, **popularity_stats)


def get_funda_avg_asking_price(location):
    url = f"https://marketinsights.funda.io/v1/LocalInsights/preview/{location.lower()}"
    return requests.get(url).json()['marketInsightsMetrics']['averageAskingPrice']['value']


def build_main_query_url(area: str, availability_option: str, min_price: str,
                         max_price: str) -> str:
    main_url = f"https://funda.nl/zoeken/koop?selected_area=%22{area}%22&object_type" \
               f"=%5B%22house%22,%22apartment%22%5D"

    if availability_option == "available":
        main_url = f"{main_url}&availability=%22available%22"
    elif availability_option == "unavailable":
        main_url = f"{main_url}&availability=%22unavailable%22"
    else:
        main_url = f"{main_url}&availability=%5B%22negotiations%22,%22unavailable%22," \
                   f"%22available%22%5D"

    if min_price is not None or max_price is not None:
        min_price = "" if min_price is None else min_price
        max_price = "" if max_price is None else max_price
        main_url = f"{main_url}&price=%22{min_price}-{max_price}%22"

    return main_url


def _get_links_from_one_parent(url: str) -> List[str]:
    """Scrape all the available housing items from one Funda search page."""
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "lxml")

    script_tag = soup.find_all("script", {"type": "application/ld+json"})[0]
    json_data = json.loads(script_tag.contents[0])
    urls = [item["url"] for item in json_data["itemListElement"]]
    return list(set(urls))


def fetch_all_links(area, availability_option, page_start: int = 1, n_pages: int = 1,
                    min_price=None, max_price=None) \
        -> List[str]:
    """Find all the available links across multiple pages."""

    logger.info("Phase 1: Fetch all the available links from all pages")
    urls = []
    main_url = build_main_query_url(area, availability_option, min_price, max_price)
    page_end = n_pages

    for i in tqdm(range(page_start, page_start + n_pages)):
        try:
            item_list = _get_links_from_one_parent(
                f"{main_url}&search_result={i}"
            )
            urls += item_list
        except IndexError:
            page_end = i
            logger.info(f"The last available page is {page_end}")
            break

    urls = list(set(urls))
    logger.info(
        f"Got all the urls. {len(urls)} houses found from {page_start} to {page_end}"
    )
    return urls
