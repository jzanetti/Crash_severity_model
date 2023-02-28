import matplotlib.pyplot as plt
import contextily as cx
from geopandas import GeoDataFrame
from os.path import join
from process import CAS_VIS
from pandas.plotting import table as pandas_plot_table
import matplotlib.ticker as ticker

def plot_total_crashes(
    workdir: str,
    cas_data: GeoDataFrame,
    cas_info: dict,
    cas_total_data):
    """Plot total crashes

    Args:
        workdir (str): working directory
        cas_data (GeoDataFrame): decoded CAS data
        cas_info (dict): CAS data meta information
        cas_total_data (_type_): processed CAS data with total crashes
    """
    ax = None
    legend_list = []
    legend_labels = []

    for crash_lvl in cas_info["crash_severity"]:

        print(f"Plotting {crash_lvl} ...")

        proc_cas_data = cas_data[cas_data["crashSeverity"] == crash_lvl]

        ax = proc_cas_data.plot(
            ax = ax,
            figsize=CAS_VIS["figsize"],
            markersize=CAS_VIS["scatter_cfg"][crash_lvl]["size"],
            color=CAS_VIS["scatter_cfg"][crash_lvl]["color"],
            legend=True,
            alpha=0.15)

        legend_list.append(
            plt.scatter(
                [],
                [], 
                s=CAS_VIS["scatter_cfg"][crash_lvl]["size"], 
                color=CAS_VIS["scatter_cfg"][crash_lvl]["color"]))
        
        legend_labels.append(crash_lvl)

    # Add the markers to the legend
    ax.legend(legend_list, legend_labels, title="", loc='center left', bbox_to_anchor=(1, 0.5))

    ax.set_title(f"Total crashes between {cas_info['start_year']} and {cas_info['end_year']}")

    n = 5
    i = n
    while i < len(cas_info['regions']):
        cas_info['regions'].insert(i, '\n')
        i += (5+1)

    cas_info = f'''Regions: {', '.join(cas_info['regions'])}
    Crash severity: {', '.join(cas_info['crash_severity'])}
    Vehicle types: {', '.join(cas_info['vehicle_types'])}'''

    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    plt.text(0.05, 0.95, cas_info, transform=ax.transAxes, va='top', bbox=props, fontsize=9.0)

    print("Adding basemap ...")
    cx.add_basemap(
        ax, 
        crs="epsg:4326", 
        source=cx.providers.OpenStreetMap.Mapnik, 
        attribution_size=1)

    plt.setp(ax.get_xticklabels(), visible=False)
    plt.setp(ax.get_yticklabels(), visible=False)

    plt.subplots_adjust(hspace=0.75)
    top10_locations = cas_total_data.sort_values('total', ascending=False)[0:10][[
            "region", "crashLocation1", "crashLocation2", "total"]]
    top10_locations = top10_locations.reset_index(drop=True)
    pandas_plot_table(ax, top10_locations,  loc="bottom", fontsize=3.0)

    print("Saving Figure ...")
    plt.savefig(
        join(workdir, "total_crashes.png"),
        bbox_inches='tight'
    )
    plt.close()


def plot_risk(
    workdir: str, 
    pred: dict, 
    base_data: dict, 
    vis_cfg: dict, 
    figsize: tuple = (15, 15)):
    """Plot risk map

    Args:
        workdir (str): working directory
        pred (dict): prediction
        base_data (dict): base data to be applied
        vis_cfg (dict): visualization configuration
        figsize (tuple, optional): figure size to be used. Defaults to (15, 15).
    """
    for proc_road_cluster in pred:

        for policy_name in pred[proc_road_cluster]:
            
            if policy_name == "base":
                continue
            
            if vis_cfg["clim"] is None:
                data_lim = max(
                    [abs(pred[proc_road_cluster][policy_name]["risk_change"].min()), 
                     abs(pred[proc_road_cluster][policy_name]["risk_change"].max())]
                )
                clim_min = -data_lim * 0.75
                clim_max = data_lim * 0.75
                clim_max = None
                clim_min = None
            else:
                clim_min = vis_cfg["clim"]["min"]
                clim_max = vis_cfg["clim"]["max"]

            ax = pred[proc_road_cluster][policy_name].plot(
                column="risk_change", 
                markersize=30, 
                figsize=figsize, 
                cmap=vis_cfg["cmap"],
                vmin=clim_min, 
                vmax=clim_max)

            title_str = f"Risk change: {policy_name}"
            if title_str is not None:
                ax.set_title(title_str)

            cbar_ax = ax.figure.add_axes(vis_cfg["colorbar_cfg"]["axs"])
            
            ax.figure.colorbar(
                ax.collections[0], 
                orientation=vis_cfg["colorbar_cfg"]["orientation"],
                cax=cbar_ax,
                format=ticker.PercentFormatter(xmax=1, decimals=1))

            cx.add_basemap(
                ax, 
                crs=base_data["roadline"].crs.to_string(), 
                source=cx.providers.OpenStreetMap.Mapnik , 
                attribution_size=1)

            plt.savefig(
                join(workdir, f"{proc_road_cluster}_{policy_name}.png"),
                bbox_inches="tight"
            )
            plt.close()