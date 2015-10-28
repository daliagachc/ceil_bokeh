from __future__ import print_function

from ceil_bokeh import sql_con, plots

from bokeh.browserlib import view
from bokeh.document import Document
from bokeh.embed import file_html
from bokeh.resources import INLINE


data_weather = sql_con.get_data_ws(time_int=3600)

plot_weather = plots.get_weather_plot(data_weather)

# data_ceil = sql_con.get_data_bs()

# plot_ceil = plots.get_bs_plot(data_ceil)

# link x_range both plots
# plot_weather.x_range = plot_ceil.x_range

doc = Document()
doc.add(plot_weather)
# doc.add(plot_ceil)

if __name__ == "__main__":
    filename = "twin_axis.html"
    with open(filename, "w") as f:
        f.write(file_html(doc, INLINE, "Twin Axis Plot"))
    print("Wrote %s" % filename)
    view(filename)
