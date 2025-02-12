import matplotlib
matplotlib.use("Agg")
from flask import Flask, render_template, request
from flask_caching import Cache
import fastf1 as ff1
from fastf1 import plotting
from matplotlib import pyplot as plt
from matplotlib.pyplot import figure
import numpy as np
import pandas as pd
import io
import base64
import seaborn as sns
import os



from plots import (
    plot_driver_stints,
    plot_tire_deg,
    plot_lap_distribution,
    plot_head_to_head,
    plot_driver_style,
    plot_tire_analysis,
    plot_driver_speed,
)

app = Flask(__name__)


TEMPLATE_NAME = "index.html"


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "head_to_head_submit" in request.form:
            # Handle head-to-head form submission
            year = int(request.form.get("year", 2024))
            weekend = int(request.form["wknd"])
            session_type = request.form.get("session", "R")
            driver1 = request.form["driver1"]
            driver2 = request.form["driver2"]

            try:
                head_to_head_img = plot_head_to_head(
                    year, weekend, session_type, driver1, driver2
                )
                return render_template(
                    TEMPLATE_NAME,
                    year=year,
                    weekend=weekend,
                    session=session_type,
                    wknd=str(weekend),
                    driver1=driver1,
                    driver2=driver2,
                    head_to_head_img=head_to_head_img,
                )
            except Exception as e:
                print(f"Error generating head-to-head plot: {str(e)}")
                return render_template(
                    TEMPLATE_NAME,
                    error="An error occurred while generating the head-to-head comparison.",
                )
        elif "driver_style_submit" in request.form:
            year = int(request.form.get("year", 2024))
            weekend = int(request.form["wknd"])
            session_type = request.form.get("session", "R")
            driver = request.form.get("driver", "VER")

            try:
                driver_style_img = plot_driver_style(year, weekend, session_type, driver=driver)
                return render_template(
                    TEMPLATE_NAME,
                    year=year,
                    weekend=weekend,
                    session=session_type,
                    wknd=str(weekend),
                    driver=driver,
                    driver_style_img=driver_style_img,
                )
            except Exception as e:
                print(f"Error generating driver style plot: {str(e)}")
                return render_template(
                    TEMPLATE_NAME,
                    error="An error occurred while generating the driver style comparison.",
                )
        elif "track_speed_submit" in request.form:
            # Handle track speed form submission
            year = int(request.form.get("speed_year", 2024))
            weekend = int(request.form["speed_wknd"])
            driver = request.form["speed_driver"]

            try:
                driver_speed_img = plot_driver_speed(year, weekend, "R", driver)
                return render_template(
                    TEMPLATE_NAME,
                    year=year,
                    weekend=weekend,
                    speed_driver=driver,
                    driver_speed_img=driver_speed_img,
                )
            except Exception as e:
                print(f"Error generating track speed plot: {str(e)}")
                return render_template(
                    TEMPLATE_NAME,
                    error="An error occurred while generating the track speed analysis.",
                )
        else:
            # Main form submission
            year = int(request.form["year"])
            weekend = int(request.form["weekend"])
            session_type = request.form["session"]
            driver = request.form.get("driver", "VER")

            try:
                stints_img = plot_driver_stints(year, weekend, session_type, driver=driver)
                lap_dist_img = plot_lap_distribution(year, weekend, session_type, driver=driver)
                driver_style_img = plot_driver_style(year, weekend, session_type, driver=driver)
                driver_speed_img = plot_driver_speed(year, weekend, session_type, driver=driver)

                return render_template(
                    TEMPLATE_NAME,
                    year=year,
                    weekend=weekend,
                    session=session_type,
                    stints_img=stints_img,
                    lap_dist_img=lap_dist_img,
                    driver_style_img=driver_style_img,
                    driver_speed_img=driver_speed_img,
                )
            except Exception as e:
                import traceback
                print(f"Error generating plots: {str(e)}")
                print(traceback.format_exc())
                return render_template(
                    TEMPLATE_NAME,
                    error="Request timed out. Please try again with fewer plots or a different session.",
                )

    return render_template(TEMPLATE_NAME)


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)

