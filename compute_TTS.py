# using OSRM to compute OD trip stats for the TTS

import json
import requests
import time
import pandas as pd

# subsetting TTS trips by mode (Walk, Drive, Bicycle)
def read_subset_tts(mode, path):
    df = pd.read_csv(path)
    df = df[df["mode"] == mode]
    return df

# joining in XY coords (based on geog - "ct" or "da") to prep for routing
def join_coords(geog, mode, od_path):

    df = read_subset_tts(mode, od_path)
    xyhome = pd.read_csv("coordinates/" + geog + "_2016_pts_pop.csv")
    xyother = pd.read_csv("coordinates/" + geog + "_2016_pts_geom.csv")

    xyhome = xyhome[["X","Y","id"]]
    xyother = xyother[["X","Y","id"]]

    print(xyhome)
    print(xyother)
    print(df)

join_coords("ct","Walk","survey_data/od_for_export.csv")
