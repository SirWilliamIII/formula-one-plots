import fastf1 as ff1
from fastf1 import plotting
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
from .utils import setup_cache


def plot_laptimes_distribution(year, weekend, session_type):
    plotting.setup_mpl(
        mpl_timedelta_support=True, misc_mpl_mods=False, color_scheme="fastf1"
    )
    ff1.Cache.enable_cache(setup_cache())
    session = ff1.get_session(year, weekend, session_type)
    session.load()

    point_finishers = session.drivers[:10]
    driver_laps = session.laps.pick_drivers(point_finishers).pick_quicklaps()
    driver_laps = driver_laps.reset_index()

    finishing_order = [session.get_driver(i)["Abbreviation"] for i in point_finishers]

    fig, ax = plt.subplots(figsize=(10, 5))

    driver_laps["LapTime(s)"] = driver_laps["LapTime"].dt.total_seconds()

    sns.violinplot(
        data=driver_laps,
        x="Driver",
        y="LapTime(s)",
        hue="Driver",
        inner=None,
        density_norm="area",
        order=finishing_order,
        palette=plotting.get_driver_color_mapping(session=session),
    )

    sns.swarmplot(
        data=driver_laps,
        x="Driver",
        y="LapTime(s)",
        order=finishing_order,
        hue="Compound",
        palette=plotting.get_compound_mapping(session=session),
        hue_order=["SOFT", "MEDIUM", "HARD"],
        linewidth=0,
        size=4,
    )

    ax.set_xlabel("Driver")
    ax.set_ylabel("Lap Time (s)")
    plt.suptitle(f"{session.event.year} {session.event.name} Lap Time Distributions")
    sns.despine(left=True, bottom=True)

    plt.tight_layout()

    img = io.BytesIO()
    plt.savefig(img, format="png", bbox_inches="tight")
    img.seek(0)
    plt.close()
    base64_img = base64.b64encode(img.getvalue()).decode("utf8")
    return f"data:image/png;base64,{base64_img}"
