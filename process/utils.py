from process import PREDICTORS_CFG, CAS_DATASET, CAS_PROJECTION, CAS_VEHICLE_TYPES
from yaml import safe_load
from pandas import DataFrame, read_csv
from pyproj import Proj, transform
from geopandas import GeoDataFrame, points_from_xy
from scipy.stats import gaussian_kde
from numpy import vstack, mgrid

def get_cas_meta(cas_data: GeoDataFrame, years: list or None, regions: list, crash_severity: list, vehicle_types: list):
    """Get Total crash meta information

    Args:
        cas_data (GeoDataFrame): _description_
        regions (list): _description_
        crash_severity (list): _description_
        vehicle_types (list): _description_

    Returns:
        _type_: _description_
    """

    if years is None:
        start_year = min(cas_data.crashYear)
        end_year = max(cas_data.crashYear)
    else:
        years = [int(i) for i in years]
        start_year = min(years)
        end_year = max(years)

    return {
        "start_year": start_year,
        "end_year": end_year,
        "regions": regions,
        "crash_severity": crash_severity,
        "vehicle_types": vehicle_types
    }


def cas_filter(cas_data: DataFrame, filter_key: str, filer_values: list) -> DataFrame:
    """Porcess CAS based on the different conditions

    Args:
        cas_data (DataFrame): CAS data
        regions (list): regions to be kept

    Returns:
        DataFrame: filtered data
    """

    if filter_key == "vehicle_types":
        for i, proc_filter_value in enumerate(filer_values):
            if i == 0:
                proc_cas_data = cas_data[cas_data[proc_filter_value] > 0]
            else:
                proc_cas_data.append(cas_data[cas_data[proc_filter_value] > 0])
            
    else:

        all_filter_values = filer_values

        if filter_key == "region":
            all_filter_values = []
            for proc_region in filer_values:
                all_filter_values.append(proc_region + " Region")
    
        proc_cas_data = cas_data[cas_data[filter_key].isin(
            all_filter_values)]

    return proc_cas_data


def get_total_cas(cas_data: DataFrame) -> DataFrame:
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
        ["region", "crashLocation1", "crashLocation2"], 
        as_index=False).agg(agg_operator)
    df["total"]= df[CAS_VEHICLE_TYPES].sum(axis=1)

    df = GeoDataFrame(
        df, 
        geometry=points_from_xy(
            df['lon'], 
            df['lat'])
    )

    df = df.set_crs(epsg=4326)

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


def read_cas(add_geometry: bool = False, get_density: bool = False) -> DataFrame:
    """Read CAS dataset

       Args:
        add_latlon (bool): if add lat and lon in the dataset
    """
    dataset = read_csv(CAS_DATASET)

    dataset["region"] = dataset["region"].replace(
        ["Manawatū-Whanganui Region"], 
        "Manawatu-Whanganui Region")

    dataset["lon"], dataset["lat"] = transform(
        Proj(init=CAS_PROJECTION), 
        Proj(init='epsg:4326'),
        dataset["X"], 
        dataset["Y"])

    dataset['lon'] = dataset['lon'] % 360.0
    dataset = dataset[dataset['lon'] < 180.0]

    for loc_key in ["crashLocation1", "crashLocation2"]:
        dataset[loc_key] = dataset[loc_key].replace(
            {
                " STREET": " ST",
                " ROAD": " RD"
            }, regex=True)

    if add_geometry:

        dataset = GeoDataFrame(
            dataset, 
            geometry=points_from_xy(
                dataset['lon'], 
                dataset['lat'])
        )

    if get_density:

        x = dataset.geometry.x
        y = dataset.geometry.y
        coords = vstack([x, y])

        kde = gaussian_kde(coords)

        xmin, ymin, xmax, ymax = dataset.total_bounds
        xgrid, ygrid = mgrid[xmin:xmax:100j, ymin:ymax:100j]
        density_surface = kde(vstack([xgrid.ravel(), ygrid.ravel()]))

        dataset = GeoDataFrame(
            {
                "density": density_surface.ravel(),
                "geometry": points_from_xy(xgrid.ravel(), ygrid.ravel())
            }
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