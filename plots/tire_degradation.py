import fastf1 as ff1
from fastf1 import plotting
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
from .utils import setup_cache


def plot_tire_deg(year, weekend, session_type):
    plotting.setup_mpl(misc_mpl_mods=False, color_scheme="fastf1")
    ff1.Cache.enable_cache(setup_cache())
    session = ff1.get_session(year, weekend, session_type)
    session.load()

    laps = session.laps.copy()
    laps["LapTimeSeconds"] = laps["LapTime"].dt.total_seconds()
    laps["FastestStintLap"] = laps.groupby(["Driver", "Stint"])[
        "LapTimeSeconds"
    ].transform("min")
    laps["DegDelta"] = laps["LapTimeSeconds"] - laps["FastestStintLap"]

    g = sns.FacetGrid(laps, col="Driver", col_wrap=4, sharey=False, height=3)
    g.map_dataframe(sns.lineplot, x="TyreLife", y="DegDelta")
    g.set_axis_labels("Tire Life (laps)", "Degradation (s)")
    g.set_titles(col_template="{col_name}")
    plt.subplots_adjust(top=0.9)
    g.fig.suptitle("Tire Degradation Curves by Driver", y=1.02)

    img = io.BytesIO()
    plt.savefig(img, format="png", bbox_inches="tight")
    img.seek(0)
    plt.close()
    base64_img = base64.b64encode(img.getvalue()).decode("utf8")
    return f"data:image/png;base64,{base64_img}"
