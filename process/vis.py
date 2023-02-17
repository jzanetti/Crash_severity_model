import matplotlib.pyplot as plt
import contextily as cx
from geopandas import GeoDataFrame, sjoin_nearest
from os.path import join
from process import CAS_VIS
from pandas.plotting import table as pandas_plot_table

def plot_total_crashes(
    workdir: str,
    cas_data: GeoDataFrame,
    cas_info: dict,
    cas_total_data):

    """
    cas_total_data_line = sjoin_nearest(
        base_data["roadline"], 
        proc_cas_data[["geometry", "total"]], 
        max_distance=0.0001)[["total", "geometry"]]
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


def plot_map(
    workdir: str, 
    pred: dict, 
    base_data: dict, 
    vis_cfg: dict, 
    cas_data: dict = None,
    cas_total_data: dict = None,
    figsize: tuple = (15, 15), 
    cmap: str = "jet",
    display_risk_as_line: bool = True):


    def _get_latlon_range(data_input: GeoDataFrame) -> dict:
        """Get lat and lon limits

        Args:
            data_input (GeoDataFrame): a geodataframe data

        Returns:
            dict: the dict contains lat and lon limits
        """
        lon_range = (
            data_input["lon"].min(), 
            data_input["lon"].max())
        lat_range = (
            data_input["lat"].min(), 
            data_input["lat"].max())
        
        return {"lat": lat_range, "lon": lon_range}


    for proc_area in pred:

        latlon = _get_latlon_range(pred[proc_area]["base"])

        if vis_cfg["cas"]["enable"]:

            proc_cas_data = cas_data.query(
                f"{latlon['lat'][0]} < lat < {latlon['lat'][1]} & " +
                f"{latlon['lon'][0]} < lon < {latlon['lon'][1]}"
            )

            ax = None
            for crash_lvl in vis_cfg["cas"]["crash_lvl"]:
                
                if vis_cfg["cas"]["crash_lvl"][crash_lvl] is None:
                    continue

                proc_cas_data2 = proc_cas_data[proc_cas_data["crashSeverity"] == crash_lvl]

                ax = proc_cas_data2.plot(
                    ax = ax,
                    markersize=vis_cfg["cas"]["crash_lvl"][crash_lvl]["size"],
                    figsize=figsize, 
                    color=vis_cfg["cas"]["crash_lvl"][crash_lvl]["color"],
                    legend=True,
                    alpha=0.2)

            cx.add_basemap(
                ax, 
                crs=base_data["roadline"].crs.to_string(), 
                source=cx.providers.OpenStreetMap.DE, 
                attribution_size=1)
            plt.savefig(
                join(workdir, f"{proc_area}_crashes.png")
            )
            plt.close()

        for policy_name in pred[proc_area]:

            if display_risk_as_line:
                pred[proc_area][policy_name] = sjoin_nearest(
                    cas_total_data["line"], 
                    pred[proc_area][policy_name][["risk", "geometry", "lat", "lon"]], 
                    max_distance=0.001)

            ax = pred[proc_area][policy_name].plot(
                column="risk", 
                markersize=5, 
                figsize=figsize, 
                legend=True, 
                cmap=cmap)

            cx.add_basemap(
                ax, 
                crs=base_data["roadline"].crs.to_string(), 
                source=cx.providers.OpenStreetMap.DE, 
                attribution_size=1)
            plt.savefig(
                join(workdir, f"{proc_area}_{policy_name}.png")
            )
            plt.close()