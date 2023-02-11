import geopandas as gpd
import numpy as np
from scipy.interpolate import interp1d
from geopandas import GeoDataFrame, points_from_xy
from shapely.geometry import LineString
# Create a GeoDataFrame with Point objects
"""
points_gdf = gpd.GeoDataFrame({
    'x': [1, 2, 3],
    'y': [1, 2, 3],
    'value': [10, 20, 30]})

points_gdf = GeoDataFrame(
    points_gdf, 
    geometry=points_from_xy(
        points_gdf.x, points_gdf.y))

points_gdf = points_gdf.set_crs(epsg=4326)

# Create a GeoDataFrame with LineString objects
lines_gdf = gpd.GeoDataFrame({
    'geometry': [LineString([(0, 0), (4, 4)]),
                 LineString([(0, 4), (4, 0)])]
})

# overlapped_gdf = gpd.overlay(lines_gdf, points_gdf, how='union')
"""
from geopandas import read_file as gpd_read_file
from pandas import read_csv
from pyproj import Proj, transform

datapath = "etc/data/road_centreline/nz-road-centrelines-topo-150k.shp"
cas_datapath = "etc/data/cas.csv"
CAS_PROJECTION = "EPSG:2193"

points_gdf = read_csv(cas_datapath)
lines_gdf = gpd_read_file(datapath)


points_gdf["lon"], points_gdf["lat"] = transform(
    Proj(init=CAS_PROJECTION), 
    Proj(init='epsg:4326'),
    points_gdf["X"], 
    points_gdf["Y"])

points_gdf = GeoDataFrame(
    points_gdf, 
    geometry=points_from_xy(
        points_gdf.lon, points_gdf.lat))

points_gdf = points_gdf.set_crs(epsg=4326)
import geopandas
print("234")
x = geopandas.sjoin_nearest(lines_gdf, points_gdf, max_distance=1.0)
print(x[["weatherA", "geometry"]])
x.plot(column="weatherA")
import matplotlib.pyplot as plt
plt.savefig("test.png")
plt.close()
raise Exception("!2321")

# For each LineString, compute the nearest Point and its value
interpolated_values = []
for line in lines_gdf.geometry:
    nearest_points = points_gdf.distance(line).sort_values().head(2)

    nearest_points_gdf = points_gdf.loc[nearest_points.index]
    x = [point.x for point in nearest_points_gdf.geometry]
    y = [point.y for point in nearest_points_gdf.geometry]
    z = nearest_points_gdf['bicycle'].tolist()

    f = interp1d(x, z, kind='linear')
    interpolated_value = f(line.centroid.x)
    interpolated_values.append(interpolated_value)

lines_gdf['interpolated_value'] = interpolated_values

print(lines_gdf)