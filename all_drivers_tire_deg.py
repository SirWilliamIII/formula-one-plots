import matplotlib.pyplot as plt
import seaborn as sns
import fastf1 as ff1
from fastf1 import plotting



def plot_tire_deg(year, wkndsession_type):
    plotting.setup_mpl(misc_mpl_mods=False, color_scheme="fastf1")
    ff1.Cache.enable_cache('/Users/will/Library/Caches/fastf1')
    year = 2024
    wknd = input['wknd']
    session = ff1.get_session(year, wknd, "R")
    session.load()

    g = sns.FacetGrid(laps, col="Driver", col_wrap=4, sharey=False, height=3)

    g.map_dataframe(sns.lineplot, x="TyreLife", y="DegDelta")

    g.set_axis_labels("Tire Life (laps)", "Degradation (s)")
    g.set_titles(col_template="{col_name}")
    plt.subplots_adjust(top=0.9)
    g.fig.suptitle("Tire Degradation Curves by Driver", y=1.02)

    plt.show()