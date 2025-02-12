import fastf1 as ff1
import matplotlib.pyplot as plt
import numpy as np
import io
import base64
from .utils import setup_cache, get_plot_cache

def plot_lap_distribution(year, weekend, session_type, driver="VER"):
    try:
        # Set up FastF1 cache
        ff1.Cache.enable_cache(setup_cache())
        
        # Get plot cache
        plot_cache = get_plot_cache()
        cache_key = f"lap_dist_{year}_{weekend}_{session_type}_{driver}"
        
        # Check Redis cache first
        if plot_cache:
            cached_plot = plot_cache.get(cache_key)
            if cached_plot:
                return cached_plot.decode('utf-8')

        # Generate plot if not cached
        session = ff1.get_session(year, weekend, session_type)
        session.load()
        
        driver_laps = session.laps.pick_driver(driver)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        ax.hist(driver_laps['LapTime'].dt.total_seconds(), 
                bins=20, 
                edgecolor='black')
        
        ax.set_xlabel('Lap Time (seconds)')
        ax.set_ylabel('Count')
        ax.set_title(f'{driver} Lap Time Distribution - {session.event.year} {session.event.name}')
        
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
        img.close()
