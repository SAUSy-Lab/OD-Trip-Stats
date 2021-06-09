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


# # (based on geog - "ct" or "da") and mode (Walk, Drive, Bicycle)
# trip_stats_tts("da","Drive","trips_drive_da_osrm_free.csv")


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

    dfself.to_csv("survey_data/" + out_name + '.csv', index = False)

# trips_intrazonal_tts("ct","Bicycle","trips_bike_ct_intrazonal.csv")





def auto_gdb_to_csv(table_name, gdb_path, output_path, input_fields=None):

    """
    Taking the big auto travel time tables and saving as csv files

    Adapted from here https://gist.github.com/d-wasserman/e9c98be1d0caebc2935afecf0ba239a0 - Thank you!

    Function will convert an arcgis table into a pandas dataframe with an object ID index, and the selected
    input fields using an arcpy.da.SearchCursor.
    """

    in_table = gdb_path + table_name

    OIDFieldName = arcpy.Describe(in_table).OIDFieldName
    if input_fields:
        final_fields = [OIDFieldName] + input_fields
    else:
        final_fields = [field.name for field in arcpy.ListFields(in_table)]
    data = [row for row in arcpy.da.SearchCursor(in_table, final_fields)]
    fc_dataframe = pd.DataFrame(data, columns=final_fields)
    del data
    fc_dataframe = fc_dataframe.set_index(OIDFieldName, drop=True)

    fc_dataframe.Total_Distance = fc_dataframe.Total_Distance.astype(int)
    fc_dataframe.Total_Time = fc_dataframe.Total_Time.astype(int)

    fc_dataframe.to_csv(output_path + table_name + ".csv", index = False)

# # e.g. running the above
# for table in ['ct_other_other_','ct_other_home_','ct_home_other_','da_other_other_','da_other_home_','da_home_other_']:
#    auto_gdb_to_csv(table + time_period,'C://Users//jamaps//Documents//phac//phac1//phac1.gdb//','C://Users//jamaps//Documents//phac//out_matrices_tor//',['OriginName','DestinationName','Total_Distance','Total_Time'])




# mode can be "time" or "free"
def auto_csv_to_trips(geog, mode, in_path, out_name):

    df = pd.read_csv("survey_data/od_for_export.csv", dtype = str)
    df = df[df["mode"] == "Drive"]

    print(df)

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


    # compute self potential trips here
    dfa = pd.read_csv("coordinates/" + geog + "_2016_area.csv", dtype = "str")

    # merge with the survey data
    dfself = dfself.merge(dfa, how="left", left_on="orig_loc", right_on = "id")

    # compute intrazonal times
    dfself["area_km"] = dfself["area_km"].astype(float)

    dfself['intrazonals'] = dfself.apply(lambda x: intrazonal(x['area_km'], "Drive"), axis=1)
    dfself[['duration','distance']] = pd.DataFrame(dfself['intrazonals'].tolist(), index=dfself.index)

    # output appropriate columns
    dfself = dfself[["tid","duration","distance"]]

    # for just free flow times
    if mode == "free":

        # home to other
        dft = pd.read_csv(in_path + geog + "_home_other_free.csv", dtype = "str")
        dft = dft.rename(columns={"OriginName": "orig_loc", "DestinationName": "dest_loc"})
        dfho = df[(df["orig_type"] == "Home") & (df["dest_type"] == "Other")]

        dfho = dfho.merge(dft, how = "left", left_on=['orig_loc','dest_loc'], right_on = ['orig_loc','dest_loc'])
        dfho = dfho.rename(columns={"Total_Distance": "distance", "Total_Time": "duration"})
        dfho = dfho[["tid","duration","distance"]]

        # other to other
        dft = pd.read_csv(in_path + geog + "_other_other_free.csv", dtype = "str")
        dft = dft.rename(columns={"OriginName": "orig_loc", "DestinationName": "dest_loc"})
        dfoo = df[(df["orig_type"] == "Other") & (df["dest_type"] == "Other")]

        dfoo = dfoo.merge(dft, how = "left", left_on=['orig_loc','dest_loc'], right_on = ['orig_loc','dest_loc'])
        dfoo = dfoo.rename(columns={"Total_Distance": "distance", "Total_Time": "duration"})
        dfoo = dfoo[["tid","duration","distance"]]

        # other to home
        dft = pd.read_csv(in_path + geog + "_other_home_free.csv", dtype = "str")
        dft = dft.rename(columns={"OriginName": "orig_loc", "DestinationName": "dest_loc"})
        dfoh = df[(df["orig_type"] == "Other") & (df["dest_type"] == "Home")]

        dfoh = dfoh.merge(dft, how = "left", left_on=['orig_loc','dest_loc'], right_on = ['orig_loc','dest_loc'])
        dfoh = dfoh.rename(columns={"Total_Distance": "distance", "Total_Time": "duration"})
        dfoh = dfoh[["tid","duration","distance"]]


        out = pd.concat([dfself,dfho,dfoo,dfoh])
        out = out.fillna(-1)
        out["duration"] = out["duration"].astype(int)
        out["distance"] = out["distance"].astype(int)

        out.to_csv("survey_data/" + out_name, index = False)

        print(out)


# # e.g. run with
# auto_csv_to_trips("da","free",'out_matrices_tor/',"trips_drive_da_esri_free.csv")





def concat_trips():

    df = pd.read_csv("survey_data/od_for_export.csv")

    df.has_data = 0


    # joining in the Bike data
    bike_trips = ["bike_ct_osrm_elev","bike_ct_osrm_flat","bike_da_osrm_elev","bike_da_osrm_flat"]

    for trip in bike_trips:
        matrix_name = "survey_data/trips_" + trip + ".csv"
        dft = pd.read_csv(matrix_name)
        df = df.merge(dft, how = "left", left_on = "tid", right_on = "tid")
        df.loc[df['duration'] > 0, 'has_data'] = 1
        df = df.rename(columns={
            "distance": trip + "_distance",
            "duration": trip + "_duration"
            })


    # joining in the Walk data
    walk_trips = ["walk_ct_osrm_elev","walk_ct_osrm_flat","walk_da_osrm_elev","walk_da_osrm_flat"]

    for trip in walk_trips:
        matrix_name = "survey_data/trips_" + trip + ".csv"
        dft = pd.read_csv(matrix_name)
        df = df.merge(dft, how = "left", left_on = "tid", right_on = "tid")
        df.loc[df['duration'] > 0, 'has_data'] = 1
        df = df.rename(columns={
            "distance": trip + "_distance",
            "duration": trip + "_duration"
            })

    # joining in the Walk data
    car_trips = ["drive_ct_osrm_free","drive_da_osrm_free"]

    for trip in car_trips:
        matrix_name = "survey_data/trips_" + trip + ".csv"
        dft = pd.read_csv(matrix_name)
        df = df.merge(dft, how = "left", left_on = "tid", right_on = "tid")
        df.loc[df['duration'] > 0, 'has_data'] = 1
        df = df.rename(columns={
            "distance": trip + "_distance",
            "duration": trip + "_duration"
            })

    df.to_csv("survey_data/od_with_ddinfo.csv", index = False)



concat_trips()
