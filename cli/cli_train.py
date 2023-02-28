"""
Usage: cli_train --workdir /tmp/rfm --cfg train.cfg

Author: Sijin Zhang

Description: 
    This is a wrapper to get trained model for road_fatalities_model

"""

import argparse
from os.path import exists
from os import makedirs
from process.train import get_data_for_training, model_train
from process.utils import read_cfg, read_cas

def get_example_usage():
    example_text = """example:
        * cli_train --workdir /tmp/rfm
                    --cfg train.cfg
        """
    return example_text


def setup_parser():
    parser = argparse.ArgumentParser(
        description="Training the CAS data",
        epilog=get_example_usage(),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("--workdir", required=True, help="working directory")
    parser.add_argument("--cfg", required=True, help="configuration path")

    return parser.parse_args(
        # [
        #    "--workdir", "rfm",
        #    "--cfg", "etc/cfg/train/model_stack.yml"
        # ]
    )


def get_data():
    args = setup_parser()

    if not exists(args.workdir):
        makedirs(args.workdir)

    cfg = read_cfg(args.cfg)

    print("Read CAS data ...")
    data = read_cas()

    print("Obtain data for model training")
    data = get_data_for_training(data, cfg)

    print(f"Start training ...")
    model_train(cfg, args.workdir, data)

    print("done")


if __name__ == "__main__":
    get_data()
