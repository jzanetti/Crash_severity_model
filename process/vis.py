import matplotlib.pyplot as plt
import contextily as cx
from geopandas import GeoDataFrame, sjoin_nearest
from os.path import join


def plot_total_crashes(
    workdir: str,
    base_data: dict, 
    latlon_range: dict, 
    cas_total_data: dict = None,
    cas_data: GeoDataFrame = None,
    figsize: tuple = (15, 15)):

    proc_cas_data = cas_total_data.query(
        f'{latlon_range["lat"]["min"]} < lat < {latlon_range["lat"]["max"]} & ' + \
        f'{latlon_range["lon"]["min"]} < lon < {latlon_range["lon"]["max"]}'
    )

    cas_total_data_line = sjoin_nearest(
        base_data["roadline"], 
        proc_cas_data[["geometry", "total"]], 
        max_distance=0.0001)[["total", "geometry"]]


    ax = cas_total_data_line.plot(
        legend=True,
        markersize=proc_cas_data["total"],
        figsize=figsize, 
        alpha=0.5,
        cmap="jet")

    """
    cx.add_basemap(
        ax, 
        crs=cas_total_data.crs.to_string(), 
        source=cx.providers.OpenStreetMap.DE, 
        attribution_size=1)
    """
    proc_area = "test"
    plt.savefig(
        join(workdir, f"{proc_area}_total_crashes.png")
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