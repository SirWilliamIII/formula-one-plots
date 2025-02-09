import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import matplotlib.pyplot as plt
import fastf1 as ff1
import seaborn as sns
from plots.utils import setup_cache


def plot_tire_analysis(wknd=3):

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

    plt.tight_layout()
    plt.show()  # This will display the plot directly


if __name__ == "__main__":
    plot_tire_analysis()  # Test with Bahrain GP
