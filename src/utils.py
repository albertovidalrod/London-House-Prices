import re
import pytesseract
import geocoder
import os
import json
from datetime import datetime
from PIL import Image


def floorplan_includes_garden(image_id: str = None) -> str:
    image_path = f"media/floorplans/{image_id}_floorplan.png"
    try:
        image = Image.open(image_path)

        # Perform OCR using PyTesseract
        extracted_text = pytesseract.image_to_string(image)
        extracted_text = extracted_text.lower()

        if "garden" in extracted_text:
            return "garden"
        elif "patio" in extracted_text:
            return "patio"
        elif "terrace" in extracted_text:
            return "terrace"
        elif "balcony" in extracted_text:
            return "balcony"
        else:
            return None
    except:
        return None


# Define a custom sorting key function
def custom_key(word):
    ordinal_values = {
        "ground": 0,
        "first": 1,
        "second": 2,
        "third": 3,
        "fourth": 4,
        "fifth": 5,
        "sixth": 6,
        "seventh": 7,
        "eighth": 8,
        "ninth": 9,
    }

    return ordinal_values.get(
        word, float("inf")
    )  # Use "inf" for words not in the dictionary


def map_to_ordinal(number):
    # Define your ordinal values dictionary
    ordinal_values = {
        "1": "first",
        "2": "second",
        "3": "third",
        "4": "fourth",
        "5": "fifth",
        "6": "sixth",
        "7": "seventh",
        "8": "eighth",
        "9": "ninth",
    }
    return ordinal_values.get(number, number)


def extract_other_data_from_floorplan(image_id: str = None) -> str:
    image_path = f"media/floorplans/{image_id}_floorplan.png"
    try:
        image = Image.open(image_path)

        # Perform OCR using PyTesseract
        extracted_text = pytesseract.image_to_string(image)
        extracted_text = extracted_text.lower()

        if "garden" in extracted_text:
            outdoor_space = "garden"
        elif "patio" in extracted_text:
            outdoor_space = "patio"
        elif "terrace" in extracted_text:
            outdoor_space = "terrace"
        elif "balcony" in extracted_text:
            outdoor_space = "balcony"
        else:
            outdoor_space = None

        patterns = [
            r"(\b(?:ground|first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth)\b)\s*floor",
            r"(\d+)(?:st|nd|rd|th)?\s*floor",
        ]

        # Find all matches and store the numbers
        floor_matches_set = set()

        for pattern in patterns:
            matches = re.finditer(pattern, extracted_text)
            for match in matches:
                floor_matches_set.add(match.group(1))

        floor_matches = list(floor_matches_set)

        if floor_matches:
            if all(item.isdigit() for item in floor_matches):
                floor_matches = [map_to_ordinal(item) for item in floor_matches]
            sorted_matches = sorted(floor_matches, key=custom_key)
            floor = sorted_matches[-1]
        else:
            floor = None

        return (outdoor_space, floor)
    except:
        return (None, None)


def extract_area_from_floorplan(image_id: str = None) -> float:
    image_path = f"media/floorplans/{image_id}_floorplan.png"
    try:
        image = Image.open(image_path)

        # Perform OCR using PyTesseract
        extracted_text = pytesseract.image_to_string(image)
        extracted_text = extracted_text.lower()

        patterns = [
            r"(\d+(\.\d+)?)\s*(?:ft\?|ft2?)",
            r"(\d+(\.\d+)?)\s*sq\.?\s*ft\.?",
            r"(\d+(\.\d+)?)\s*sq\.?\s*feet",
            r"(\d+(\.\d+)?)\s*sqft",
            r"(\d+(\.\d+)?)\s*saft",  # extracted text in winworths floorplans says "saft"
            r"(\d+(\.\d+)?)\s*sqt",  # extracted text in 131536022 floorplan says "sqt"
            r"(\d+(\.\d+)?)\s*sa\.?\s*ft\.?",
            r"(\d+(\.\d+)?)\s*sa\.?\s*feet",
            r"(\d+(\.\d+)?)\s*sq\.?\s*teet",
        ]

        # Find all matches and store the numbers
        numbers_before_sqft_set = set()

        for pattern in patterns:
            matches = re.finditer(pattern, extracted_text)
            for match in matches:
                numbers_before_sqft_set.add(match.group(1))

        numbers_before_sqft = list(numbers_before_sqft_set)

        if numbers_before_sqft:
            sorted_numbers = sorted(numbers_before_sqft, key=lambda x: float(x))
            if len(sorted_numbers) > 1:
                last_values = sorted_numbers[-2:]

                if float(last_values[-2]) / float(last_values[-1]) < 0.35:
                    return last_values[-1]
                else:
                    return last_values[-2]
            else:
                return sorted_numbers[-1]
        else:
            return None
    except:
        return None


def find_postcode(road: str) -> str:
    address = road + ", London"
    location = geocoder.osm(address)

    if location.ok and location.postal:
        postcode = location.postal

        if postcode.split(" ")[0].startswith("N"):
            return postcode.split(" ")[0]
        else:
            return None
    else:
        return None


def extract_area_from_dataframe(size_str: str) -> float:
    pattern = r"(\d+)\s*sq\. ft\."

    match = re.search(pattern, size_str)

    if match:
        number_before_sqft = match.group(1)
        return number_before_sqft
    else:
        return None


def generate_scraping_metadata(
    data_dir: str, postcode_list: list, garden_option_list: list
):
    current_date = datetime.now()
    current_year = current_date.strftime("%Y")
    current_month = current_date.strftime("%B")
    current_date_string = current_date.strftime("%d/%m/%Y")

    metadata_filename = f"{current_month}_{current_year}_scraping_metadata"

    files_generated = []
    for postcode in postcode_list:
        for garden_option in garden_option_list:
            # Call the main function with command-line arguments

            if garden_option.casefold() == "garden".casefold():
                garden_save_str = "garden"
            else:
                garden_save_str = "no_garden"
            files_generated.append(f"house_data_{garden_save_str}_{postcode}")

    metadata = {
        "creation_date": current_date_string,
        "postcodes": postcode_list,
        "garden_options": garden_option_list,
        "files_generated": files_generated,
    }

    # Save the metadata to a JSON file
    metadata_path = data_dir + f"/{metadata_filename}.json"
    with open(metadata_path, "w") as file:
        json.dump(metadata, file, indent=4)
