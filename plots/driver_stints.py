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
        if plot_cache:
            try:
                cache_key = f"stints_{year}_{weekend}_{session_type}_{driver}"
                cached_plot = plot_cache.get(cache_key)
                if cached_plot:
                    return cached_plot
            except Exception as e:
                print(f"Redis cache error: {str(e)}")
                plot_cache = None

        # Generate plot if not cached
        session = ff1.get_session(year, weekend, session_type)
        session.load()
        
        # Get driver's laps and sort by time
        driver_laps = session.laps.pick_driver(driver).sort_values('Time')
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Plot lap times colored by compound
        compounds = driver_laps['Compound'].unique()
        current_stint = 0
        last_compound = None
        
        for idx, lap in driver_laps.iterrows():
            if last_compound != lap['Compound']:
                current_stint += 1
                last_compound = lap['Compound']
            
            color = 'red' if lap['Compound'] == 'SOFT' else 'yellow' if lap['Compound'] == 'MEDIUM' else 'white'
            ax.scatter(lap['LapNumber'], 
                      lap['LapTime'].total_seconds(),
                      c=color,
                      edgecolor='black',
                      label=f'Stint {current_stint} ({lap["Compound"]})' if idx == driver_laps.index[0] or last_compound != driver_laps.iloc[idx-1]['Compound'] else "",
                      marker='o')
        
        # Remove duplicate labels
        handles, labels = plt.gca().get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        ax.legend(by_label.values(), by_label.keys())
        
        ax.set_xlabel('Lap Number')
        ax.set_ylabel('Lap Time (seconds)')
        ax.set_title(f'{driver} Stint Analysis - {session.event.year} {session.event.name}')
        ax.grid(True, alpha=0.2)
        
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
        print(f"Error in plot_driver_stints: {str(e)}")
        raise
    finally:
        if plt is not None:
            plt.close('all')
        if img is not None:
            img.close()
