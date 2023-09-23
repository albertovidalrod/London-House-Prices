import argparse
import os
import re
import sys

import dask
import dask.dataframe as dd
import dask.multiprocessing
import geocoder
import numpy as np
import pandas as pd
from dask import delayed

from utils import extract_area_from_floorplan


@delayed
def dask_extract_area_from_floorplan(id: str, floorplans_dir: str):
    return extract_area_from_floorplan(id, floorplans_dir)


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
    args = parser.parse_args()
    search_area = args.search_area

    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    FLOORPLANS_DIR = os.path.join(CURRENT_DIR, f"../media/floorplans/{search_area}")
    DATA_DIR = os.path.join(CURRENT_DIR, f"../data/{search_area}")

    floorplans = os.listdir(FLOORPLANS_DIR)
    floorplans = [file for file in floorplans if file != ".DS_Store"]
    floorplan_id = [file.split("_")[0] for file in floorplans]

    # Create a list of Dask delayed objects
    delayed_results = [
        dask_extract_area_from_floorplan(id, FLOORPLANS_DIR) for id in floorplan_id
    ]

    # Compute the results to trigger the computation
    floor_size = list(dask.compute(*delayed_results))

    # Create dataframe and save it
    data = {"id": floorplan_id, "size": floor_size}
    if os.path.exists(f"{DATA_DIR}/all_floor_size.parquet"):
        size_df = pd.read_parquet(f"{DATA_DIR}/all_floor_size.parquet")
        data_df = pd.DataFrame(data)
        all_df = pd.concat([size_df, data_df])
        all_df = all_df.drop_duplicates(subset=["id"], keep="last")
        all_df.reset_index(drop=True, inplace=True)
    else:
        all_df = pd.DataFrame(data)

    all_df.to_csv(f"{DATA_DIR}/all_floor_size.csv", index=False)
    all_df.to_parquet(f"{DATA_DIR}/all_floor_size.parquet")

    # Delete floorplans
    for file in floorplans:
        os.remove(f"{FLOORPLANS_DIR}/{file}")
    os.rmdir(f"media/floorplans/{search_area}")
