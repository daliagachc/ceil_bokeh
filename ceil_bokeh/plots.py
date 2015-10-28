import time

import pandas as pd

__author__ = 'diego'

'''
retrieves bs plot
'''
from math import isnan
from bokeh.plotting import figure
from bokeh.models.glyphs import Line
from bokeh.models import BoxSelectTool, Plot, PreviewSaveTool, Grid, Circle, Legend, GlyphRenderer
from bokeh.models import LinearAxis
from bokeh.models import ColumnDataSource
from bokeh.models import PanTool, WheelZoomTool, CrosshairTool
from bokeh.models import DataRange1d
from bokeh.models import DatetimeAxis
from bokeh.plotting_helpers import _update_legend as update_legend

from ceil_bokeh import sql_con
from ceil_bokeh import constants as cs


def get_weather_plot(time_int=None,t_min=None,t_max=None):
    plot_height = cs.plot_height
    plot_width = cs.plot_width
    border_left = cs.border_left
    column_names = cs.column_names_weewx
    column_time = cs.time_column_name_weewx
    if t_max == None or t_min == None:
        t_max, t_min = get_first_time_interval()
    t_span = t_max - t_min
    if time_int == None:
        time_int = cs.time_int
    data_seconds = sql_con.get_data_ws(time_int=time_int, t_min=t_min, t_max=t_max)
    data_seconds.iloc[:, 0] = data_seconds.iloc[:, 0] * 1000

    plot = Plot(x_range=DataRange1d(start=(t_min-t_span*.1)*1000,
                                    end=(t_max+t_span*.1)*1000),
                y_range=DataRange1d(),
                plot_width=plot_width,
                plot_height=plot_height,
                # x_axis_type="datetime",
                min_border_left=border_left,
                toolbar_location="right")

    add_glyphs_to_plot(column_names, column_time, data_seconds, plot,'source_weather')

    plot.add_layout(DatetimeAxis(name="date_time_axis"), 'below')

    plot.add_tools(PanTool(),
                   WheelZoomTool(),
                   # ResizeTool(),
                   CrosshairTool(),
                   PreviewSaveTool()
                   )
    Grid(plot=plot,dimension=0,ticker=plot.select('date_time_axis')[0].ticker)

    Grid(plot=plot,
         dimension=1,
         ticker=plot.select(type=LinearAxis,name=column_names[0])[0].ticker
         )

    set_legends(plot)

    plot.title = cs.plot_title_weewx + ' averaged to {} seconds'.format(time_int)


    return plot


def get_ceil_plot(time_int=None,t_min=None,t_max=None):
    if time_int == None:
        time_int = cs.time_int
    plot_height = cs.plot_height
    plot_width = cs.plot_width
    border_left = cs.border_left

    if t_min == None or t_max == None:
        t_max, t_min = get_first_time_interval()

    t_span = t_max-t_min

    data = sql_con.get_data_bs(time_int=time_int, t_min=t_min, t_max=t_max)
    # print data



    ll = len(data)
    toolset = [CrosshairTool(),WheelZoomTool(),PreviewSaveTool(),PanTool()]
    plot = figure(x_range=DataRange1d(start=(t_min-t_span*.1)*1000,
                                      end=(t_max+t_span*.1)*1000
                                      ),
                  y_range=[0, 250 * 15],
                  plot_height=plot_height,
                  plot_width=plot_width,
                  x_axis_type="datetime",
                  min_border_left=border_left,
                  toolbar_location="right",
                  tools=toolset
                  )
    plot.yaxis.axis_label = "meters above ground"
    dd = []
    tt = []
    y = []
    dw = []
    dh = []



    for i in range(ll):
        dd.append(data.iloc[i:i + 1, 1:].T.values)
        tt.append(int(data.iloc[i, 0]) * 1000 - time_int * 1000 / 2)
        y.append(0)
        dw.append(time_int * 1000)
        dh.append(250 * 15)

    plot.image(image=dd, x=tt, y=y, dw=dw, dh=dh, palette="Spectral11", dilate=True)

    plot.title = cs.plot_title_ceil + ' averaged to {} seconds'.format(time_int)

    return plot


def get_first_time_interval():
    t_max = int(time.time())
    t_min = int(t_max - cs.time_span_first)
    return t_max, t_min


def get_date_range_plot(source_time):

    data_time_ws = sql_con.get_data_tm(cs.time_column_name_weewx,
                                       cs.time_int_data_range,
                                       cs.data_base_name_weewx,
                                       cs.table_name_weewx
                                       ) * 1000
    data_time_bs = sql_con.get_data_tm(cs.time_column_name_ceil,
                                       cs.time_int_data_range,
                                       cs.data_base_name_ceil,
                                       cs.bs_table_name_ceil
                                       ) * 1000
    y_factors=['weather','ceilometer']
    data_time_ws['y'] = y_factors[0]
    data_time_bs['y'] = y_factors[1]

    data_time_bs.rename(columns={0: 'x'}, inplace=True)
    data_time_ws.rename(columns={0: 'x'}, inplace=True)

    source_df = pd.concat([data_time_ws, data_time_bs],
                          ignore_index=True)

    source_df.sort_values('x', inplace=True)

    source_time.data = ColumnDataSource(data=source_df).data
    source_time.name = 'source_time'

    toolset = "crosshair , xpan ,reset, xwheel_zoom"

    t_min_mili = float(source_df['x'].min())
    t_max_mili = float(source_df['x'].max())
    t_span_mili=t_max_mili-t_min_mili

    # Generate a figure container
    plot = figure(plot_height=cs.data_range_plot_height,
                  plot_width=cs.plot_width,
                  tools=toolset,
                  x_axis_type="datetime",
                  y_range=y_factors,
                  toolbar_location="right",
                  x_range=[t_min_mili-.1*t_span_mili,
                           t_max_mili+.1*t_span_mili],
                  logo=None)

    plot.add_tools(BoxSelectTool(dimensions=['width']))

    plot.circle('x', 'y', source=source_time, color="red")
    plot.title = "select interval from below"

    # df=source_time.to_df()

    # t_max,t_min = get_first_time_interval()
    # index=df[df.x>=t_min*1000].index.values
    # source_time.selected['1d']['indices']=index

    return plot


def add_glyphs_to_plot(column_names, column_time, data_seconds, plot,source_name):
    pos = ["right", "left", "left", "left", "left", "left", "left", "left", "left"]
    plot.extra_y_ranges = {}
    colors = ['blue', 'orange', 'green', 'purple', 'red']
    source = ColumnDataSource(data=data_seconds, name='ws_source')

    set_y_ranges(column_names, data_seconds, plot)

    set_glyphs(colors, column_names, column_time, plot, pos, source)


def set_glyphs(colors, column_names, column_time, plot, pos, source):
    for i, name in enumerate(column_names):
        color = colors[i]
        glyph_line = Line(x=column_time,
                    y=name,
                    line_width=1,
                    line_alpha=.7,
                    line_color=color)

        glyph = Circle(x=column_time,
                       y=name,
                       fill_color=color,
                       line_alpha=0,
                       fill_alpha=.7)



        plot.add_layout(LinearAxis(y_range_name=name,
                                   major_label_text_color=color,
                                   axis_line_color=color,
                                   major_tick_line_color=color,
                                   minor_tick_line_color=color,
                                   name=name),
                        pos[i])

        # plot.line(x=column_time,
        #           y=name,
        #           line_width=1,
        #           line_alpha=.7,
        #           line_color=color,
        #           legend=name,
        #           y_range_name=name,
        #           source=source)

        plot.add_glyph(source,
                       glyph,
                       y_range_name=name,
                       name=name)

        plot.add_glyph(source,
                       glyph_line,
                       y_range_name=name,
                       name=name)




def update_y_ranges(column_names, data_seconds, plot):
    for i, name in enumerate(column_names):
        r_end, r_start = find_range(data_seconds, name)

        plot.extra_y_ranges[name].start = r_start
        plot.extra_y_ranges[name].end = r_end


def set_y_ranges(column_names, data_seconds, plot):
    for i, name in enumerate(column_names):
        r_end, r_start = find_range(data_seconds, name)
        plot.extra_y_ranges[name] = DataRange1d(start=r_start,
                                                end=r_end)


def find_range(data_seconds, name):
    r_start = float(data_seconds[name].min())
    r_end = float(data_seconds[name].max())

    if isnan(r_start):
        r_start=0.0
    if isnan(r_end):
        r_end=1.0

    if r_start == r_end:
        r_start -= 1
        r_end += 1
    else:
        padding = r_end - r_start
        r_start -= padding * .1
        r_end += padding * .1
    return r_end, r_start


def set_legends(plot_weather):

    units_dict=dict()
    for i in range(len(cs.column_names_weewx)):
        units_dict[cs.column_names_weewx[i]]=cs.column_units_weewx[i]

    for i,glyph_renderer in enumerate(plot_weather.select(type=GlyphRenderer)):
        update_legend(plot_weather,
                      glyph_renderer.name + ' ' + units_dict[glyph_renderer.name],
                      glyph_renderer)

        legend = plot_weather.select_one(Legend)
        assert isinstance(legend, Legend)
        legend.background_fill_alpha = .7
        legend.border_line_alpha = .5
        legend.orientation = 'top_left'