import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import fastf1 as ff1
import seaborn as sns
from plots.utils import setup_cache
from matplotlib.collections import LineCollection


def test_driver_speed(year=2024, wknd=1, ses="R", driver="VER"):
    ff1.Cache.enable_cache(setup_cache())
    session = ff1.get_session(year, wknd, ses)
    session.load()
    lap = session.laps.pick_drivers(driver).pick_fastest()
    
    
    x = lap.telemetry["X"]
    y = lap.telemetry["Y"]
    speed = lap.telemetry["Speed"]
    colormap = mpl.cm.plasma

    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)

    # Create figure with transparent background and adjusted layout
    fig = plt.figure(figsize=(15, 10), facecolor='none', constrained_layout=True)
    ax = fig.add_subplot(111)
    ax.patch.set_alpha(1)  # Keep axes background white
    
    # Set text colors to #333333
    plt.rcParams['text.color'] = '#333333'
    plt.rcParams['axes.labelcolor'] = '#333333'
    plt.rcParams['axes.edgecolor'] = '#333333'
    plt.rcParams['xtick.color'] = '#333333'
    plt.rcParams['ytick.color'] = '#333333'

    # Format title similar to Race Strategy plot
    title = f"Track Speed Analysis {session.event['OfficialEventName']}: {driver}"
    fig.suptitle(title, size=24, y=0.95, color='#333333')
    ax.axis("off")

    # Create background track line
    ax.plot(
        lap.telemetry["X"],
        lap.telemetry["Y"],
        color="#333333",
        linestyle="-",
        linewidth=16,
        zorder=0,
    )

    # Create a continuous norm to map from data points to colors
    norm = plt.Normalize(speed.min(), speed.max())
    lc = LineCollection(segments, cmap=colormap, norm=norm, linestyle="-", linewidth=5)

    # Set the values used for colormapping
    lc.set_array(speed)

    # Merge all line segments together
    line = ax.add_collection(lc)

    # Create a color bar as a legend with adjusted position and style
    cbaxes = fig.add_axes([0.25, 0.05, 0.5, 0.03])  # Made thinner
    normlegend = mpl.colors.Normalize(vmin=speed.min(), vmax=speed.max())
    legend = mpl.colorbar.ColorbarBase(
        cbaxes, 
        norm=normlegend, 
        cmap=colormap, 
        orientation="horizontal"
    )
    legend.set_label("Speed (km/h)", color='#333333', size=10, labelpad=8)
    legend.ax.tick_params(labelsize=9, color='#333333')  # Adjust tick label size

    plt.show()


if __name__ == "__main__":
    # Test with different parameters
    test_driver_speed()  # Default: 2024 Bahrain GP, VER
    # test_driver_speed(2024, 2, "R", "LEC")  # 2024 Saudi GP, LEC
    # test_driver_speed(2024, 3, "R", "HAM")  # 2024 Australian GP, HAM
