from __future__ import print_function

from bokeh.browserlib import view
from bokeh.document import Document
from bokeh.embed import file_html
from bokeh.resources import INLINE

from ceil_bokeh import sql_con, plots

border_left = 150
time_int = 3600
data_weather = sql_con.get_data_ws(time_int=time_int)

plot_weather = plots.get_weather_plot(data_weather, border_left=border_left)

data_ceil = sql_con.get_data_bs(time_int=time_int)

plot_ceil = plots.get_ceil_plot(data_ceil, time_int=time_int, border_left=border_left)

# link x_range both plots
plot_weather.x_range = plot_ceil.x_range

doc = Document()
doc.add(plot_weather)
doc.add(plot_ceil)

if __name__ == "__main__":
    filename = "twin_axis.html"
    with open(filename, "w") as f:
        f.write(file_html(doc, INLINE, "Twin Axis Plot"))
    print("Wrote %s" % filename)
    view(filename)
