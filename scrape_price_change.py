import argparse
import os
import time
from datetime import datetime

import yaml
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from timeout_decorator import TimeoutError, timeout

from src.house import House
from src.session import Session
from src.utils import generate_price_change_scraping_metadata

# import chromedriver_autoinstaller


@timeout(10)
def house_scraping_wrapper(session: Session, house: House) -> None:
    # Create an instance of the House class to store the scraped information
    house_instance = House()

    # Create soup object from the property's html content
    house_ad_html = str(house)

    # Get the important information from the house ad on the search results page
    try:
        house_instance.scan_house_price_change(house_ad_html)
    except TimeoutError:
        print("Time out scanning the house price change. Skipping to next house")
        return

    # Add the house instance to the session
    session.add_house(house_instance)

    # Go back to the search results page
    # session.driver.back()
    time.sleep(0.2)


def main(
    postcode: str, garden_option: str, search_area: str, search_config: dict
) -> None:
    session = Session(search_config)
    session.launch_browser_with_extension(CURRENT_DIR)
    session.set_search_parameters(postcode, garden_option, search_area)
    time.sleep(0.75)

    while True:
        html = session.driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        houses = soup.find_all("div", {"class": "l-searchResult is-list"})

        for house in houses:
            try:
                house_scraping_wrapper(session, house)
            except TimeoutError:
                print("Time out gathering data. Skipping to next house")

        try:
            next_button_args = (
                By.CLASS_NAME,
                "pagination-button.pagination-direction.pagination-direction--next",
            )
            next_button = session.wait.until(
                EC.element_to_be_clickable(next_button_args)
            )
            session.driver.execute_script("arguments[0].click();", next_button)
            time.sleep(0.75)

        except:
            print(f"Finished scraping {postcode} and {garden_option}")
            break

    session.save_price_change_dataframe(DATA_DIR, garden_option, postcode, search_area)
    session.driver.quit()
    del session


if __name__ == "__main__":
    # Parse the arguments and assign them to variables
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-s",
        "--search_area",
        type=str,
        choices=["all postcodes", "area interest"],
        help="Specify the search area. Only 'all postcodes' and 'area interest' are available",
    )
    parser.add_argument(
        "-g", "--garden_list", type=str, help="Specify the garden options"
    )
    args = parser.parse_args()
    search_area = args.search_area
    garden_list = args.garden_list
    garden_option_list = garden_list.split(",")

    # Define global variables
    # Get the current month and create a folder to save the data
    DATE_FOLDER = datetime.now().strftime("%B %Y")
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(CURRENT_DIR, f"data/{search_area}/{DATE_FOLDER}")
    os.makedirs(DATA_DIR, exist_ok=True)

    # Load config file for the house search parameters depending on the search area
    if search_area.casefold() == "area interest".casefold():
        config_file_path = os.path.join(CURRENT_DIR, "config/config_area_interest.yml")
    elif search_area.casefold() == "all postcodes".casefold():
        config_file_path = os.path.join(CURRENT_DIR, "config/config_all_postcodes.yml")
    else:
        raise ValueError(
            "Invalid search area. Search area must be 'area interest' or 'all postcodes'."
        )

    # Load the configuration from the YAML file
    with open(config_file_path, "r") as config_file:
        search_config = yaml.safe_load(config_file)

    postcode_list = [search_config["postcodes"][datetime.now().day]]

    for postcode in postcode_list:
        for garden_option in garden_option_list:
            # Call the main function with command-line arguments
            main(postcode, garden_option, search_area, search_config)

generate_price_change_scraping_metadata(
    DATA_DIR, postcode_list, garden_option_list, search_area, search_config
)
