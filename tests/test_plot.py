import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import matplotlib.pyplot as plt
import fastf1 as ff1
import seaborn as sns
from plots.utils import setup_cache


def test_tire_analysis(wknd=1):  # Default to Bahrain GP
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

    plt.figure(figsize=(10, 6))
    sns.set_style("whitegrid")

    sns.barplot(
        data=driver_degradation,
        x="Driver",
        y="AvgDeg",
        hue="Driver",
        legend=False,
        palette="RdYlGn_r",
    )

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
    test_tire_analysis()  # Test with Bahrain GP
    # test_tire_analysis(2)  # Or test with Saudi Arabian GP
