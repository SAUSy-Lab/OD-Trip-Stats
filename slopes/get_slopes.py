import pandas as pd
import geopandas as gpd
import pyrosm
import time
import os

start_time = time.time()

# Initialize the OSM object

osm = pyrosm.OSM("gtha_2017.pbf")

# getting edges

nodes, edges = osm.get_network(nodes=True, network_type="walking")

edges1 = edges[['u','v','length']]
edges1.rename(columns = {'u':'i', 'v':'j'}, inplace = True)

edges2 = edges[['v','u','length']]
edges2.rename(columns = {'v':'i', 'u':'j'}, inplace = True)

df = pd.concat([edges1, edges2 ], axis=0)

print(edges)
print(list(edges.columns))

del edges, edges1, edges2

#






# read in elevation data

dfe = pd.read_csv("elevs/0_nodes_elev.csv")
for filename in os.listdir("elevs"):
    if filename.endswith(".csv"):
        dfe = pd.concat([dfe, pd.read_csv("elevs/" + filename)], axis = 0)
dfe = dfe.drop_duplicates()




# joining data

df = df.merge(dfe, how="left", left_on='i', right_on="id")
df.rename(columns = {'elev':'i_elev'}, inplace = True)

df = df.merge(dfe, how="left", left_on='j', right_on="id")
df.rename(columns = {'elev':'j_elev'}, inplace = True)

df = df[["i","j","length", "i_elev","j_elev"]]


# computuing slope

df["slope"] = (df["j_elev"] - df["i_elev"]) / df["length"]

print(df)



#
