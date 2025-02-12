import fastf1 as ff1
from fastf1 import plotting
import matplotlib.pyplot as plt
import io
import base64
from .utils import setup_cache, get_plot_cache


def plot_driver_style(year, weekend, session_type, driver="VER"):
    img = None
    try:
        # Set up FastF1 cache
        ff1.Cache.enable_cache(setup_cache())
        
        # Get plot cache
        plot_cache = get_plot_cache()
        if plot_cache:
            try:
                cache_key = f"style_plot_{year}_{weekend}_{session_type}_{driver}"
                cached_plot = plot_cache.get(cache_key)
                if cached_plot:
                    return cached_plot
            except Exception as e:
                print(f"Redis cache error: {str(e)}")
                plot_cache = None

        # Generate plot if not cached
        session = ff1.get_session(year, weekend, session_type)
        session.load()

        fig, ax = plt.subplots(figsize=(10, 6))

        # Get driver's laps
        driver_laps = session.laps.pick_driver(driver)
        
        # Plot lap times
        ax.plot(
            range(len(driver_laps['LapTime'])),
            driver_laps['LapTime'].dt.total_seconds(),
            label=driver,
            marker='o'
        )

        # Add compound information
        compounds = driver_laps['Compound'].unique()
        for compound in compounds:
            compound_laps = driver_laps[driver_laps['Compound'] == compound]
            ax.scatter(
                range(len(compound_laps['LapTime'])), 
                compound_laps['LapTime'].dt.total_seconds(),
                label=f'{compound} tires',
                marker='s'
            )

        ax.set_xlabel("Lap Number")
        ax.set_ylabel("Lap Time (seconds)")
        ax.set_title(f"{driver} Driving Style Analysis - {session.event.year} {session.event.name}")
        ax.legend()
        ax.grid(True)

        img = io.BytesIO()
        plt.savefig(img, format='png', dpi=300, bbox_inches='tight')
        img.seek(0)
        
        plot_data = f"data:image/png;base64,{base64.b64encode(img.getvalue()).decode('utf8')}"
        
        # Cache the plot in Redis if available
        if plot_cache:
            try:
                plot_cache.setex(cache_key, 3600, plot_data)
            except Exception as e:
                print(f"Redis cache set error: {str(e)}")
            
        return plot_data
    except Exception as e:
        print(f"Error in plot_driver_style: {str(e)}")
        raise
    finally:
        if plt is not None:
            plt.close('all')
        if img is not None:
            img.close()
