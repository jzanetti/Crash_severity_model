"""
Usage: cli_predict
            --workdir /tmp/rfm

Author: Sijin Zhang

Description: 
    This is a wrapper to get build-in dataset from climadarisk

"""

import argparse
from os.path import exists
from os import makedirs
from process.utils import read_cfg, read_cas, get_total_cas
from process.predict import read_base_data, read_model, area_prediction, road_prediction
from process.vis import plot_risk

def get_example_usage():
    example_text = """example:
        * cli_predict --workdir /tmp/rfm
                      --cfg predict_cfg.yml
        """
    return example_text


def setup_parser():
    parser = argparse.ArgumentParser(
        description="Predicting the road risk",
        epilog=get_example_usage(),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--workdir", required=True, help="working directory")
    parser.add_argument(
        "--cfg", required=True, help="configuration path")

    return parser.parse_args(
        [
            "--workdir", "rfm",
            "--cfg", "etc/cfg/model_predict2.yml"
        ]
    )


def get_data():
    args = setup_parser()

    if not exists(args.workdir):
        makedirs(args.workdir)

    cfg = read_cfg(args.cfg)

    print("Reading base data (nslr, roadline and roadslope) ...")
    base_data = read_base_data(cfg["inputs"])

    print("Reading trained model ...")
    model = read_model(cfg["model_path"])

    print("Reading CAS ...")
    cas_data = None
    cas_total_data = None
    #if cfg["vis"]["cas"]["enable"]:
    #    cas_data = read_cas(add_geometry=True)
    #    cas_total_data = get_total_cas(cas_data)

    print("Start prediction ...")
    pred = {"area": {}, "raod": {}}
    try:
        for proc_area in cfg["areas"]:
            pred["area"][proc_area] = area_prediction(
                model, base_data, proc_area, cfg)
    except KeyError:
        pass
    
    try:
        for road_cluster_name in cfg["roads"]:
            pred["raod"][road_cluster_name] = road_prediction(
                model, base_data, road_cluster_name, cfg)
    except KeyError:
        pass

    print("Plotting ...")
    plot_risk(
        args.workdir, 
        pred["raod"], 
        base_data, 
        cfg["vis"],
        cas_data=cas_data,
        cas_total_data=cas_total_data, 
        figsize=(15, 15))

if __name__ == "__main__":
    get_data()
