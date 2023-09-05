import time
import os
import sys

# import chromedriver_autoinstaller

from bs4 import BeautifulSoup
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from timeout_decorator import timeout, TimeoutError


from src.session import Session
from src.house import House
from src.utils import generate_scraping_metadata


@timeout(10)
def iter_wrapper(session: Session, house) -> None:
    # Create an instance of the House class to store the scraped information
    house_instance = House()

    # Create soup object from the property's html content
    house_ad_html = str(house)

    # Get the important information from the house ad on the search results page
    try:
        house_instance.scan_house_ad(house_ad_html)
    except TimeoutError:
        print("Time out scanning the house ad. Skipping to next house")
        return

    # Get the important information from the house page
    try:
        session.click_on_house(house_instance.id)
    except TimeoutError:
        print("Time out clicking on house. Skipping to next house")
        # Go back to the search results page
        session.driver.back()
        time.sleep(0.3)
        return
    except:
        print("Could not click on house element")
        session.driver.back()
        time.sleep(0.3)
        return

    # Save the html version of the new page
    property_html = session.driver.page_source

    # Get the important information from the house page
    try:
        house_instance.scan_house_page(property_html)
    except TimeoutError:
        print("Time out scanning the house page")

    # Add the house instance to the session
    session.add_house(house_instance)

    # Save the house pictures
    # session.save_house_pictures(HOUSE_PICTURES_DIR, house_instance.id)

    # Save the floorplan
    session.save_house_floorplan(FLOORPLANS_DIR, house_instance.id)

    # Go back to the search results page
    session.driver.back()
    time.sleep(0.4)


def main(postcode: str, garden_option: str, search_area: str) -> None:
    session = Session(search_area)
    session.launch_browser_with_extension(CURRENT_DIR)
    session.set_search_parameters(postcode, garden_option)
    time.sleep(0.75)

    while True:
        html = session.driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        houses = soup.find_all("div", {"class": "l-searchResult is-list"})

        for house in houses:
            try:
                iter_wrapper(session, house)
            except TimeoutError:
                print("Time out gathering data. Skipping to next house")
            # # Create an instance of the House class to store the scraped information
            # house_instance = House()

            # # Create soup object from the property's html content
            # house_ad_html = str(house)

            # # Get the important information from the house ad on the search results page
            # try:
            #     house_instance.scan_house_ad(house_ad_html)
            # except TimeoutError:
            #     print("Time out scanning the house ad. Skipping to next house")
            #     continue

            # if (
            #     garden_option.casefold() != "garden".casefold()
            #     and house_instance.id in garden_house_id_list
            # ):
            #     continue
            # else:
            #     # Get the important information from the house page
            #     try:
            #         session.click_on_house(house_instance.id)
            #     except TimeoutError:
            #         print("Time out clicking on house. Skipping to next house")
            #         # Go back to the search results page
            #         session.driver.back()
            #         time.sleep(0.3)
            #         continue
            #     except:
            #         print("Could not click on house element")

            #     # Wait a bit for the new page to load and save the html version of the new page
            #     time.sleep(0.5)
            #     property_html = session.driver.page_source

            #     # Get the important information from the house page
            #     try:
            #         house_instance.scan_house_page(property_html)
            #     except TimeoutError:
            #         print("Time out scanning the house page")

            #     # Add the house instance to the session
            #     session.add_house(house_instance)

            #     # Save the house pictures
            #     session.save_house_pictures(HOUSE_PICTURES_DIR, house_instance.id)

            #     # Save the floorplan
            #     session.save_house_floorplan(FLOORPLANS_DIR, house_instance.id)

            #     # Go back to the search results page
            #     session.driver.back()
            #     time.sleep(0.3)

        try:
            next_button_args = (
                By.CLASS_NAME,
                "pagination-button.pagination-direction.pagination-direction--next",
            )
            next_button = session.wait.until(
                EC.element_to_be_clickable(next_button_args)
            )
            session.driver.execute_script("arguments[0].click();", next_button)
            time.sleep(1)

        except:
            print(f"Finished scraping {postcode} and {garden_option}")
            break

    session.generate_and_save_dataframe(DATA_DIR, garden_option, postcode)
    session.driver.quit()
    del session


if __name__ == "__main__":
    # Check if the correct number of command-line arguments is provided
    # if len(sys.argv) != 3:
    #     print("Incorrect number of inputs. Three inputs should be provided")
    # else:
    #     # Convert command-line arguments to integers
    #     postcode_list_str = sys.argv[1]
    #     # Split the argument string into a list using the comma as a delimiter
    #     postcode_list = postcode_list_str.split(",")
    #     garden_list_str = sys.argv[2]
    #     garden_option_list = garden_list_str.split(",")
    #     search_area = "north london"

    #     # Define global variables
    #     # Get the current month and create a folder to save the data
    #     current_month = datetime.now().strftime("%B")
    #     current_year = datetime.now().year
    #     DATE_FOLDER = f"{current_month} {current_year}"

    #     CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    #     FLOORPLANS_DIR = os.path.join(CURRENT_DIR, "media/floorplans")
    #     HOUSE_PICTURES_DIR = os.path.join(CURRENT_DIR, "media/house_pictures")
    #     DATA_DIR = os.path.join(CURRENT_DIR, f"data/North London/{DATE_FOLDER}")
    #     os.makedirs(DATA_DIR, exist_ok=True)
    #     os.makedirs(FLOORPLANS_DIR, exist_ok=True)
    #     os.makedirs(HOUSE_PICTURES_DIR, exist_ok=True)

    #     for postcode in postcode_list:
    #         for garden_option in garden_option_list:
    #             # Call the main function with command-line arguments
    #             main(postcode, garden_option, search_area)

    # generate_scraping_metadata(DATA_DIR, postcode_list, garden_option_list)

    # Define global variables
    # Get the current month and create a folder to save the data
    current_month = datetime.now().strftime("%B")
    current_year = datetime.now().year
    DATE_FOLDER = f"{current_month} {current_year}"

    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    FLOORPLANS_DIR = os.path.join(CURRENT_DIR, "media/floorplans")
    HOUSE_PICTURES_DIR = os.path.join(CURRENT_DIR, "media/house_pictures")
    DATA_DIR = os.path.join(CURRENT_DIR, f"data/North London/{DATE_FOLDER}")
    os.makedirs(DATA_DIR, exist_ok=True)

    # For debugging only
    # Convert command-line arguments to integers
    postcode_list = ["N193TX", "NW53AF", "N20PE"]
    # postcode_list = ["N20PE"]
    garden_option_list = ["Garden", "NoGarden"]
    search_area = "north london"

    for postcode in postcode_list:
        for garden_option in garden_option_list:
            # Call the main function with command-line arguments
            main(postcode, garden_option, search_area)

    generate_scraping_metadata(DATA_DIR, postcode_list, garden_option_list)
