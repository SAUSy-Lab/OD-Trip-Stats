# using OSRM to compute OD trip stats for the TTS

import json
import requests
import time
import pandas as pd
from trips import osrm_trip
from trips import intrazonal


# joining in XY coords (based on geog - "ct" or "da") and mode (Walk, Drive, Bicycle)
def trip_stats_tts(geog, mode, out_name):

    # load in survey data
    df = pd.read_csv("survey_data/od_for_export.csv", dtype = str)
    df = df[df["mode"] == mode]

    # add in CT ids, if looking at CT
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

    print(df)
    print(dfself)



    # compute self potential trips here
    dfa = pd.read_csv("coordinates/" + geog + "_2016_area.csv", dtype = "str")

    # merge with the survey data
    dfself = dfself.merge(dfa, how="left", left_on="orig_loc", right_on = "id")

    # compute intrazonal times
    dfself["area_km"] = dfself["area_km"].astype(float)
    dfself['intrazonals'] = dfself.apply(lambda x: intrazonal(x['area_km'], mode), axis=1)
    dfself[['duration','distance']] = pd.DataFrame(dfself['intrazonals'].tolist(), index=dfself.index)

    # output appropriate columns
    dfself = dfself[["tid","duration","distance"]]


    # loop over trips, computing stats for each
    out = []
    i = 0

    # home to other
    dfho = df[(df["orig_type"] == "Home") & (df["dest_type"] == "Other")]

    dfho = dfho.merge(xyhome, how="left", left_on='orig_loc', right_on="id")
    dfho = dfho.rename(columns={"X": "Xi", "Y": "Yi"})
    del dfho["id"]
    dfho = dfho.merge(xyother, how="left", left_on='dest_loc', right_on="id")
    dfho = dfho.rename(columns={"X": "Xj", "Y": "Yj"})
    dfho = dfho[["tid","Xi","Yi","Xj","Yj"]]

    for index, row in dfho.iterrows():
        duration, distance = osrm_trip(row["tid"],row["Xi"],row["Yi"],row["Xj"],row["Yj"],"walking")
        out.append([row["tid"], duration, distance])
        i += 1
        print(i)


    # other to Home
    dfoh = df[(df["orig_type"] == "Other") & (df["dest_type"] == "Home")]
    dfoh = dfoh.merge(xyhome, how="left", left_on='orig_loc', right_on="id")
    dfoh = dfoh.rename(columns={"X": "Xi", "Y": "Yi"})
    del dfoh["id"]
    dfoh = dfoh.merge(xyother, how="left", left_on='dest_loc', right_on="id")
    dfoh = dfoh.rename(columns={"X": "Xj", "Y": "Yj"})
    dfoh = dfoh[["tid","Xi","Yi","Xj","Yj"]]

    for index, row in dfoh.iterrows():
        duration, distance = osrm_trip(row["tid"],row["Xi"],row["Yi"],row["Xj"],row["Yj"],"walking")
        out.append([row["tid"], duration, distance])
        i += 1
        print(i)


    # other to other
    dfoo = df[(df["orig_type"] == "Other") & (df["dest_type"] == "Other")]
    dfoo = dfoo.merge(xyhome, how="left", left_on='orig_loc', right_on="id")
    dfoo = dfoo.rename(columns={"X": "Xi", "Y": "Yi"})
    del dfoo["id"]
    dfoo = dfoo.merge(xyother, how="left", left_on='dest_loc', right_on="id")
    dfoo = dfoo.rename(columns={"X": "Xj", "Y": "Yj"})
    dfoo = dfoo[["tid","Xi","Yi","Xj","Yj"]]

    for index, row in dfoo.iterrows():
        duration, distance = osrm_trip(row["tid"],row["Xi"],row["Yi"],row["Xj"],row["Yj"],"walking")
        out.append([row["tid"], duration, distance])
        i += 1
        print(i)

    out = pd.DataFrame(out, columns = ["tid","duration","distance"])

    out = pd.concat([dfself,out])

    out["duration"] = out["duration"].astype(int)
    out["distance"] = out["distance"].astype(int)

    out.to_csv("survey_data/" + out_name, index = False)



def trips_intrazonal_tts(geog, mode, out_name):

    # load in survey data
    df = pd.read_csv("survey_data/od_for_export.csv", dtype = str)
    df = df[df["mode"] == mode]


    # add in CT ids, if looking at CT
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

    # seperating self trips (i = j) and non-self (i != j)
    dfself = df[df["orig_loc"] == df["dest_loc"]]
    df = df[df["orig_loc"] != df["dest_loc"]]




    # get appropriate areas of zones
    dfa = pd.read_csv("coordinates/" + geog + "_2016_area.csv", dtype = "str")

    # merge with the survey data
    dfself = dfself.merge(dfa, how="left", left_on="orig_loc", right_on = "id")

    # compute intrazonal times
    dfself["area_km"] = dfself["area_km"].astype(float)
    dfself['intrazonals'] = dfself.apply(lambda x: intrazonal(x['area_km'], mode), axis=1)
    dfself[['duration','distance']] = pd.DataFrame(dfself['intrazonals'].tolist(), index=dfself.index)

    # output appropriate columns
    dfself = dfself[["tid","duration","distance"]]

    dfself.to_csv("survey_data/" + out_name, index = False)



# (based on geog - "ct" or "da") and mode (Walk, Drive, Bicycle)
trip_stats_tts("ct","Walk","trips_walk_ct_osrm_elev.csv")


# trips_intrazonal_tts("ct","Bicycle","trips_bike_ct_intrazonal.csv")
