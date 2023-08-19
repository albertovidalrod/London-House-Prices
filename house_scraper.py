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


def main(postcode, garden_option):
    # Get the current month and create a folder to save the data
    current_month = datetime.now().strftime("%B")
    current_year = datetime.now().year
    DATE_FOLDER = f"{current_month} {current_year}"

    current_dir = os.path.dirname(os.path.abspath(__file__))
    floorplans_dir = os.path.join(current_dir, "media/floorplans")
    house_pictures_dir = os.path.join(current_dir, "media/house_pictures")
    data_dir = os.path.join(current_dir, f"data/{DATE_FOLDER}")
    os.makedirs(data_dir, exist_ok=True)

    session = Session()
    session.launch_browser_with_extension()
    session.set_search_parameters(postcode, garden_option)
    # session.driver.implicitly_wait(10)
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
                try:
                    house_instance.scan_house_page(property_html)
                except:
                    print("Time-out when scanning house page")
                    pass

                # Add the house instance to the session
                session.add_house(house_instance)

                # Save the house pictures
                session.save_house_pictures(house_pictures_dir, house_instance.id)

                # Save the floorplan
                session.save_house_floorplan(floorplans_dir, house_instance.id)

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
            print("Finished scraping")
            break
    session.generate_and_save_dataframe(data_dir, garden_option, postcode)

    print("Data saved")


if __name__ == "__main__":
    # Check if the correct number of command-line arguments is provided
    # if len(sys.argv) != 3:
    #     print("Incorrect number of inputs. Three inputs should be provided")
    # else:
    #     # Convert command-line arguments to integers
    #     postcode_list_str = sys.argv[1]
    #     # Split the argument string into a list using the comma as a delimiter
    #     postcode_list = postcode_list_str.split(",")
    #     garden_option = sys.argv[2]

    #     for postcode in postcode_list:
    #         # Call the main function with command-line arguments
    #         main(postcode, garden_option)

    # For debugging only
    # Convert command-line arguments to integers
    postcode = "NW53AF"
    garden_option = "NoGarden"

    # Call the main function with command-line arguments
    main(postcode, garden_option)
