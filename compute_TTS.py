# using OSRM to compute OD trip stats for the TTS

import json
import requests
import time
import pandas as pd
from trips import osrm_trip


# joining in XY coords (based on geog - "ct" or "da") and mode (Walk, Drive, Bicycle)
def trip_stats_tts(geog, mode):


    # load in survey data
    df = pd.read_csv("survey_data/od_for_export.csv", dtype = str)
    df = df[df["mode"] == mode]


    # add in CT ids, if looking at CT
    print(df)
    if geog == "ct":
        dact = pd.read_csv("coordinates/da_ct_2016_link.csv", dtype = "str")
        df = df.merge(dact, how="left", left_on='orig_loc', right_on="dauid")
        df.ctuid = df.ctuid.fillna(df['orig_loc'])
        df.orig_loc = df.ctuid
        del df["ctuid"], df["dauid"]
        df = df.merge(dact, how="left", left_on='dest_loc', right_on="dauid")
        df.ctuid = df.ctuid.fillna(df['dest_loc'])
        df.dest_loc = df.ctuid
        del df["ctuid"], df["dauid"]
        print(df)


    # load in coords, and reduce columns
    xyhome = pd.read_csv("coordinates/" + geog + "_2016_pts_pop.csv", dtype = str)
    xyother = pd.read_csv("coordinates/" + geog + "_2016_pts_geom.csv", dtype = str)
    xyhome = xyhome[["X","Y","id"]]
    xyother = xyother[["X","Y","id"]]


    # load in coordinates for stations, and append to other coords
    xystations = pd.read_csv("coordinates/transit_stations_update.csv")
    xystations = xystations.rename(columns={"route_code": "id"})
    xystations = xystations[["X","Y","id"]]

    xyhome = pd.concat([xyhome, xystations ], axis=0)
    xyother = pd.concat([xyother, xystations ], axis=0)


    # seperating self trips (i = j) and non-self (i != j)
    dfself = df[df["orig_loc"] == df["dest_loc"]]
    df = df[df["orig_loc"] != df["dest_loc"]]


    # loop over trips, computing stats for each
    out = [["tid","duration","distance"]]

    # compute self potential trips here



    # home to other
    dfho = df[(df["orig_type"] == "Home") & (df["dest_type"] == "Other")]
    dfho = dfho.merge(xyhome, how="left", left_on='orig_loc', right_on="id")
    dfho = dfho.rename(columns={"X": "Xi", "Y": "Yi"})
    del dfho["id"]
    dfho = dfho.merge(xyother, how="left", left_on='dest_loc', right_on="id")
    dfho = dfho.rename(columns={"X": "Xj", "Y": "Yj"})
    dfho = dfho[["tid","Xi","Yi","Xj","Yj"]]

    print(dfho)

    for index, row in dfho.iterrows():
        print(row["tid"])
        duration, distance = osrm_trip(row["tid"],row["Xi"],row["Yi"],row["Xj"],row["Yj"],"walking")
        out.append([row["tid"], duration, distance])





    # # other to Home
    # dfoh = df[(df["orig_type"] == "Other") & (df["dest_type"] == "Home")]
    #
    # # other to other
    # dfoo = df[(df["orig_type"] == "Other") & (df["dest_type"] == "Other")]



    # other to home


    # other to other


    # home to home



trip_stats_tts("ct","Drive")
