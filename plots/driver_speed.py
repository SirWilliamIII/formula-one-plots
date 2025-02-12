import fastf1 as ff1
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection
import io
import base64
from .utils import setup_cache, get_plot_cache
import os
import redis


def plot_driver_speed(year, weekend, session_type, driver="VER"):
    # Set up FastF1 cache
    ff1.Cache.enable_cache(setup_cache())
    
    # Get plot cache
    plot_cache = get_plot_cache()
    cache_key = f"speed_plot_{year}_{weekend}_{session_type}_{driver}"
    
    # Check Redis cache first
    if plot_cache:
        cached_plot = plot_cache.get(cache_key)
        if cached_plot:
            return cached_plot.decode('utf-8')
    
    # Generate plot if not cached
    session = ff1.get_session(year, weekend, session_type)
    session.load()
    lap = session.laps.pick_drivers(driver).pick_fastest()

    x = lap.telemetry["X"]
    y = lap.telemetry["Y"]
    speed = lap.telemetry["Speed"]
    colormap = mpl.cm.plasma

    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)

    # Create figure with transparent background and adjusted layout
    fig = plt.figure(figsize=(15, 8), facecolor="none")  # Reduced height

    # Create main axis for track with specific position to leave room for title
    ax = fig.add_axes([0.1, 0.15, 0.8, 0.75])  # [left, bottom, width, height]
    ax.patch.set_alpha(1)  # Keep axes background white

    # Set text colors to #333333
    plt.rcParams["text.color"] = "#333333"
    plt.rcParams["axes.labelcolor"] = "#333333"
    plt.rcParams["axes.edgecolor"] = "#333333"
    plt.rcParams["xtick.color"] = "#333333"
    plt.rcParams["ytick.color"] = "#333333"

    # Format title with adjusted position
    title = f"Track Speed Analysis {session.event['OfficialEventName']}: {driver}"
    fig.suptitle(title, size=20, y=0.98, color="#333333")
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

    # Create a color bar as a legend with adjusted position
    cbaxes = fig.add_axes(
        [0.25, 0.12, 0.5, 0.03]
    )  # Increased y-position from 0.05 to 0.12
    normlegend = mpl.colors.Normalize(vmin=speed.min(), vmax=speed.max())
    legend = mpl.colorbar.ColorbarBase(
        cbaxes, norm=normlegend, cmap=colormap, orientation="horizontal"
    )
    legend.set_label("Speed (km/h)", color="#333333", size=10, labelpad=8)
    legend.ax.tick_params(labelsize=9, color="#333333")  # Adjust tick label size

    # Save with transparent background
    img = io.BytesIO()
    plt.savefig(
        img, format="png", dpi=300, facecolor="none", edgecolor="none", transparent=True
    )
    img.seek(0)
    plt.close()

    plot_data = f"data:image/png;base64,{base64.b64encode(img.getvalue()).decode('utf8')}"
    
    # Cache the plot in Redis if available
    if plot_cache:
        plot_cache.setex(cache_key, 3600, plot_data)  # Cache for 1 hour
        
    return plot_data


def get_driver_speed_plot(year, grand_prix, session_name):
    cache = setup_cache()
    cache_key = f"speed_plot_{year}_{grand_prix}_{session_name}"
    
    # If using Redis
    if isinstance(cache, redis.Redis):
        cached_plot = cache.get(cache_key)
        if cached_plot:
            return cached_plot
        
        # Generate plot...
        # Save to Redis
        cache.setex(cache_key, 3600, plot_data)  # Cache for 1 hour
    else:
        # Your existing file-based caching logic
        cache_file = os.path.join(cache, cache_key)
        if os.path.exists(cache_file):
            return load_from_file(cache_file)
            
        # Generate plot...
        # Save to file
