"""
Usage: crash_total --workdir <WORKING DIRECTORY>
                   [--regions <REGIONS>]
                   [--crash_severity <CRASH SEVERITY TYPES>]
                   [--vehicle_types <VEHICLE TYPES>]
                   [--years <CRASH YEARS>]

Author: Sijin Zhang

Description: 
    This is a wrapper to plot all crashes on a map

"""

import argparse
from os.path import exists, join
from os import makedirs
from process import CAS_REGIONS, CAS_CRASH_SEVERITY, CAS_VEHICLE_TYPES
from process.utils import get_cas_meta, read_cas, get_total_cas, cas_filter
from process.vis import plot_total_crashes

def get_example_usage():
    example_text = """example:
        * crash_total --workdir /tmp/rfm
                      [--regions Auckland, Wellington]
                      [--crash_severity 'Minor Crash', 'Serious Crash', 'Fatal Crash']
                      [--vehicle_types truck, moped]
                      [--years 2017, 2018]
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
        "--regions", 
        nargs="+", 
        required=False,
        choices=CAS_REGIONS,
        default=CAS_REGIONS,
        help=f"regions to be plotted, "
            "choosing from {CAS_REGIONS}")

    parser.add_argument(
        "--crash_severity", 
        nargs="+", 
        required=False,
        choices=CAS_CRASH_SEVERITY,
        default=CAS_CRASH_SEVERITY,
        help=f"crash secerity to be plotted, "
            "choosing from {CAS_CRASH_SEVERITY}")

    parser.add_argument(
        "--vehicle_types", 
        nargs="+", 
        required=False,
        choices=CAS_VEHICLE_TYPES,
        default=CAS_VEHICLE_TYPES,
        help=f"vehicle types to be plotted, "
            "choosing from {CAS_VEHICLE_TYPES}")

    parser.add_argument(
        "--years", 
        nargs="+", 
        required=False,
        default=None,
        help="years to be analyzed")


    return parser.parse_args(
        #[
        #    "--workdir", "rfm",
        #    #"--regions", "Auckland", #"Auckland", "Wellington"
        #    #"--crash_severity", "Fatal Crash", # "Serious Crash", "Non-Injury Crash", "Minor Crash", "Serious Crash", "Fatal Crash",
        #    #"--vehicle_types", "bicycle",
        #    #"--years", "2010", "2020"
        #]
    )


def get_data():
    args = setup_parser()

    if not exists(args.workdir):
        makedirs(args.workdir)

    print("Reading CAS ...")
    cas_data = read_cas(add_geometry=True)
    cas_info = get_cas_meta(cas_data, args.years, args.regions, args.crash_severity, args.vehicle_types)

    cas_data = cas_filter(cas_data, "vehicle_types", args.vehicle_types) 
    cas_data = cas_filter(cas_data, "region", args.regions)
    cas_data = cas_filter(cas_data, "crashSeverity", args.crash_severity)
    if args.years is not None:
        cas_data = cas_filter(
            cas_data, "crashYear", [int(i) for i in args.years])

    cas_total_data = get_total_cas(cas_data)

    print("Plotting ...")
    plot_total_crashes(
        args.workdir,
        cas_data,
        cas_info,
        cas_total_data)

    print("Saving totals ...")
    cas_total_data.sort_values(
        "total", 
        ascending=False)[0:10][[
            "region", "crashLocation1", "crashLocation2", "total"]].to_csv(
            join(args.workdir, "top10_crash_locations.csv"), index=False)
    
    print("done")



if __name__ == "__main__":
    get_data()
