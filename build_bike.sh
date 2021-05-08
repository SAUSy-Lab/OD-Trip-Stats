osmconvert gtha_2017.pbf > gtha_2017_bike.osm.xml

osrm-extract bike/gtha_2017_bike.osm.xml -p bike/bicycle.lua

rm bike/gtha_2017_bike.osm.xml

# osrm-contract bike/gtha_2017_bike.osrm

osrm-contract bike/gtha_2017_bike.osrm --segment-speed-file bike/osm_speeds_bike.csv

osrm-routed bike/gtha_2017_bike.osrm
