import fastf1 as ff1
from fastf1 import plotting
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
from .utils import setup_cache


def plot_tire_analysis(wknd):
    ff1.Cache.enable_cache(setup_cache())
    session = ff1.get_session(2024, wknd, "R")
    session.load()

    laps = session.laps.copy()
    laps["LapTimeSeconds"] = laps["LapTime"].dt.total_seconds()
    laps["FastestStintLap"] = laps.groupby(["Driver", "Stint"])[
        "LapTimeSeconds"
    ].transform("min")
    laps["DegDelta"] = laps["LapTimeSeconds"] - laps["FastestStintLap"]

    driver_degradation = (
        laps.groupby("Driver")["DegDelta"]
        .mean()
        .reset_index()
        .rename(columns={"DegDelta": "AvgDeg"})
    )

    driver_degradation.sort_values("AvgDeg", inplace=True)

    # Create figure with transparent background
    plt.figure(figsize=(10, 6), facecolor="none")

    # Set style with transparent background
    sns.set_style("whitegrid", {"axes.facecolor": "white"})

    # Create the plot
    ax = sns.barplot(
        data=driver_degradation,
        x="Driver",
        y="AvgDeg",
        hue="Driver",
        legend=False,
        palette="RdYlGn_r",
    )

    # Set the figure and axes backgrounds transparent
    ax.figure.patch.set_alpha(0)
    ax.patch.set_alpha(1)  # Keep axes background white

    plt.title(
        "Which Drivers Managed Their Tires Best? (Lower Degradation = Better)",
        fontsize=14,
        pad=15,
    )
    plt.xlabel("Driver", fontsize=12)
    plt.ylabel("Avg Tire Degradation (s)", fontsize=12)

    for index, row in driver_degradation.iterrows():
        plt.text(
            x=index,
            y=row["AvgDeg"] + 0.01,
            s=f"{row['AvgDeg']:.2f}",
            ha="center",
            va="bottom",
            fontsize=9,
            color="black",
        )

    # Save with transparent background
    img = io.BytesIO()
    plt.savefig(
        img,
        format="png",
        dpi=150,
        bbox_inches="tight",
        facecolor="none",
        edgecolor="none",
        transparent=True,
    )
    img.seek(0)
    plt.close()

    return f"data:image/png;base64,{base64.b64encode(img.getvalue()).decode('utf8')}"
