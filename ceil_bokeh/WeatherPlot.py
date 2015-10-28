import time

__author__ = 'diego'
from bokeh.models import Plot, DataRange1d, DatetimeAxis, PanTool, WheelZoomTool, ResizeTool, CrosshairTool, \
    ColumnDataSource, Line, LinearAxis, ToolEvents

from ceil_bokeh import constants as cs
from ceil_bokeh import sql_con


class WeatherPlot(Plot):

    __subtype__ = "WeatherPlot"
    __view_model__ = "Plot"

    def __init__(self,**kwargs):
        super(WeatherPlot,self).__init__(**kwargs)

    # def __init__(self,
    #              data,
    #              column_names=cs.column_names_weewx,
    #              column_time=cs.time_column_name_weewx,
    #              plot_height=300,
    #              plot_width=800,
    #              border_left=150,
    #              **kwargs):
    #     if "tool_events" not in kwargs:
    #         kwargs["tool_events"] = ToolEvents()
    #     super(WeatherPlot,self).__init__(x_range=DataRange1d(),
    #                                      y_range=DataRange1d(),
    #                                      plot_width=800,
    #                                      plot_height=500,
    #                                      min_border_left=150,
    #                                      **kwargs)

        time_int = 3600
        t_max = int(time.time())
        t_min = t_max - 3600 * 24
        data = sql_con.get_data_ws(time_int=time_int,
                                           t_max=t_max,
                                           t_min=t_min)
        self._data = data
        column_names=cs.column_names_weewx
        column_time=cs.time_column_name_weewx
        data_seconds = data
        data_seconds.iloc[:, 0] = data_seconds.iloc[:, 0] * 1000
        add_glyphs_to_plot(column_names, column_time, data_seconds, self)
        self.add_layout(DatetimeAxis(), 'below')
        self.add_tools(PanTool(), WheelZoomTool(), ResizeTool(), CrosshairTool())
        # self._data = data
        # self._column_names = column_names
        # self._column_time = column_time

    def update_source(self,data):
        self._data = data
        data_seconds = data
        data_seconds.iloc[:, 0] = data_seconds.iloc[:, 0] * 1000
        self.select('ws_source')[0]=ColumnDataSource(data_seconds)
        set_y_ranges(self.column_names,data_seconds,self.plot)



def get_ws_plot(data,
                plot_height=300,
                plot_width=800,
                column_names=cs.column_names_weewx,
                column_time=cs.time_column_name_weewx,
                border_left=200):
    data_seconds = data
    data_seconds.iloc[:, 0] = data_seconds.iloc[:, 0] * 1000

    plot = Plot(x_range=DataRange1d(),
                y_range=DataRange1d(),
                plot_width=plot_width,
                plot_height=plot_height,
                min_border_left=border_left,
                **kwargs)

    add_glyphs_to_plot(column_names, column_time, data_seconds, plot)

    plot.add_layout(DatetimeAxis(), 'below')

    plot.add_tools(PanTool(), WheelZoomTool(), ResizeTool(), CrosshairTool())
    return plot


def add_glyphs_to_plot(column_names, column_time, data_seconds, plot):
    pos = ["right", "left", "left", "left", "left", "left", "left", "left", "left"]
    plot.extra_y_ranges = {}
    colors = ['blue', 'orange', 'green', 'purple', 'red']
    source = ColumnDataSource(data=data_seconds, name='ws_source')

    set_y_ranges(column_names, data_seconds, plot)

    set_glyphs(colors, column_names, column_time, plot, pos, source)


def set_glyphs(colors, column_names, column_time, plot, pos, source):
    for i, name in enumerate(column_names):
        color = colors[i]
        line = Line(x=column_time,
                    y=name,
                    line_width=1,
                    line_alpha=.7,
                    line_color=color)

        plot.add_layout(LinearAxis(y_range_name=name,
                                   major_label_text_color=color,
                                   axis_line_color=color,
                                   major_tick_line_color=color,
                                   minor_tick_line_color=color),
                        pos[i])

        plot.add_glyph(source,
                       line,
                       y_range_name=name,
                       name=name)


def set_y_ranges(column_names, data_seconds, plot):
    for i, name in enumerate(column_names):
        r_end, r_start = find_range(data_seconds, name)
        plot.extra_y_ranges[name] = DataRange1d(start=r_start,
                                                end=r_end)


def find_range(data_seconds, name):
    r_start = float(data_seconds[name].min())
    r_end = float(data_seconds[name].max())
    if r_start == r_end:
        r_start -= 1
        r_end += 1
    else:
        padding = r_end - r_start
        r_start -= padding * .1
        r_end += padding * .1
    return r_end, r_start
