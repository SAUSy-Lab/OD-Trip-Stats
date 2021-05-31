osmconvert gtha_2017.pbf > gtha_2017_bike.osm.xml

osrm-extract bike/gtha_2017.osm.xml -p bike/bicycle.lua

osrm-contract bike/gtha_2017.osrm --segment-speed-file bike/osm_speeds_bike.csv

osrm-routed bike/gtha_2017.osrm






osmconvert gtha_2017.pbf > gtha_2017_walk.osm.xml

osrm-extract walk/gtha_2017.osm.xml -p walk/foot.lua

osrm-contract walk/gtha_2017.osrm --segment-speed-file walk/osm_speeds_walk.csv

osrm-routed walk/gtha_2017.osrm






osmconvert network_data/gtha_2017.pbf > network_data/gtha_2017_car.osm.xml

osrm-extract drive/gtha_2017.osm.xml -p drive/car.lua

rm drive/gtha_2017_car.osm.xml

osrm-contract drive/gtha_2017.osrm

osrm-routed drive/gtha_2017.osrm
