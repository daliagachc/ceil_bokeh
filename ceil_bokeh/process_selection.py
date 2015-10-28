from bokeh.models import ColumnDataSource, Plot, DataRange1d
import ceil_bokeh.tests.SlidersApp

__author__ = 'diego'

import sys

from ceil_bokeh import sql_con
import ceil_bokeh.tests.SlidersApp as SlidersApp

from ceil_bokeh import constants as cs
from ceil_bokeh import PlotManager as pm

def process_selection(app,obj,attrname,old,new):

    print 'start process selection '
    print 'app',app
    print 'obl',obj
    print 'attrname',attrname
    print 'old',old
    print 'new',new

    plots_id=[
        app.p_manager._id_weather,app.p_manager._id_ceil,app.p_manager._id_data_range
    ]

    time_column = ['dateTime','x','x']

    if new==1:
        sign = 1

    else:
        sign = -1
    print 'sign=',sign
    sys.stdout.flush()
    for i,id in enumerate(plots_id):
        plot = pm.find_plot(app,id)
        print 'plot name ',plot.name
        column_data_source = plot.select_one(ColumnDataSource)
        df_miliseconds = column_data_source.to_df()
        print df_miliseconds
        sys.stdout.flush()
        df_miliseconds[time_column[i]] = df_miliseconds[time_column[i]] + sign*cs.utc_shift*1000
        new_csd=ColumnDataSource(df_miliseconds)
        column_data_source.data=new_csd.data

    # assert type(app) is SlidersApp

    # t_max, t_min = get_t_min_max_from_sel(df, new)
    # time_int = 60 * 60 * 1
    #
    # data = sql_con.get_data_ws(time_int, t_min=t_min, t_max=t_max)
    # data_seconds = data
    # data_seconds.iloc[:, 0] = data_seconds.iloc[:, 0] * 1000
    #
    # app.p_manager.update_source(app, new)
    # # self.p_manager.find_plot(self).select('ws_source')[0]=ColumnDataSource(data_seconds)
    # # self.weather_plot.select('ws_source')[0]=ColumnDataSource(data_seconds, name='ws_source')
    # # self.weather_plot.select('ws_source')[0].data=ColumnDataSource(data_seconds).data
    # # self.weather_plot.x_range.start=1445000000000
    # print app.weather_plot.name
    # print app.select({'name': 'plot'})
    #
    # print app.p_manager.plot.x_range.start
    from bokeh.models import PanTool, WheelZoomTool, CrosshairTool, ToolEvents, BoxSelectTool

    # print app.plot_data_range.select_one(BoxSelectTool).__dict__
    # import ceil_bokeh.plots as plots
    # df=app.source_data_range.to_df()
    # print app.select(Plot)
    # t_max,t_min = plots.get_first_time_interval()
    # index=df[df.x>=(t_min-3600*50)*1000].index.values
    # app.source_data_range.selected['1d']['indices']=index
    # print app.plot_weather.select_one(ColumnDataSource).selected
    # print app.plot_weather.select_one(ColumnDataSource).to_df().index.values
    # app.plot_weather.select_one(ColumnDataSource).selected['1d']['indices'] = app.plot_weather.select_one(ColumnDataSource).to_df().index.values
    # print app.plot_data_range.select_one(ColumnDataSource).selected['1d']['indices']
    #
    # print app.plot_weather.select(DataRange1d)

    # app.plot_weather.x_range.start=0

    # df=obj.to_df()
    #
    # t_max,t_min = plots.get_first_time_interval()
    # index=df[df.x>=(t_min-3600*50)*1000].index.values
    # obj.selected['1d']['indices']=index

    sys.stdout.flush()


def get_t_min_max_from_sel(df, new):
    ind = new['1d']['indices']
    # print type(df)
    # print df
    # print ind
    sel_df = df.iloc[ind]
    sel_df = sel_df.sort_values('x')
    # print sel_df

    times = [int(i / 1000) for i in sel_df['x'].iloc[[0, -1]].values]
    t_min = times[0]
    t_max = times[1]
    return t_min, t_max
