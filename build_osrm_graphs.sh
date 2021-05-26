osmconvert gtha_2017.pbf > gtha_2017_bike.osm.xml

osrm-extract bike/gtha_2017_bike.osm.xml -p bike/bicycle.lua

rm bike/gtha_2017_bike.osm.xml

# osrm-contract bike/gtha_2017_bike.osrm

osrm-contract bike/gtha_2017_bike.osrm --segment-speed-file bike/osm_speeds_bike.csv

osrm-routed bike/gtha_2017_bike.osrm





osmconvert gtha_2017.pbf > gtha_2017_walk.osm.xml

osrm-extract walk/gtha_2017_walk.osm.xml -p walk/foot.lua

rm walk/gtha_2017_walk.osm.xml

# osrm-contract bike/gtha_2017_bike.osrm

osrm-contract walk/gtha_2017_walk.osrm --segment-speed-file bike/gtha_2017_walk.csv

osrm-routed walk/gtha_2017_walk.osrm









osmconvert network_data/gtha_2017.pbf > network_data/gtha_2017_car.osm.xml

osrm-extract drive/gtha_2017_car.osm.xml -p drive/car.lua

rm drive/gtha_2017_car.osm.xml

osrm-contract drive/gtha_2017_car.osrm

osrm-routed drive/gtha_2017_car.osrm
