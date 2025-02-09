import fastf1 as ff1
from fastf1 import plotting
import matplotlib.pyplot as plt
import io
import base64
from .utils import setup_cache

def plot_driver_styling(year=2024, weekend=1, session_type="R", drivers=None):
    plotting.setup_mpl(mpl_timedelta_support=True, misc_mpl_mods=False, color_scheme='fastf1')
    ff1.Cache.enable_cache(setup_cache())
    session = ff1.get_session(year, weekend, session_type)
    session.load()
    
    if drivers is None:
        drivers = ['HAM', 'PER', 'VER', 'RUS']
    
    fig, ax = plt.subplots(figsize=(8, 6))
    
    for driver in drivers:
        laps = session.laps.pick_drivers(driver).pick_quicklaps().reset_index()
        style = plotting.get_driver_style(identifier=driver,
                                        style=['color', 'linestyle'],
                                        session=session)
        ax.plot(laps['LapTime'], **style, label=driver)
    
    ax.set_xlabel("Lap Number")
    ax.set_ylabel("Lap Time")
    ax.legend()
    plt.title(f"{session.event.year} {session.event.name} Driver Comparison")
    
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    plt.close()
    base64_img = base64.b64encode(img.getvalue()).decode('utf8')
    return f"data:image/png;base64,{base64_img}" 