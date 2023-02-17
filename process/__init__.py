


CAS_DATASET = "etc/data/cas.csv"
CAS_PROJECTION = "EPSG:2193"
CAS_VEHICLE_TYPES = ["bicycle", "bus", "schoolBus", "carStationWagon", "moped", "motorcycle", "suv", "taxi", "truck", "vanOrUtility", "vehicle"]
CAS_REGIONS = [
    'Auckland', 'Bay of Plenty', 'Canterbury',
    'Gisborne', "Hawke's Bay",
    'Manawatu-Whanganui', 'Marlborough', 'Nelson',
    'Northland Region', 'Otago Region', 'Southland',
    'Taranaki', 'Tasman', 'Waikato',
    'Wellington', 'West Coast']
CAS_CRASH_SEVERITY = ["Non-Injury Crash", "Minor Crash", "Serious Crash", "Fatal Crash"]
CAS_VIS = {
    "figsize": (25, 15),
    "scatter_cfg": {
        "Non-Injury Crash": {
            "color": "k",
            "size": 10},
        "Minor Crash": {
            "color": "g",
            "size": 30
        },
        "Serious Crash": {
            "color": "b",
            "size": 100
        },
        "Fatal Crash": {
            "color": "r",
            "size": 300
        }
    }
}




#NSLR_DATASET  = "etc/data/road_speedlimit/National_Speed_Limit_Register_(NSLR).shp"
#ROADLINE_DATASET = "etc/data/road_centreline/nz-road-centrelines-topo-150k.shp"
#ROAD_SLOPE = "etc/data/road_slope/nzenvds-slope-degrees-v10.tif"


PREDICTORS_CFG = {
    "lat": {"convert": None, "invalid_value": None},
    "lon": {"convert": None, "invalid_value": None}, 
    "speedLimit": {"convert": None, "invalid_value": None},
    "NumberOfLanes": {"convert": None, "invalid_value": None},
    "crashSHDescription": {"convert": {"No": 0.0, "Yes": 1.0}, "invalid_value": "Unknown"},
    "flatHill": {"convert": {"Flat": 0.0, "Hill Road": 1.0}, "invalid_value": "Null"},
    "weatherA": {"convert": {"Fine": 0.0, "Light rain": 1.0, "Mist or Fog": 3.0, "Heavy rain": 3.0, "Hail or Sleet": 3.0, "Snow": 3.0}, "invalid_value": "Null"},
    "light": {"convert": {"Bright sun": 0.0, "Overcast": 1.0, "Twilight": 2.0, "Dark": 3.0}, "invalid_value": "Unknown"}, 
    "roadSurface": {"convert": {"End of seal": 0.0, "Unsealed": 1.0, "Sealed": 2.0}, "invalid_value": "Null"}
}

MODEL_CFGS = {
    "xgb": {
        "n_estimators": 200,
        "max_depth": 9,
        "learning_rate": 0.1,
        "objective": "reg:squarederror"
    },
    "knb": {
        "n_neighbors": 9
    },
    "sgd": {
        "max_iter": 1000, 
        "tol": 1e-3
    }
}