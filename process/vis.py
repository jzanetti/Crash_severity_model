import matplotlib.pyplot as plt
import contextily as cx
from geopandas import GeoDataFrame
from os.path import join

def plot_map(workdir: str, pred: dict, base_data: dict, vis_cfg: dict, cas_data: dict = None, figsize: tuple = (15, 15), cmap: str = "jet"):


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

        for policy_name in pred[proc_area]:

            if vis_cfg["cas_basemap"]["enable"]:

                latlon = _get_latlon_range(pred[proc_area][policy_name])
                proc_cas_data = cas_data.query(
                    f"{latlon['lat'][0]} < lat < {latlon['lat'][1]} & " +
                    f"{latlon['lon'][0]} < lon < {latlon['lon'][1]}"
                )
                proc_cas_data = proc_cas_data[proc_cas_data["crashSeverity"].isin(
                    vis_cfg["cas_basemap"]["crash_lvl"])]

            ax = pred[proc_area][policy_name].plot(
                column="risk", 
                markersize=3, 
                figsize=figsize, 
                legend=True, 
                cmap=cmap)

            if vis_cfg["cas_basemap"]["enable"]:

                latlon = _get_latlon_range(pred[proc_area][policy_name])

                proc_cas_data = cas_data.query(
                    f"{latlon['lat'][0]} < lat < {latlon['lat'][1]} & " +
                    f"{latlon['lon'][0]} < lon < {latlon['lon'][1]}"
                )

                proc_cas_data = proc_cas_data[proc_cas_data["crashSeverity"].isin(
                    vis_cfg["cas_basemap"]["crash_lvl"])]

                proc_cas_data.plot(
                    ax=ax, 
                    markersize=10, 
                    color="k", 
                    alpha=0.5)

            cx.add_basemap(
                ax, 
                crs=base_data["roadline"].crs.to_string(), 
                source=cx.providers.OpenStreetMap.DE, 
                attribution_size=1)
            plt.savefig(
                join(workdir, f"{proc_area}_{policy_name}.png")
            )
            plt.close()
