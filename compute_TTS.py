# using OSRM to compute OD trip stats for the TTS

import json
import requests
import time
import pandas as pd

# subsetting TTS trips by
def read_subset_tts(mode, path):

    return df

# joining in XY coords (based on geog - "ct" or "da") and mode (Walk, Drive, Bicycle)
def trip_stats_tts(geog, mode):

    # load in data
    df = pd.read_csv("survey_data/od_for_export.csv", dtype = str)
    df = df[df["mode"] == mode]

    # load in coords, and reduce columns
    xyhome = pd.read_csv("coordinates/" + geog + "_2016_pts_pop.csv", dtype = str)
    xyother = pd.read_csv("coordinates/" + geog + "_2016_pts_geom.csv", dtype = str)
    xyhome = xyhome[["X","Y","id"]]
    xyother = xyother[["X","Y","id"]]

    # home to other
    dfho = df[(df["orig_type"] == "Home") & (df["dest_type"] == "Other")]
    dfho = dfho.merge(xyhome, how="left", left_on='orig_loc', right_on="id")
    dfho = dfho.rename(columns={"X": "Xi", "Y": "Yi"})
    del dfho["id"]
    print(dfho)

    # home to Home
    dfhh = df[(df["orig_type"] == "Home") & (df["dest_type"] == "Home")]

    # other to Home
    dfoh = df[(df["orig_type"] == "Other") & (df["dest_type"] == "Home")]

    # other to other
    dfoo = df[(df["orig_type"] == "Other") & (df["dest_type"] == "Other")]



    # other to home


    # other to other


    # home to home



trip_stats_tts("da","Walk")
