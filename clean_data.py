import os
import geocoder
import re

import dask
import dask.multiprocessing
import dask.dataframe as dd
from dask import delayed

import pandas as pd
import numpy as np

from src.utils import (
    extract_area_from_floorplan,
)


@delayed
def dask_extract_area_from_floorplan(id: str, search_area: str):
    return extract_area_from_floorplan(id, search_area)


search_area = "area interest"
floorplans = os.listdir(f"media/floorplans/{search_area}")
floorplans = [file for file in floorplans if file != ".DS_Store"]

floorplan_id = [file.split("_")[0] for file in floorplans]

# Create a list of Dask delayed objects
delayed_results = [
    dask_extract_area_from_floorplan(id, search_area) for id in floorplan_id
]

# Compute the results to trigger the computation
floor_size = list(dask.compute(*delayed_results))

# Create dataframe and save it
data = {"id": floorplan_id, "size": floor_size}
size_df = pd.DataFrame(data)
size_df.to_csv(f"data/{search_area}/all_floor_size.csv")
size_df.to_parquet(f"data/{search_area}/all_floor_size.parquet")

# Delete floorplans
for file in floorplans:
    os.remove(f"media/floorplans/{search_area}/{file}")
os.rmdir(f"media/floorplans/{search_area}")
