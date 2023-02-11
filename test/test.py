from geopandas import read_file as gpd_read_file
from pandas import read_csv
from geopandas import GeoDataFrame, points_from_xy
import pysal
from pyproj import Proj, transform
from shapely.geometry import Point, LineString

datapath = "etc/data/road_centreline/nz-road-centrelines-topo-150k.shp"
cas_datapath = "etc/data/cas.csv"
CAS_PROJECTION = "EPSG:2193"

cas = read_csv(cas_datapath)
data = gpd_read_file(datapath)

cas["lon"], cas["lat"] = transform(
    Proj(init=CAS_PROJECTION), 
    Proj(init='epsg:4326'),
    cas["X"], 
    cas["Y"])

x = 3
col = "value"

cas = GeoDataFrame(
    cas, 
    geometry=points_from_xy(
        cas.lon, cas.lat))

import pysal
segments = []
for i, row in data.iterrows():
    line = row.geometry
    num_segments = 10 # or another desired number of segments
    segment_length = line.length / num_segments
    for j in range(num_segments):
        start = line.interpolate(j * segment_length)
        end = line.interpolate((j + 1) * segment_length)
        segment = LineString([start, end])
        segments.append((i, j, segment))

import spatialpandas as spd


segments_gdf = GeoDataFrame(segments, columns=["line_id", "segment_id", "geometry"])

# Create an IDW interpolator
col = "bicycle"
idw = pysal.explore.esda.kenel.adaptive_kernel_density.AdaptiveKernelDensity(cas[col], cas.geometry)

# Interpolate the values for the segments
segments_gdf[col] = idw(segments_gdf.geometry)

# Aggregate the values for each linestring
aggregated = segments_gdf.groupby("line_id").mean()
data[col] = aggregated[col]


import spatialpandas as spd
interpolated_points = spd.interpolate_points_to_lines(cas, data)

"""
import pysal
import pandas as pd
import geopandas as gpd

# Load the source GeoDataFrame with known values
gdf_src = gpd.read_file("source.shp")

# Load the target GeoDataFrame with unknown values
gdf_tgt = gpd.read_file("target.shp")

# Specify the column with the known values
col = "value"

# Create an IDW interpolator
idw = pysal.explore.esda.adaptive_kernel_density.AdaptiveKernelDensity(gdf_src[col], gdf_src.geometry)

# Interpolate the values for the target GeoDataFrame
gdf_tgt[col] = idw(gdf_tgt.geometry)
"""

"""
f the source dataframe has point geometry and the target dataframe has linestring geometry, you can perform interpolation along the linestring by either splitting the linestring into segments or by using a spatial join to assign values to each segment.

Here's an example in Python using the Geopandas library and the PySAL library's IDW interpolation method:


    import pysal
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, LineString

# Load the source GeoDataFrame with known values
gdf_src = gpd.read_file("source.shp")

# Load the target GeoDataFrame with unknown values
gdf_tgt = gpd.read_file("target.shp")

# Specify the column with the known values
col = "value"

# Split the target linestrings into segments
segments = []
for i, row in gdf_tgt.iterrows():
    line = row.geometry
    num_segments = 10 # or another desired number of segments
    segment_length = line.length / num_segments
    for j in range(num_segments):
        start = line.interpolate(j * segment_length)
        end = line.interpolate((j + 1) * segment_length)
        segment = LineString([start, end])
        segments.append((i, j, segment))

segments_gdf = gpd.GeoDataFrame(segments, columns=["line_id", "segment_id", "geometry"])

# Create an IDW interpolator
idw = pysal.explore.esda.adaptive_kernel_density.AdaptiveKernelDensity(gdf_src[col], gdf_src.geometry)

# Interpolate the values for the segments
segments_gdf[col] = idw(segments_gdf.geometry)

# Aggregate the values for each linestring
aggregated = segments_gdf.groupby("line_id").mean()
gdf_tgt[col] = aggregated[col]


In this example, the source GeoDataFrame gdf_src contains known values in a column named value. The target GeoDataFrame gdf_tgt contains linestring geometries with unknown values. The linestrings are split into segments and stored in a new GeoDataFrame segments_gdf. The IDW interpolation method from the PySAL library's esda module is used to interpolate the unknown values for each segment based on the known values in the source GeoDataFrame. Finally, the values for each segment are aggregated to get the mean value for each linestring and stored in the value column of the target GeoDataFrame gdf_tgt.

"""