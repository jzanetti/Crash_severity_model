from geopandas import read_file as gpd_read_file
from process import NSLR_DATASET, ROADLINE_DATASET
from pickle import load as pickle_load
from pandas import DataFrame
from geopandas import sjoin
from process.utils import data_conversions
from geopandas import GeoDataFrame, points_from_xy
from rioxarray import open_rasterio
from xarray.core.dataarray import DataArray

def read_base_data(input_cfg: dict) -> dict:
    """Read base data for the model prediction

    Returns:
        dict: base data for prediction
    """
    nslr = gpd_read_file(input_cfg["nslr"])
    roadline = gpd_read_file(input_cfg["road_centrelines"])
    roadslope = open_rasterio(input_cfg["road_slope"])

    return {"nslr": nslr, "roadline": roadline, "roadslope": roadslope}


def read_model(model_path: str):
    """Read trained model

    Args:
        model_path (str): model path

    Returns:
        _type_: _description_
    """
    return pickle_load(open(model_path, "rb" ))



def get_data_for_prediction(
    all_roads: dict,
    roadslope: DataArray,
    predictors: list, 
    cfg: dict,
    road_slope_cutoff: float = 3.0) -> DataFrame:
    """Get data for prediction

    Args:
        all_roads (dict): all roads to be used
        predictors (list): predictors to be applied
        cfg (dict): data configuration

    Returns:
        DataFrame: geopandas dataframe
    """
    output = {}

    for proc_predictor in predictors:
        output[proc_predictor] = []

    for proc_road in all_roads:

        default_spd = proc_road[1]
        default_lanes = proc_road[2]

        for proc_point in proc_road[0]:

            # x = roadslope.sel(x=proc_base_data["lon"].values, y=proc_base_data["lat"].values, method="nearest").values[0, :, :].diagonal()
            for proc_predictor in predictors:

                if proc_predictor == "lon":
                    output["lon"].append(proc_point[0])

                elif proc_predictor == "lat":
                    output["lat"].append(proc_point[1])

                elif proc_predictor == "speedLimit":
                    spd_to_use = default_spd
                    if cfg["speedlimit"] is not None:
                        spd_to_use = cfg["speedlimit"]

                    output["speedLimit"].append(spd_to_use)

                elif proc_predictor == "flatHill":
                    if cfg["flatHill"] is not None:
                        flatHill_to_use = cfg["flatHill"]
                    else:
                        road_slope = roadslope.sel(
                            x=proc_point[0], y=proc_point[1], method="nearest").values[0]

                        if road_slope > road_slope_cutoff:
                            flatHill_to_use = "Hill Road"
                        else:
                            flatHill_to_use = "Flat"
                    output["flatHill"].append(flatHill_to_use)

                elif proc_predictor == "NumberOfLanes":
                    lanes_to_use = default_lanes
                    if cfg["NumberOfLanes"] is not None:
                        lanes_to_use = cfg["NumberOfLanes"]
                    output["NumberOfLanes"].append(lanes_to_use)


                else:
                    output[proc_predictor].append(cfg[proc_predictor])
    
    return DataFrame.from_dict(output)


def area_prediction(model :dict, base_data: dict, area_name: str, predict_cfg: dict) -> DataFrame:
    """Generate prediction for an area

    Args:
        model (dict): model to be used
        base_data (dict): base data to be applied
        area_name (str): area name, e.g., Upper Hutt City
        predict_cfg (dict): prediction configuration

    Returns:
        DataFrame: Dataframe for output
    """

    proc_speed_zone_data = base_data["nslr"].loc[
        base_data["nslr"]["rcaZoneR_1"] == area_name]

    proc_speed_zone_data = proc_speed_zone_data.to_crs(4326)
    proc_data = sjoin(
        base_data["roadline"], 
        proc_speed_zone_data, op="intersects")

    proc_all_roads = proc_data.apply(
        lambda x: [y for y in (
            x["geometry"].coords, 
            x["speedLim_2"], 
            x["lane_count"])], axis=1)

    output = {}
    for policy_name in predict_cfg["areas"][area_name]:

        proc_base_data = get_data_for_prediction(
            proc_all_roads,
            base_data["roadslope"],
            predict_cfg["predictors"], 
            predict_cfg["areas"][area_name][policy_name])

        proc_base_data = data_conversions(
            proc_base_data, predict_cfg["predictors"])

        proc_base_data["risk"] = model["model"].predict(
            model["scaler"].transform(proc_base_data))

        if "lat" in predict_cfg["predictors"] and "lon" in predict_cfg["predictors"]:
            proc_base_data = GeoDataFrame(
                proc_base_data, 
                geometry=points_from_xy(
                    proc_base_data.lon, proc_base_data.lat))

            proc_base_data = proc_base_data.set_crs(epsg=4326)

        output[policy_name] = proc_base_data

    return output
