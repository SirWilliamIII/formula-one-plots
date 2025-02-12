import fastf1 as ff1
import matplotlib.pyplot as plt
import numpy as np
import io
import base64
from .utils import setup_cache, get_plot_cache


def plot_driver_stints(year, weekend, session_type, driver="VER"):
    img = None
    try:
        # Set up FastF1 cache
        ff1.Cache.enable_cache(setup_cache())
        
        # Get plot cache
        plot_cache = get_plot_cache()
        cache_key = f"stints_{year}_{weekend}_{session_type}_{driver}"
        
        # Check Redis cache first
        if plot_cache:
            cached_plot = plot_cache.get(cache_key)
            if cached_plot:
                return cached_plot.decode('utf-8')

        # Generate plot if not cached
        session = ff1.get_session(year, weekend, session_type)
        session.load()
        
        driver_stints = session.laps.pick_driver(driver).get_stints()
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        for idx, stint in driver_stints.iterlaps():
            ax.plot(stint['LapNumber'], 
                   stint['LapTime'].dt.total_seconds(),
                   marker='o',
                   label=f'Stint {idx+1} ({stint["Compound"].iloc[0]})')
        
        ax.set_xlabel('Lap Number')
        ax.set_ylabel('Lap Time (seconds)')
        ax.set_title(f'{driver} Stint Analysis - {session.event.year} {session.event.name}')
        ax.legend()
        
        img = io.BytesIO()
        plt.savefig(img, format='png', dpi=300, bbox_inches='tight')
        img.seek(0)
        
        plot_data = f"data:image/png;base64,{base64.b64encode(img.getvalue()).decode('utf8')}"
        
        # Cache the plot in Redis if available
        if plot_cache:
            plot_cache.setex(cache_key, 3600, plot_data)  # Cache for 1 hour
            
        return plot_data
    finally:
        # Clean up matplotlib resources
        plt.close('all')
        if img is not None:
            img.close()
