import fastf1 as ff1
from fastf1 import plotting
import matplotlib.pyplot as plt
import io
import base64
from .utils import setup_cache, get_plot_cache


def plot_driver_style(year, weekend, session_type, driver="VER"):
    # Set up FastF1 cache
    ff1.Cache.enable_cache(setup_cache())
    
    # Get plot cache
    plot_cache = get_plot_cache()
    cache_key = f"style_plot_{year}_{weekend}_{session_type}_{driver}"
    
    # Check Redis cache first
    if plot_cache:
        cached_plot = plot_cache.get(cache_key)
        if cached_plot:
            return cached_plot.decode('utf-8')

    # Generate plot if not cached
    session = ff1.get_session(year, weekend, session_type)
    session.load()

    fig, ax = plt.subplots(figsize=(8, 6))

    laps = session.laps.pick_drivers(driver).pick_quicklaps().reset_index()
    style = plotting.get_driver_style(
        identifier=driver, style=["color", "linestyle"], session=session
    )
    ax.plot(laps["LapTime"], **style, label=driver)

    ax.set_xlabel("Lap Number")
    ax.set_ylabel("Lap Time")
    ax.legend()
    plt.title(f"{session.event.year} {session.event.name} Driver Comparison")

    img = io.BytesIO()
    plt.savefig(img, format='png', dpi=300, bbox_inches='tight')
    img.seek(0)
    plt.close()

    plot_data = f"data:image/png;base64,{base64.b64encode(img.getvalue()).decode('utf8')}"
    
    # Cache the plot in Redis if available
    if plot_cache:
        plot_cache.setex(cache_key, 3600, plot_data)  # Cache for 1 hour
        
    return plot_data
