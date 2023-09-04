import requests
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.select import Select
from timeout_decorator import timeout

import pandas as pd

from src.house import House


class Session:
    def __init__(self, mode: str) -> None:
        # Define the url from which the data will be scraped
        self.url = "https://www.rightmove.co.uk/property-for-sale.html"

        # Get url information
        self.house_list = []

        # Load config files depending on mode

    def launch_browser_with_extension(self, current_dir: str) -> None:
        self.driver_service = Service(executable_path="/opt/homebrew/bin/chromedriver")
        self.driver_options = webdriver.ChromeOptions()
        # Define path to the extension
        extension_path = os.path.join(
            current_dir,
            "../../../../../Application Support/Google/Chrome/Default/Extensions/jccihedpilhidcbkconacnalppdeecno/1.6.1_0",
        )
        # Add the extension and launch Chrome
        self.driver_options.add_argument("--load-extension=" + extension_path)
        self.driver = webdriver.Chrome(
            service=self.driver_service,
            options=self.driver_options,
        )
        self.driver.get(self.url)

        # Define the wait element to pause the script until an element is found or ready to
        # be clicked
        self.wait = WebDriverWait(self.driver, 10)

        # Find cookie button and accept cookies
        cookie_button_args = (By.ID, "onetrust-accept-btn-handler")
        self.wait.until(EC.presence_of_element_located(cookie_button_args))
        cookie_button = self.driver.find_element(*cookie_button_args)
        self.wait.until(EC.element_to_be_clickable(cookie_button_args))
        self.driver.execute_script("arguments[0].click();", cookie_button)

    def launch_browser_headless_mode(self) -> None:
        self.driver_service = Service()
        self.driver_options = webdriver.ChromeOptions()
        self.driver_options.add_argument("--headless")
        self.driver = webdriver.Chrome(
            service=self.driver_service,
            options=self.driver_options,
        )
        self.driver.get(self.url)

        # Define the wait element to pause the script until an element is found or ready to
        # be clicked
        self.wait = WebDriverWait(self.driver, 10)

        # Find cookie button and accept cookies
        cookie_button_args = (By.ID, "onetrust-accept-btn-handler")
        self.wait.until(EC.presence_of_element_located(cookie_button_args))
        cookie_button = self.driver.find_element(*cookie_button_args)
        self.wait.until(EC.element_to_be_clickable(cookie_button_args))
        self.driver.execute_script("arguments[0].click();", cookie_button)

    def set_search_parameters(self, postcode: str, garden_option: str) -> None:
        # Find postcode field and search button
        # postcode_element = self.driver.find_element(by=By.ID, value="searchLocation")
        # search_button = self.driver.find_element(by=By.ID, value="search")
        postcode_element = self.driver.find_element(
            By.CLASS_NAME, value="ksc_typeAheadInputField"
        )
        search_button = self.driver.find_element(By.CLASS_NAME, value="ksc_button")

        # Fill the postcode
        postcode_element.send_keys(postcode)
        # self.wait until the update button is clickable and then click it
        self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "ksc_button")))
        self.driver.execute_script("arguments[0].click();", search_button)

        # Select property features
        # Search area radius
        search_radius = "1.0"
        search_radius_element = self.wait.until(
            EC.element_to_be_clickable((By.ID, "radius"))
        )
        select_search_radius = Select(search_radius_element)
        select_search_radius.select_by_value(search_radius)

        # Min price
        min_price = "350000"
        min_price_element = self.wait.until(
            EC.element_to_be_clickable((By.ID, "minPrice"))
        )
        select_min_price = Select(min_price_element)
        select_min_price.select_by_value(min_price)

        # Max price
        max_price = "550000"
        max_price_element = self.wait.until(
            EC.element_to_be_clickable((By.ID, "maxPrice"))
        )
        select_max_price = Select(max_price_element)
        select_max_price.select_by_value(max_price)

        # Min bedrooms
        min_bedrooms = "1"
        min_bedrooms_element = self.wait.until(
            EC.element_to_be_clickable((By.ID, "minBedrooms"))
        )
        select_min_bedrooms = Select(min_bedrooms_element)
        select_min_bedrooms.select_by_value(min_bedrooms)

        # Max bedrooms
        max_bedrooms = "3"
        max_bedrooms_element = self.wait.until(
            EC.element_to_be_clickable((By.ID, "maxBedrooms"))
        )
        select_max_bedrooms = Select(max_bedrooms_element)
        select_max_bedrooms.select_by_value(max_bedrooms)

        # self.wait until the find properties button is clickable and then click it
        find_properties_button_args = (By.ID, "submit")
        search_button = self.driver.find_element(*find_properties_button_args)
        self.wait.until(EC.element_to_be_clickable(find_properties_button_args))
        self.driver.execute_script("arguments[0].click();", search_button)

        # Expand the filter field
        filters_button_args = (By.XPATH, """//*[@id="filtersBar"]/div/button[2]""")
        filters_button = self.driver.find_element(*filters_button_args)
        self.wait.until(EC.element_to_be_clickable(filters_button_args))
        self.driver.execute_script("arguments[0].click();", filters_button)

        # Select Garden as one of the must haves
        if garden_option.casefold() == "garden".casefold():
            garden_homes_args = (
                By.XPATH,
                """//*[@id="mustHaveDontShow"]/div/div[1]/div[1]/div/div[2]/div[1]""",
            )
            garden_homes_option = self.driver.find_element(*garden_homes_args)
            self.wait.until(EC.element_to_be_clickable(garden_homes_args))
            self.driver.execute_script("arguments[0].click();", garden_homes_option)

        # Remove new homes
        new_homes_args = (
            By.XPATH,
            """//*[@id="mustHaveDontShow"]/div/div[1]/div[2]/div/div[2]/div[1]""",
        )
        new_home_option = self.driver.find_element(*new_homes_args)
        self.wait.until(EC.element_to_be_clickable(new_homes_args))
        self.driver.execute_script("arguments[0].click();", new_home_option)

        # Remove retirement homes
        retirement_homes_args = (
            By.XPATH,
            """//*[@id="mustHaveDontShow"]/div/div[1]/div[2]/div/div[2]/div[2]""",
        )
        retirement_home_option = self.driver.find_element(*retirement_homes_args)
        self.wait.until(EC.element_to_be_clickable(retirement_homes_args))
        self.driver.execute_script("arguments[0].click();", retirement_home_option)

        # Remove buying scheme homes
        buy_scheme_args = (
            By.XPATH,
            """//*[@id="mustHaveDontShow"]/div/div[1]/div[2]/div/div[2]/div[3]""",
        )
        buy_scheme_option = self.driver.find_element(*buy_scheme_args)
        self.wait.until(EC.element_to_be_clickable(buy_scheme_args))
        self.driver.execute_script("arguments[0].click();", buy_scheme_option)

        # Add reserved houses
        checkbox_element = self.driver.find_element(
            By.CSS_SELECTOR, 'label.includeStatus-checkbox[for="filters-sold-stc"]'
        )

        # Click the checkbox to select it
        checkbox_element.click()

        # Close filter menu
        close_filter_args = (
            By.XPATH,
            """//*[@id="searchFilters"]/div[2]/div[2]/div/div[3]/button""",
        )
        close_filter_button = self.driver.find_element(*close_filter_args)
        self.wait.until(EC.element_to_be_clickable(close_filter_args))
        self.driver.execute_script("arguments[0].click();", close_filter_button)

    @timeout(10)
    def click_on_house(self, house_id: str) -> None:
        current_url = self.driver.current_url
        try:
            house_url = (
                f"https://www.rightmove.co.uk/properties/{house_id}#/?channel=RES_BUY"
            )
            self.driver.get(house_url)
            time.sleep(0.5)
        except:
            print("Time out trying to click on the house link")
            self.driver.get(current_url)
            time.sleep(0.5)

    def save_house_floorplan(self, floorplans_dir, house_id):
        try:
            floorplan_url = f"https://www.rightmove.co.uk/properties/{house_id}#/floorplan?channel=RES_BUY"
            # Click on the floorplan and download it
            self.driver.get(floorplan_url)
            time.sleep(0.5)

            # Locate the new img element on the new page
            floorplan_larger_element = self.driver.find_element(
                By.CSS_SELECTOR, ".react-transform-component img"
            )

            # Get the src attribute value (new image URL)
            floorplan_url = floorplan_larger_element.get_attribute("src")

            # Download the new image using requests
            response = requests.get(floorplan_url)

            # Save the new image to a file
            with open(f"{floorplans_dir}/{house_id}_floorplan.png", "wb") as f:
                f.write(response.content)

            # Go back to the property details page
            self.driver.back()
        except:
            print("Could not find the floorplan")
            return

    def save_house_pictures(self, house_pictures_dir: str, house_id: str) -> None:
        try:
            # Click on the house pictures
            pictures_url = f"https://www.rightmove.co.uk/properties/{house_id}#/media?channel=RES_BUY"
            self.driver.get(pictures_url)
            time.sleep(0.3)

            # Find the element that contains all the pictures
            parent_element = self.driver.find_elements(
                By.XPATH, """//*[@id="root"]/div/div[2]/div[2]/div"""
            )
            # Extract the pictures from the container html element
            house_larger_pictures_element = parent_element[0].find_elements(
                By.CLASS_NAME, "_2BEYToQ5mjPuC5vD8izBf0._3A5jUK72scDMjjyquC9HAc"
            )

            # Create directory to save house pictures
            house_dir = f"{house_pictures_dir}/{house_id}"
            os.makedirs(f"{house_dir}", exist_ok=True)

            # Iterate over the picture elements and save them
            for i, picture_element in enumerate(house_larger_pictures_element[:-2]):
                # Find the element that contains the url to the picture
                picture_link_element = picture_element.find_element(
                    By.CSS_SELECTOR,
                    "div._2BEYToQ5mjPuC5vD8izBf0._3A5jUK72scDMjjyquC9HAc img",
                )
                # Extract the url (src) attribute value
                picture_url = picture_link_element.get_attribute("src")

                # Download the new image using requests
                response = requests.get(picture_url)

                # Save the new image to a file
                with open(f"{house_dir}/{house_id}_picture_{i}.png", "wb") as f:
                    f.write(response.content)

            # Go back to the property details page
            self.driver.back()
            time.sleep(0.3)
        except:
            print("Could not find the pictures of the house")
            return

    def add_house(self, house: House) -> None:
        if isinstance(house, House):
            self.house_list.append(house)
        else:
            raise ValueError("Only instances of House can be added to the session")

    def generate_and_save_dataframe(
        self, data_dir: str, garden_option: str, postcode: str
    ) -> None:
        data = {
            "id": [house.id for house in self.house_list],
            "price": [house.price for house in self.house_list],
            "added_reduced": [house.added_reduced for house in self.house_list],
            "address": [house.address for house in self.house_list],
            "description": [house.description for house in self.house_list],
            "price_change_date": [house.price_change_date for house in self.house_list],
            "price_change_value": [
                house.price_change_value for house in self.house_list
            ],
            "type_house": [house.type_house for house in self.house_list],
            "bathrooms": [house.bathrooms for house in self.house_list],
            "bedrooms": [house.bedrooms for house in self.house_list],
            "size": [house.size for house in self.house_list],
            "tenure": [house.tenure for house in self.house_list],
            "key_features": [house.key_features for house in self.house_list],
            "close_stations": [house.close_stations for house in self.house_list],
            "close_stations_type": [
                house.close_stations_type for house in self.house_list
            ],
            "tenure_ground_rent": [
                house.tenure_ground_rent for house in self.house_list
            ],
            "tenure_annual_service_charge": [
                house.tenure_annual_service_charge for house in self.house_list
            ],
            "tenure_lease_length": [
                house.tenure_lease_length for house in self.house_list
            ],
            "council_tax_band": [house.council_tax_band for house in self.house_list],
        }
        if garden_option.casefold() == "garden".casefold():
            garden_save_str = "garden"
        else:
            garden_save_str = "no_garden"
        self.house_dataframe = pd.DataFrame(data)
        self.house_dataframe.to_csv(
            f"{data_dir}/house_data_{garden_save_str}_{postcode}.csv"
        )
        self.house_dataframe.to_parquet(
            f"{data_dir}/house_data_{garden_save_str}_{postcode}.parquet"
        )
