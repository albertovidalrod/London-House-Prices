from dataclasses import dataclass, field

from bs4 import BeautifulSoup
from timeout_decorator import timeout


@dataclass
class House:
    id: str = None
    price: str = None
    added_reduced: str = None
    address: str = None
    description: str = None
    price_change_date: list[str] = field(default_factory=list)
    price_change_value: list[str] = field(default_factory=list)
    type_house: str = None
    bathrooms: str = None
    bedrooms: str = None
    tenure: str = None
    size: str = None
    key_features: list[str] = field(default_factory=list)
    close_stations: list[str] = field(default_factory=list)
    close_stations_type: list[str] = field(default_factory=list)
    tenure_ground_rent: str = "Ask agent"
    tenure_annual_service_charge: str = "Ask agent"
    tenure_lease_length: str = "Ask agent"
    council_tax_band: str = "Ask agent"
    sold_under_offer: str = False

    @timeout(5)
    def scan_house_ad(self, house_ad_html) -> None:
        house_ad_soup = BeautifulSoup(house_ad_html, "html.parser")

        # Get house id
        self.id = house_ad_soup.find("div").get("id").split("-")[1]
        # Get house price
        self.price = house_ad_soup.find(
            "div", class_="propertyCard-priceValue"
        ).get_text()
        # Get house date when it was added to rightmove or when its price was last
        # reduced
        self.added_reduced = house_ad_soup.find(
            "span", class_="propertyCard-branchSummary-addedOrReduced"
        ).get_text()
        # Get house address
        self.address = house_ad_soup.find("address").get_text()
        # Get house description
        self.description = house_ad_soup.find("span", itemprop="description").get_text()

        # Find the element with the specified class and data-test attribute
        sold_under_offer_element = house_ad_soup.find(
            "span",
            {
                "class": "ksc_lozenge berry propertyCard-tagTitle propertyCard-tagTitle--show",
                "data-test": "property-status",
            },
        )

        # Check if the element exists
        if sold_under_offer_element:
            self.sold_under_offer = True
        else:
            self.sold_under_offer = False

    @timeout(10)
    def scan_house_price_change(self, house_ad_html) -> None:
        house_ad_soup = BeautifulSoup(house_ad_html, "html.parser")
        # Get house id
        self.id = house_ad_soup.find("div").get("id").split("-")[1]
        # Get house price
        self.price = house_ad_soup.find(
            "div", class_="propertyCard-priceValue"
        ).get_text()
        # Get the dates when the price has changed. This information is provided by a
        # a Chrome extension
        self.price_change_date = [
            element.get_text()
            for element in house_ad_soup.find_all("td", class_="pl-date-column")
        ]
        # Get the price change value, if any. This information is provided by a
        # a Chrome extension
        self.price_change_value = [
            element.get_text()
            for element in house_ad_soup.find_all("td", class_="pl-price-column")
        ]

    @timeout(5)
    def scan_house_page(self, house_page_html):
        house_soup = BeautifulSoup(house_page_html, "html.parser")

        # Get the type of house, number of bedrooms, number of bathrooms, size of the
        # house (if the information is available) and the tenure type
        house_details = [
            element.get_text()
            for element in house_soup.find_all("dl", class_="_3gIoc-NFXILAOZEaEjJi1n")
        ]
        for item in house_details:
            if "PROPERTY TYPE" in item:
                self.type_house = item.split("PROPERTY TYPE")[-1]
            elif "BEDROOMS" in item:
                self.bedrooms = item.split("×")[-1]
            elif "BATHROOMS" in item:
                self.bathrooms = item.split("×")[-1]
            elif "SIZE" in item:
                self.size = item.split("SIZE")[-1]
            elif "TENURE" in item:
                self.tenure = item.split("RE")[-1]

        # Get the key features of the house
        key_features = [
            element.get_text()
            for element in house_soup.find_all("li", class_="lIhZ24u1NHMa5Y6gDH90A")
        ]
        if key_features:
            self.key_features = key_features

        # Get information about the closest stations
        self.close_stations = [
            element.get_text().split("Station")
            for element in house_soup.find_all("div", class_="mlEuHXZpfrrzJtwlRmwBe")
        ]
        self.close_stations_type = [
            element.find("use")["xlink:href"].split("#")[1]
            for element in house_soup.find_all("div", class_="_33FcKz0Izh9IdGj_vDDgmK")
        ]

        # Get the tenure details: ground rent, annual service charge and lease length
        house_tenure_details_element = house_soup.find_all(
            "p", class_="_215KNIlPCd_x8o2is5Adgn"
        )
        if house_tenure_details_element:
            house_tenure_details = [
                element.get_text() for element in house_tenure_details_element
            ]
            if house_tenure_details:
                self.tenure_ground_rent = house_tenure_details[0]
                self.tenure_annual_service_charge = house_tenure_details[1]
                self.tenure_lease_length = house_tenure_details[2]

        # Get the council tax band
        council_tax_element = house_soup.find("p", class_="_1VOsciKYew6xj3RWxMv_6J")
        if council_tax_element:
            self.council_tax_band = council_tax_element.get_text()
