from process import PREDICTORS_CFG, CAS_DATASET, CAS_PROJECTION, CAS_VEHICLE_TYPES
from yaml import safe_load
from pandas import DataFrame, read_csv
from pyproj import Proj, transform
from geopandas import GeoDataFrame, points_from_xy, sjoin_nearest


def get_total_cas(cas_data: DataFrame, base_data: dict) -> DataFrame:
    """Get total CAS casuality

    Args:
        cas_data (DataFrame): cas dataset

    Returns:
        DataFrame: CAS dataset with total casualities
    """
    agg_operator = {}
    for proc_key in CAS_VEHICLE_TYPES:
        agg_operator[proc_key] = "sum"

    agg_operator["lat"] = "mean"
    agg_operator["lon"] = "mean"

    df = cas_data.groupby(
        ["region", "crashLocation1", "crashLocation2"], as_index=False).agg(agg_operator)
    df["total"]= df[CAS_VEHICLE_TYPES].sum(axis=1)

    df = GeoDataFrame(
        df, 
        geometry=points_from_xy(
            df['lon'], 
            df['lat'])
    )

    df = df.set_crs(epsg=4326)

    df["lon"] = df["lon"] % 360.0
    """
    df_line = sjoin_nearest(
        base_data["roadline"], 
        df[["geometry", "total"]], 
        max_distance=0.003)[["total", "geometry", "lat", "lon"]]

    return {"point": df, "line": df_line}
    """
    return df

def read_cfg(cfg_path: str) -> dict:
    """Read configuration file

    Args:
        cfg_path (str): _description_

    Returns:
        dict: _description_
    """
    with open(cfg_path, "r") as fid:
        cfg = safe_load(fid)

    return cfg


def read_cas(add_latlon: bool = True, add_geometry: bool = False) -> DataFrame:
    """Read CAS dataset

       Args:
        add_latlon (bool): if add lat and lon in the dataset
    """
    dataset = read_csv(CAS_DATASET)

    if add_latlon:
        dataset["lon"], dataset["lat"] = transform(
            Proj(init=CAS_PROJECTION), 
            Proj(init='epsg:4326'),
            dataset["X"], 
            dataset["Y"])

    if add_geometry:

        if not add_latlon:
            raise Exception("add_latlon must set to True in order to have add_geometry ...")

        dataset = GeoDataFrame(
            dataset, 
            geometry=points_from_xy(
                dataset['lon'], 
                dataset['lat'])
        )

    return dataset


def data_conversions(predictor_data: dict, proc_predictors_cfg: dict) -> dict:
    """Data conversion

    Args:
        predictor_data (dict): data to be processed

    Returns:
        dict: processed data
    """
    for proc_predictor_name in proc_predictors_cfg:

        predictor_data = predictor_data[
            predictor_data[proc_predictor_name] != PREDICTORS_CFG[
                proc_predictor_name]["invalid_value"]]

        if PREDICTORS_CFG[proc_predictor_name]["convert"] is not None:
            for convert_key in PREDICTORS_CFG[proc_predictor_name]["convert"]:
                predictor_data[proc_predictor_name] = predictor_data[proc_predictor_name].replace(
                    [convert_key], 
                    PREDICTORS_CFG[proc_predictor_name]["convert"][convert_key])

    return predictor_data