import geopandas as gpd
# from process import PREDICTORS
from pickle import load as pickle_load
from pandas import DataFrame
from geopandas import GeoDataFrame, points_from_xy
import contextily as cx
import matplotlib.pyplot as plt

# check road name: https://data.linz.govt.nz/layer/50329-nz-road-centrelines-topo-150k/
# check speed limit: https://opendata-nzta.opendata.arcgis.com/datasets/aa376f1f2f3643bdac4d18855229239c/explore?location=-42.022106%2C-7.361753%2C5.95

import rioxarray as rxr
dataarray = rxr.open_rasterio("/Users/zhans/Downloads/lris-nzenvds-slope-degrees-v10-GTiff/nzenvds-slope-degrees-v10.tif")
df = dataarray[0].to_pandas()

-41.119111345585395, 174.98767281285978
dataarray.sel(x=174.98767281285978, y=-41.119111345585395, method="nearest").values
target_name = "target1"

locations_to_use = ["State Highways", "Upper Hutt City", "Queenstown-Lakes District"]

locations_to_be_analyzed = {
    "Upper Hutt City": {
        "Field Street base": {
            "name": "Field Street",
            "crashSHDescription": "No",
            "NumberOfLanes": 2.0,
            "flatHill": "Flat", # "Flat" or "Hill Road"
            "weather": "Fine",
            "light": "Overcast",
            "roadSurface": "Sealed",
            "speedlimit": 50.0
        },
        "Field Street policy1": {
            "name": "Field Street",
            "crashSHDescription": "No",
            "NumberOfLanes": 2.0,
            "flatHill": "Flat",
            "weather": "Fine",
            "light": "Overcast",
            "roadSurface": "Sealed",
            "speedlimit": 40.0
        },
        "Field Street policy2": {
            "name": "Field Street",
            "crashSHDescription": "No",
            "NumberOfLanes": 2.0,
            "flatHill": "Flat",
            "weather": "Fine",
            "light": "Overcast",
            "roadSurface": "Sealed",
            "speedlimit": 60.0
        },
        
        },
    "State Highways": {
        "WELLINGTON URBAN MOTORWAY base": {
            "name": "WELLINGTON URBAN MOTORWAY",
            "crashSHDescription": "Yes",
            "NumberOfLanes": 4.0,
            "flatHill": "Flat",
            "weather": "Fine",
            "light": "Overcast",
            "roadSurface": "Sealed",
            "speedlimit": 100.0
        },
        "WELLINGTON URBAN MOTORWAY policy1": {
            "name": "WELLINGTON URBAN MOTORWAY",
            "crashSHDescription": "Yes",
            "NumberOfLanes": 4.0,
            "flatHill": "Flat",
            "weather": "Fine",
            "light": "Overcast",
            "roadSurface": "Sealed",
            "speedlimit": 90.0
        },

        "WELLINGTON URBAN MOTORWAY policy2": {
            "name": "WELLINGTON URBAN MOTORWAY",
            "crashSHDescription": "Yes",
            "NumberOfLanes": 4.0,
            "flatHill": "Flat",
            "weather": "Fine",
            "light": "Overcast",
            "roadSurface": "Sealed",
            "speedlimit": 110.0
        }
    },
    "Queenstown-Lakes District": {
        "CROWN RANGE ROAD base": {
            "name": "CROWN RANGE ROAD",
            "crashSHDescription": "No",
            "NumberOfLanes": 2.0,
            "flatHill": "Hill Road",
            "weather": "Fine",
            "light": "Overcast",
            "roadSurface": "Sealed",
            "speedlimit": 100.0
        },
        "CROWN RANGE ROAD policy1": {
            "name": "CROWN RANGE ROAD",
            "crashSHDescription": "No",
            "NumberOfLanes": 2.0,
            "flatHill": "Hill Road",
            "weather": "Fine",
            "light": "Overcast",
            "roadSurface": "Sealed",
            "speedlimit": 90.0
        },
    },

}


nslr_path = "/Users/zhans/Github/road_fatalities_model/etc/National_Speed_Limit_Register_(NSLR)/National_Speed_Limit_Register_(NSLR).shp"
roadline_path = "/Users/zhans/Github/road_fatalities_model/etc/lds-nz-road-centrelines-topo-150k-SHP/nz-road-centrelines-topo-150k.shp"
model_path = f"rfm/model_{target_name}.model"


nslr = gpd.read_file(nslr_path)
roadline = gpd.read_file(roadline_path)
model = pickle_load( open(model_path, "rb" ) )

output = {}

for proc_rcazone in locations_to_use:

    proc_speed_zone_data = nslr.loc[nslr["rcaZoneR_1"] == proc_rcazone]

    proc_speed_zone_data = proc_speed_zone_data.to_crs(4326)

    if proc_rcazone not in output:
        output[proc_rcazone] = {}

    for proc_street_cfg_name in locations_to_be_analyzed[proc_rcazone]:

        proc_street_cfg = locations_to_be_analyzed[proc_rcazone][proc_street_cfg_name]
        proc_street_name = proc_street_cfg["name"]

        proc_street_data = roadline.loc[roadline["name_ascii"] == proc_street_name.upper() ]

        proc_data = gpd.sjoin(proc_street_data, proc_speed_zone_data, op='intersects')

        roadspd = proc_data["speedLim_2"]

        if proc_street_cfg["speedlimit"] is not None:
            roadspd = proc_street_cfg["speedlimit"]

        proc_points = proc_data.apply(lambda x: [y for y in x['geometry'].coords], axis=1).values[0]

        test_data = {}
        for proc_key in PREDICTORS[target_name]:
            if PREDICTORS[target_name][proc_key]["use"]:
                test_data[proc_key] = []

        for proc_point_input in proc_points:
            
            test_data["lon"].append(proc_point_input[0])
            test_data["lat"].append(proc_point_input[1])
            test_data["speedLimit"].append(roadspd)
            test_data["crashSHDescription"].append(proc_street_cfg["crashSHDescription"])
            test_data["NumberOfLanes"].append(proc_street_cfg["NumberOfLanes"])
            test_data["flatHill"].append(proc_street_cfg["flatHill"])
            test_data["weatherA"].append(proc_street_cfg["weather"])
            test_data["light"].append(proc_street_cfg["light"])
            test_data["roadSurface"].append(proc_street_cfg["roadSurface"])


        test_data = DataFrame.from_dict(test_data)

        for proc_predictor_name in test_data:
            if PREDICTORS[target_name][proc_predictor_name]["convert"] is not None:
                for convert_key in PREDICTORS[target_name][proc_predictor_name]["convert"]:
                    test_data[proc_predictor_name] = test_data[proc_predictor_name].replace(
                        [convert_key], 
                        PREDICTORS[target_name][proc_predictor_name]["convert"][convert_key])

        output[proc_rcazone][proc_street_cfg_name] = model["model"].predict(
            model["scaler"].transform(test_data)) * 100.0

        if "base" in proc_street_cfg_name:
            proc_risk_base =  output[proc_rcazone][proc_street_cfg_name]

    for proc_street_cfg_name in output[proc_rcazone]:

        if "base" not in proc_street_cfg_name:
            risk_change = 100.0 * (output[proc_rcazone][proc_street_cfg_name] - proc_risk_base) / proc_risk_base
            test_data[f"{proc_street_cfg_name} base"] = proc_risk_base
            test_data[f"{proc_street_cfg_name} risk change"] = risk_change

            df = GeoDataFrame(test_data, geometry=points_from_xy(test_data.lon, test_data.lat))
            df = df.set_crs(epsg=4326)

            fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2)

            fig.subplots_adjust(wspace=0.3)

            df.plot(ax=ax1, column=f"{proc_street_cfg_name} base", alpha=0.3, legend=True, legend_kwds={'format': '%.2f%%'}, cmap="jet")
            cx.add_basemap(ax1, crs=roadline.crs.to_string(), source=cx.providers.OpenStreetMap.DE, attribution_size=1)
            ax1.set_title("Base Risk")
            ax1.set_xticks([])
            ax1.set_yticks([])



            plt.subplot(122)
            df.plot(ax=ax2, column=f"{proc_street_cfg_name} risk change", alpha=0.3, legend=True, legend_kwds={'format': '%.3f%%'})
            cx.add_basemap(ax2, crs=roadline.crs.to_string(), source=cx.providers.OpenStreetMap.DE, attribution_size=1)
            ax2.set_title("Risk Change")
            ax2.set_xticks([])
            ax2.set_yticks([])

            plt.suptitle(proc_street_cfg_name)

            plt.savefig(f"{proc_street_cfg_name}.png".replace(" ", "_"), bbox_inches="tight")
            plt.close()
