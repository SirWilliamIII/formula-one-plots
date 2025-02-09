import fastf1 as ff1
from fastf1 import plotting
import matplotlib.pyplot as plt
import io
import base64
from .utils import setup_cache

def plot_head_to_head(year, weekend, session_type, driver1, driver2):
    
    ff1.plotting.setup_mpl(mpl_timedelta_support=False, misc_mpl_mods=False, color_scheme='fastf1')
    ff1.Cache.enable_cache(setup_cache())
    
    session = ff1.get_session(year, weekend, session_type)
    session.load()
    
    d1_fast = session.laps.pick_drivers(driver1).pick_fastest()
    d2_fast = session.laps.pick_drivers(driver2).pick_fastest()
    telemetry_d1 = d1_fast.get_car_data().add_distance()
    telemetry_d2 = d2_fast.get_car_data().add_distance()
    
    fig, ax = plt.subplots(4, figsize=(15, 15))
    fig.suptitle("Fastest Race Lap Telemetry Comparison")

    ax[0].plot(telemetry_d1['Distance'], telemetry_d1['Speed'], label=driver1)
    ax[0].plot(telemetry_d2['Distance'], telemetry_d2['Speed'], label=driver2)
    ax[0].set(ylabel='Speed')
    ax[0].legend(loc="lower right")

    ax[1].plot(telemetry_d1['Distance'], telemetry_d1['Throttle'], label=driver1)
    ax[1].plot(telemetry_d2['Distance'], telemetry_d2['Throttle'], label=driver2)
    ax[1].set(ylabel='Throttle')

    ax[2].plot(telemetry_d1['Distance'], telemetry_d1['Brake'], label=driver1)
    ax[2].plot(telemetry_d2['Distance'], telemetry_d2['Brake'], label=driver2)
    ax[2].set(ylabel='Brakes')

    ax[3].plot(telemetry_d1['Distance'], telemetry_d1['RPM'], label=driver1)
    ax[3].plot(telemetry_d2['Distance'], telemetry_d2['RPM'], label=driver2)
    ax[3].set(ylabel='RPMs')

    for a in ax.flat:
        a.label_outer()

    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    plt.close()
    base64_img = base64.b64encode(img.getvalue()).decode('utf8')
    return f"data:image/png;base64,{base64_img}" 