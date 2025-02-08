import matplotlib
matplotlib.use('Agg')
import fastf1 as ff1
from fastf1 import plotting
from matplotlib import pyplot as plt
from matplotlib.pyplot import figure
import numpy as np
import pandas as pd
import io
import base64
import seaborn as sns
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'head_to_head_submit' in request.form:
            # Handle head-to-head form submission
            year = int(request.form.get('year', 2024))
            weekend = int(request.form['wknd'])
            session_type = request.form.get('session', 'R')
            driver1 = request.form['driver1']
            driver2 = request.form['driver2']
            
            try:
                head_to_head_img = plot_head_to_head(year, weekend, session_type, driver1, driver2)
                return render_template('index.html',
                                    year=year,
                                    weekend=weekend,
                                    session=session_type,
                                    wknd=str(weekend),
                                    driver1=driver1,
                                    driver2=driver2,
                                    head_to_head_img=head_to_head_img)
            except Exception as e:
                print(f"Error generating head-to-head plot: {str(e)}")
                return render_template('index.html', 
                                    error="An error occurred while generating the head-to-head comparison.")
        elif 'driver_style_submit' in request.form:
            # Handle driver style form submission
            year = int(request.form.get('year', 2024))
            weekend = int(request.form['wknd'])
            session_type = request.form.get('session', 'R')
            selected_drivers = request.form.getlist('selected_drivers')
            
            try:
                driver_style_img = plot_driver_styling(year, weekend, session_type, selected_drivers)
                return render_template('index.html',
                                    year=year,
                                    weekend=weekend,
                                    session=session_type,
                                    wknd=str(weekend),
                                    selected_drivers=selected_drivers,
                                    driver_style_img=driver_style_img)
            except Exception as e:
                print(f"Error generating driver style plot: {str(e)}")
                return render_template('index.html', 
                                    error="An error occurred while generating the driver style comparison.")
        else:
            # Handle main form submission (existing code)
            year = int(request.form['year'])
            weekend = int(request.form['weekend'])
            session_type = request.form['session']
            
            try:
                stints_img = plot_driver_stints(year, weekend, session_type)
                tire_deg_img = plot_tire_deg(year, weekend, session_type)
                head_to_head_img = plot_head_to_head(year, weekend, session_type)
                laptimes_img = plot_laptimes_distribution(year, weekend, session_type)
                
                return render_template('index.html',
                                    year=year,
                                    weekend=weekend,
                                    session=session_type,
                                    stints_img=stints_img,
                                    tire_deg_img=tire_deg_img,
                                    head_to_head_img=head_to_head_img,
                                    laptimes_img=laptimes_img)
            except Exception as e:
                # Handle any errors that might occur during plot generation
                print(f"Error generating plots: {str(e)}")
                return render_template('index.html', 
                                    error="An error occurred while generating the plots. Please try different parameters.")
    
    return render_template('index.html')

def plot_driver_stints(year, weekend, session_type):
    ff1.Cache.enable_cache("/Users/will/Library/Caches/fastf1")
    race = ff1.get_session(year, weekend, session_type)
    race.load()

    driver_stints = (
        race.laps[["Driver", "Stint", "Compound", "LapNumber"]]
        .groupby(["Driver", "Stint", "Compound"])
        .count()
        .reset_index()
    )

    driver_stints = driver_stints.rename(columns={"LapNumber": "StintLength"})
    driver_stints = driver_stints.sort_values(by=["Stint"])

    compound_colors = {
        "SOFT": "#FF3333",
        "MEDIUM": "#FFF200",
        "HARD": "#EBEBEB",
        "INTERMEDIATE": "#39B54A",
        "WET": "#00AEEF",
    }

    plt.rcParams["figure.figsize"] = [15, 10]
    plt.rcParams["figure.autolayout"] = True

    fig, ax = plt.subplots()

    for driver in race.results["Abbreviation"]:
        stints = driver_stints.loc[driver_stints["Driver"] == driver]
        previous_stint_end = 0
        for _, stint in stints.iterrows():
            plt.barh(
                [driver],
                stint["StintLength"],
                left=previous_stint_end,
                color=compound_colors[stint["Compound"]],
                edgecolor="black",
            )

            previous_stint_end = previous_stint_end + stint["StintLength"]
            
    
    plt.title(f"Race strategy - {race}")
    plt.xlabel("Lap")
    ax.invert_yaxis()
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)

    img = io.BytesIO()
    plt.savefig(img, format="png", dpi=300, bbox_inches="tight")
    img.seek(0)
    plt.close()
    base64_img = base64.b64encode(img.getvalue()).decode("utf8")
    return f"data:image/png;base64,{base64_img}"

def plot_tire_deg(year, weekend, session_type):
    plotting.setup_mpl(misc_mpl_mods=False, color_scheme="fastf1")
    ff1.Cache.enable_cache('/Users/will/Library/Caches/fastf1')
    session = ff1.get_session(year, weekend, session_type)
    session.load()
    
    laps = session.laps.copy()
    laps["LapTimeSeconds"] = laps["LapTime"].dt.total_seconds()
    laps["FastestStintLap"] = laps.groupby(["Driver", "Stint"])["LapTimeSeconds"].transform("min")
    laps["DegDelta"] = laps["LapTimeSeconds"] - laps["FastestStintLap"]

    g = sns.FacetGrid(laps, col="Driver", col_wrap=4, sharey=False, height=3)
    g.map_dataframe(sns.lineplot, x="TyreLife", y="DegDelta")
    g.set_axis_labels("Tire Life (laps)", "Degradation (s)")
    g.set_titles(col_template="{col_name}")
    plt.subplots_adjust(top=0.9)
    g.fig.suptitle("Tire Degradation Curves by Driver", y=1.02)

    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    plt.close()
    base64_img = base64.b64encode(img.getvalue()).decode('utf8')
    return f"data:image/png;base64,{base64_img}"

def plot_head_to_head(year, weekend, session_type, driver1="VER", driver2="PER"):
    ff1.plotting.setup_mpl(mpl_timedelta_support=False, misc_mpl_mods=False, color_scheme='fastf1')
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

def plot_laptimes_distribution(year, weekend, session_type):
    plotting.setup_mpl(mpl_timedelta_support=True, misc_mpl_mods=False, color_scheme='fastf1')
    session = ff1.get_session(year, weekend, session_type)
    session.load()
    
    # Get all the laps for the point finishers only
    point_finishers = session.drivers[:10]
    driver_laps = session.laps.pick_drivers(point_finishers).pick_quicklaps()
    driver_laps = driver_laps.reset_index()
    
    # Get the finishing order for the drivers
    finishing_order = [session.get_driver(i)['Abbreviation'] for i in point_finishers]
    
    # Create the figure
    fig, ax = plt.subplots(figsize=(10, 5))
    
    # Convert timedelta to float (seconds)
    driver_laps["LapTime(s)"] = driver_laps["LapTime"].dt.total_seconds()
    
    sns.violinplot(data=driver_laps,
                  x="Driver",
                  y="LapTime(s)",
                  hue="Driver",
                  inner=None,
                  density_norm="area",
                  order=finishing_order,
                  palette=plotting.get_driver_color_mapping(session=session))
    
    sns.swarmplot(data=driver_laps,
                  x="Driver",
                  y="LapTime(s)",
                  order=finishing_order,
                  hue="Compound",
                  palette=plotting.get_compound_mapping(session=session),
                  hue_order=["SOFT", "MEDIUM", "HARD"],
                  linewidth=0,
                  size=4)
    
    ax.set_xlabel("Driver")
    ax.set_ylabel("Lap Time (s)")
    plt.suptitle(f"{session.event.year} {session.event.name} Lap Time Distributions")
    sns.despine(left=True, bottom=True)
    
    plt.tight_layout()
    
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    plt.close()
    base64_img = base64.b64encode(img.getvalue()).decode('utf8')
    return f"data:image/png;base64,{base64_img}"

def plot_driver_styling(year, weekend, session_type, drivers=None):
    plotting.setup_mpl(mpl_timedelta_support=True, misc_mpl_mods=False, color_scheme='fastf1')
    session = ff1.get_session(year, weekend, session_type)
    session.load()
    
    if drivers is None:
        drivers = ['HAM', 'PER', 'VER', 'RUS']  # Default drivers if none specified
    
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

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)


