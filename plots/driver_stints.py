import fastf1 as ff1
import matplotlib.pyplot as plt
import io
import base64
import os
from .utils import setup_cache


def plot_driver_stints(year, weekend, session_type):
    ff1.Cache.enable_cache(setup_cache())
    race = ff1.get_session(year, weekend, session_type)
    race.load()

    driver_stints = (
        race.laps[["Driver", "Stint", "Compound", "LapNumber"]]
        .groupby(["Driver", "Stint", "Compound"])
        .count()
        .reset_index()
    )

    driver_stints = driver_stints.rename(columns={"LapNumber": "StintLength"})
    driver_stints = driver_stints.sort_values(by=["Stint"])

    compound_colors = {
        "SOFT": "#FF3333",
        "MEDIUM": "#FFF200",
        "HARD": "#EBEBEB",
        "INTERMEDIATE": "#39B54A",
        "WET": "#00AEEF",
    }

    # Create figure with transparent background
    plt.figure(figsize=(15, 10), facecolor="none")

    # Set style with transparent background
    plt.rcParams["figure.autolayout"] = True

    # Create the plot
    fig, ax = plt.subplots(facecolor="none")
    ax.patch.set_alpha(1)  # Keep axes background white

    # Set text colors to #333333
    plt.rcParams["text.color"] = "#333333"
    plt.rcParams["axes.labelcolor"] = "#333333"
    plt.rcParams["axes.edgecolor"] = "#333333"
    plt.rcParams["xtick.color"] = "#333333"
    plt.rcParams["ytick.color"] = "#333333"

    for driver in race.results["Abbreviation"]:
        stints = driver_stints.loc[driver_stints["Driver"] == driver]
        previous_stint_end = 0
        for _, stint in stints.iterrows():
            plt.barh(
                [driver],
                stint["StintLength"],
                left=previous_stint_end,
                color=compound_colors[stint["Compound"]],
                edgecolor="black",
            )
            previous_stint_end = previous_stint_end + stint["StintLength"]

    plt.title(f"Race strategy - {race}", color="#333333", pad=15)
    plt.xlabel("Lap", color="#333333")
    ax.invert_yaxis()
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)

    # Save with transparent background
    img = io.BytesIO()
    plt.savefig(
        img,
        format="png",
        dpi=200,
        facecolor="none",
        edgecolor="none",
        transparent=True,
    )
    img.seek(0)
    plt.close()

    base64_img = base64.b64encode(img.getvalue()).decode("utf8")
    return f"data:image/png;base64,{base64_img}"
