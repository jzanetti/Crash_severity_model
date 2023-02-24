from os.path import join
from pickle import dump as pickle_dump

from pandas import DataFrame
from sklearn.ensemble import StackingRegressor
from sklearn.linear_model import SGDRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPRegressor
from xgboost import XGBRegressor

from process import MODEL_CFGS
from process.utils import data_conversions



def get_data_for_training(dataset: DataFrame, cfg: dict) -> dict:
    """Get data to be trained with

    Args:
        dataset (DataFrame): raw CAS data
        cfg: model training configuration

    Returns:
        dict: the data to be used
    """
    data_to_use = {}

    proc_target_cfg = cfg["target"]
    proc_predictors_cfg = cfg["predictors"]

    print(f"Dropping NaN values ...")
    proc_dataset = dataset.dropna(
        subset=list(
            proc_predictors_cfg + 
            [proc_target_cfg["name"]]))

    print("Check state highway ...")
    if cfg["state_highway"]:
        proc_dataset = proc_dataset[
            proc_dataset["crashSHDescription"] == "Yes"]
    else:
        proc_dataset = proc_dataset[
            proc_dataset["crashSHDescription"] == "No"]

    print(f"Converting target data ...")
    for proc_target_key in proc_target_cfg["score"]:
        proc_dataset[proc_target_cfg["name"]] = proc_dataset[
            proc_target_cfg["name"]].replace(
                [proc_target_key], 
                proc_target_cfg["score"][proc_target_key]
            )

    print(f"Converting predictors ...")
    proc_dataset = data_conversions(
        proc_dataset, proc_predictors_cfg)


    data_to_use = {
        "train": proc_dataset[proc_predictors_cfg],
        "target": proc_dataset[[proc_target_cfg["name"]]]
    }

    return data_to_use


def model_train(cfg: dict, workdir: str, data_to_use: dict, n_jobs: int = 4, verbose: int = 100):
    """model training

    Args:
        cfg (dict): configuration
        workdir (str): working directory
        data_to_use (dict): data to be trained
        n_jobs (int, optional): cpu to be used. Defaults to 4.
        verbose (int, optional): debug level. Defaults to 100.
    """

    def _get_data_scaler(training_data: DataFrame):
        """Get data scaler

        Args:
            training_data (DataFrame): the base data to 
                be used for setting up data scaler

        Returns:
            _type_: _description_
        """
        scaler = StandardScaler()
        scaler.fit(training_data)
        return scaler

    scaler = _get_data_scaler(data_to_use["train"])

    if cfg["model_type"] in ["xgb", "stack"]:
        xgb_model = XGBRegressor(
            n_estimators=MODEL_CFGS["xgb"]["n_estimators"], 
            max_depth=MODEL_CFGS["xgb"]["max_depth"], 
            learning_rate=MODEL_CFGS["xgb"]["learning_rate"], 
            objective=MODEL_CFGS["xgb"]["objective"])

        if cfg["model_type"] == "xgb":
            final_model = xgb_model


    if cfg["model_type"] in ["knb", "stack"]:
        knb_model = KNeighborsRegressor(
            MODEL_CFGS["knb"]["n_neighbors"])

        if cfg["model_type"] == "knb":
            final_model = knb_model

    if cfg["model_type"] in ["sgd", "stack"]:
        sgd_model = SGDRegressor(
            max_iter=MODEL_CFGS["sgd"]["max_iter"], 
            tol=MODEL_CFGS["sgd"]["tol"])

        if cfg["model_type"] == "sgd":
            final_model = sgd_model

    if cfg["model_type"] in ["mlp", "stack"]:
        mlp_model = MLPRegressor(
            hidden_layer_sizes=1000)

        if cfg["model_type"] == "mlp":
            final_model = mlp_model


    if cfg["model_type"] == "stack":
        final_model = StackingRegressor(
            estimators=[
                # ("xgb", xgb_model),
                # ("kng", knb_model),
                ("mpl", mlp_model)
            ],
            final_estimator = sgd_model,
            verbose=verbose,
            n_jobs=n_jobs
        )

    training_data = scaler.transform(data_to_use["train"]) 

    print("start model fitting ...")
    final_model.fit(training_data, data_to_use["target"])

    print("Saving model ...")
    pickle_dump(
        {
            "model": final_model,
            "scaler": scaler
        },
        open(
            join(workdir, f"trained_{cfg['model_name']}.model"), 
            "wb"
        )
    )