import time
import requests
import os
from bs4 import BeautifulSoup
from requests_html import HTMLSession
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.select import Select

from src.session import Session
from src.house import House

import pandas as pd

current_dir = os.path.dirname(os.path.abspath(__file__))
floorplans_dir = os.path.join(current_dir, "media/floorplans")
house_pictures_dir = os.path.join(current_dir, "media/house_pictures")

session = Session()
session.launch_browser_with_extension()
session.set_search_parameters()
# session.driver.implicitly_wait(10)
time.sleep(1)

html = session.driver.page_source
soup = BeautifulSoup(html, "html.parser")
houses = soup.find_all("div", {"class": "l-searchResult is-list"})


for house in houses:
    # Create soup object from the property's html content
    house_ad_html = str(house)
    house_ad_soup = BeautifulSoup(house_ad_html, "html.parser")

    # Get property's id, price and address
    property_id = house_ad_soup.find("div").get("id").split("-")[1]
    property_price = house_ad_soup.find(
        "div", class_="propertyCard-priceValue"
    ).get_text()
    added_reduced = house_ad_soup.find(
        "span", class_="propertyCard-branchSummary-addedOrReduced"
    ).get_text()
    address = house_ad_soup.find("address").get_text()
    price_change_date = [
        element.get_text()
        for element in house_ad_soup.find_all("td", class_="pl-date-column")
    ]

    price_change_value = [
        element.get_text()
        for element in house_ad_soup.find_all("td", class_="pl-price-column")
    ]
    description = house_ad_soup.find("span", itemprop="description").get_text()

    # Do the same using an instance of the House class and one of the functions
    house_instance = House()
    house_instance.scan_house_ad(house_ad_html)

    # Click on property link
    house_link_element = session.driver.find_element(
        By.XPATH, f'//*[@id="property-{property_id}"]/div/div/div[4]/div[1]/div[2]/a'
    )
    session.driver.execute_script("arguments[0].click();", house_link_element)

    time.sleep(0.25)
    property_html = session.driver.page_source
    property_soup = BeautifulSoup(property_html, "html.parser")

    property_details = [
        element.get_text()
        for element in property_soup.find_all("dl", class_="_3gIoc-NFXILAOZEaEjJi1n")
    ]
    property_type = property_details[0].split("PROPERTY TYPE")[-1]
    property_bedrooms = property_details[1].split("×")[-1]
    property_bathrooms = property_details[2].split("×")[-1]
    if "SIZE" in property_details[3]:
        property_details[3].split("SIZE")
        property_area = (
            property_details[3].split("SIZE")[-1].split("(")[-1].split(" ")[0]
        )
        property_tenure = property_details[4].split("RE")[-1]
    else:
        property_area = float("NaN")
        property_tenure = property_details[3].split("RE")[-1]

    property_key_features = [
        element.get_text()
        for element in property_soup.find_all("li", class_="lIhZ24u1NHMa5Y6gDH90A")
    ]

    property_stations = [
        element.get_text().split("Station")
        for element in property_soup.find_all("div", class_="mlEuHXZpfrrzJtwlRmwBe")
    ]

    property_tenure_details = [
        element.get_text()
        for element in property_soup.find_all("p", class_="_215KNIlPCd_x8o2is5Adgn")
    ]
    property_council_tax_band = property_soup.find(
        "p", class_="_1VOsciKYew6xj3RWxMv_6J"
    ).get_text()

    # Do the same using an instance of the House class and one of the functions
    house_instance.scan_house_page(property_html)
    session.add_house(house_instance)

    # # Access the property images
    # house_pictures_element = session.driver.find_element(
    #     By.CSS_SELECTOR, "a._345hU7-W8dOLOomnuuoDVx"
    # )
    # house_pictures_element.click()
    # time.sleep(0.5)

    # # What works so far:
    # parent_element = session.driver.find_elements(
    #     By.XPATH, """//*[@id="root"]/div/div[2]/div[2]/div"""
    # )
    # house_larger_pictures_element = parent_element[0].find_elements(
    #     By.CLASS_NAME, "_2BEYToQ5mjPuC5vD8izBf0._3A5jUK72scDMjjyquC9HAc"
    # )

    # for i, picture_element in enumerate(house_larger_pictures_element[:-2]):
    #     picture_link_element = picture_element.find_element(
    #         By.CSS_SELECTOR, "div._2BEYToQ5mjPuC5vD8izBf0._3A5jUK72scDMjjyquC9HAc img"
    #     )
    #     # Extract the link (src) attribute value
    #     picture_url = picture_link_element.get_attribute("src")

    #     # Download the new image using requests
    #     response = requests.get(picture_url)

    #     # Create directory to save house pictures
    #     house_dir = f"{house_pictures_dir}/{house_instance.id}"
    #     os.makedirs(f"{house_dir}", exist_ok=True)

    #     # Save the new image to a file
    #     with open(f"{house_dir}/{house_instance.id}_picture_{i}.png", "wb") as f:
    #         f.write(response.content)

    # # Go back to the property details page
    # session.driver.back()
    session.save_house_pictures(house_pictures_dir, house_instance.id)

    # Save the floorplan
    session.save_house_floorplan(floorplans_dir, house_instance.id)

    # Go back to the search results page
    session.driver.back()
    time.sleep(0.25)


# Find next button
next_button_args = (
    By.XPATH,
    """//*[@id="searchFilters"]/div[2]/div[2]/div/div[3]/button""",
)

# while True:
#     try:
#         next_button = driver.find_element(*next_button_args)
#         wait.until(EC.element_to_be_clickable(next_button_args))
#         driver.execute_script("arguments[0].click();", next_button)
#     except:
#         break

print("we're testing")
