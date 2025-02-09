import matplotlib

matplotlib.use("Agg")
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
from plots import (
    plot_driver_stints,
    plot_tire_deg,
    plot_laptimes_distribution,
    plot_head_to_head,
    plot_driver_styling,
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
            # Handle driver style form submission
            year = int(request.form.get("year", 2024))
            weekend = int(request.form["wknd"])
            session_type = request.form.get("session", "R")
            selected_drivers = request.form.getlist("selected_drivers")

            try:
                driver_style_img = plot_driver_styling(
                    year, weekend, session_type, selected_drivers
                )
                return render_template(
                    TEMPLATE_NAME,
                    year=year,
                    weekend=weekend,
                    session=session_type,
                    wknd=str(weekend),
                    selected_drivers=selected_drivers,
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
            # Handle main form submission (existing code)
            year = int(request.form["year"])
            weekend = int(request.form["weekend"])
            session_type = request.form["session"]

            try:
                stints_img = plot_driver_stints(year, weekend, session_type)
                tire_deg_img = plot_tire_deg(year, weekend, session_type)
                tire_analysis_img = plot_tire_analysis(weekend)
                head_to_head_img = plot_head_to_head(year, weekend, session_type)
                laptimes_img = plot_laptimes_distribution(year, weekend, session_type)
                driver_speed_img = plot_driver_speed(year, weekend, session_type)

                return render_template(
                    TEMPLATE_NAME,
                    year=year,
                    weekend=weekend,
                    session=session_type,
                    stints_img=stints_img,
                    tire_deg_img=tire_deg_img,
                    tire_analysis_img=tire_analysis_img,
                    head_to_head_img=head_to_head_img,
                    laptimes_img=laptimes_img,
                    driver_speed_img=driver_speed_img,
                )
            except Exception as e:
                # Handle any errors that might occur during plot generation
                print(f"Error generating plots: {str(e)}")
                return render_template(
                    TEMPLATE_NAME,
                    error="An error occurred while generating the plots. Please try different parameters.",
                )

    return render_template(TEMPLATE_NAME)


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)

