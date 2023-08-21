import time
import os
import sys
import concurrent.futures

import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from src.session import Session
from src.house import House


def main(postcode: str, garden_option: str, garden_house_id_list: str = []) -> None:
    session = Session()
    session.launch_browser_with_extension()
    session.set_search_parameters(postcode, garden_option)
    time.sleep(0.75)

    while True:
        html = session.driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        houses = soup.find_all("div", {"class": "l-searchResult is-list"})

        for house in houses:
            # Create an instance of the House class to store the scraped information
            house_instance = House()

            # Create soup object from the property's html content
            house_ad_html = str(house)

            # Get the important information from the house ad on the search results page
            house_instance.scan_house_ad(house_ad_html)

            if (
                garden_option.casefold() != "garden".casefold()
                and house_instance.id in garden_house_id_list
            ):
                continue
            else:
                try:
                    # Click on house link
                    house_link_element = session.driver.find_element(
                        By.XPATH,
                        f'//*[@id="property-{house_instance.id}"]/div/div/div[4]/div[1]/div[2]/a',
                    )
                    session.driver.execute_script(
                        "arguments[0].click();", house_link_element
                    )

                    # Wait a bit for the new page to load and save the html version of the new page
                    time.sleep(0.5)
                    property_html = session.driver.page_source

                    # Get the important information from the house page
                    house_instance.scan_house_page(property_html)

                    # Add the house instance to the session
                    session.add_house(house_instance)

                    # Save the house pictures
                    session.save_house_pictures(HOUSE_PICTURES_DIR, house_instance.id)

                    # Save the floorplan
                    session.save_house_floorplan(FLOORPLANS_DIR, house_instance.id)

                    # Go back to the search results page
                    session.driver.back()
                    time.sleep(0.3)

                except:
                    print("Could not click on property")
                    # Continue to the next iteration of the loop
                    continue

        try:
            next_button_args = (
                By.CLASS_NAME,
                "pagination-button.pagination-direction.pagination-direction--next",
            )
            next_button = session.wait.until(
                EC.element_to_be_clickable(next_button_args)
            )
            session.driver.execute_script("arguments[0].click();", next_button)
            time.sleep(0.5)

        except:
            print(f"Finished scraping {postcode} and {garden_option}")
            break
    session.generate_and_save_dataframe(DATA_DIR, garden_option, postcode)


if __name__ == "__main__":
    # Check if the correct number of command-line arguments is provided
    if len(sys.argv) != 3:
        print("Incorrect number of inputs. Three inputs should be provided")
    else:
        # Convert command-line arguments to integers
        postcode_list_str = sys.argv[1]
        # Split the argument string into a list using the comma as a delimiter
        postcode_list = postcode_list_str.split(",")
        garden_list_str = sys.argv[2]
        garden_option_list = garden_list_str.split(",")

        # Define global variables
        # Get the current month and create a folder to save the data
        current_month = datetime.now().strftime("%B")
        current_year = datetime.now().year
        DATE_FOLDER = f"{current_month} {current_year}"

        CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
        FLOORPLANS_DIR = os.path.join(CURRENT_DIR, "media/floorplans")
        HOUSE_PICTURES_DIR = os.path.join(CURRENT_DIR, "media/house_pictures")
        DATA_DIR = os.path.join(CURRENT_DIR, f"data/{DATE_FOLDER}")
        os.makedirs(DATA_DIR, exist_ok=True)

        for postcode in postcode_list:
            for garden_option in garden_option_list:
                if garden_option.casefold() != "garden".casefold():
                    garden_data = pd.read_parquet(
                        f"{DATA_DIR}/house_data_garden_{postcode}.parquet"
                    )
                    garden_data_id = garden_data["id"].tolist()
                else:
                    garden_data_id = []
                # Call the main function with command-line arguments
                main(postcode, garden_option, garden_data_id)

    # # Define global variables
    # # Get the current month and create a folder to save the data
    # current_month = datetime.now().strftime("%B")
    # current_year = datetime.now().year
    # DATE_FOLDER = f"{current_month} {current_year}"

    # CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    # FLOORPLANS_DIR = os.path.join(CURRENT_DIR, "media/floorplans")
    # HOUSE_PICTURES_DIR = os.path.join(CURRENT_DIR, "media/house_pictures")
    # DATA_DIR = os.path.join(CURRENT_DIR, f"data/{DATE_FOLDER}")
    # os.makedirs(DATA_DIR, exist_ok=True)

    # # For debugging only
    # # Convert command-line arguments to integers
    # postcode = "N20PE"
    # garden_option = "NoGarden"

    # # Call the main function with command-line arguments
    # main(postcode, garden_option)

    # for postcode in postcode_list:
    #     for garden_option in garden_option_list:
    #         if garden_option.casefold() != "garden".casefold():
    #             garden_data = pd.read_parquet(
    #                 f"{DATA_DIR}/house_data_garden_{postcode}.parquet"
    #             )
    #             garden_data_id = garden_data["id"]
    #         # Call the main function with command-line arguments
    #         main(postcode, garden_option, garden_data_id)
