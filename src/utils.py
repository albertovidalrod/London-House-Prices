import re
import pytesseract
from PIL import Image


def extract_data_from_floorplan(image_path: str) -> list(float):
    image_path = "floorplans/129675866_floorplan.png"

    # Open the image file
    image = Image.open(image_path)

    # Perform OCR using PyTesseract
    extracted_text = pytesseract.image_to_string(image)

    # Define a regular expression pattern to match numbers along with any symbols
    # pattern = r"\d+[^\w\s]*"
    pattern = r'\d+(?:[\'°"]\d*)?(?:\.\d+)?'

    # Use regex to find all numbers in the text
    numbers_and_symbols = re.findall(pattern, extracted_text)

    # Extract the numbers only
    numbers = [
        float(num)
        for num in numbers_and_symbols
        if re.match(r"^\d+(\.\d+)?$", num) or num.isnumeric()
    ]
    sorted_numbers = sorted(numbers)
    last_values = sorted_numbers[-2:]

    return last_values
