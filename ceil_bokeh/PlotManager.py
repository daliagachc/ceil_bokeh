import logging
logger = logging.getLogger(__name__)
from bokeh.models import ColumnDataSource

from ceil_bokeh import plots
from ceil_bokeh import constants as cs

__author__ = 'diego'


class PlotManager(object):


    column_names = cs.column_names_weewx

     # first retrieval is alway in utc

    def __init__(self):
        logger.debug('creating object from %s',self)
        pass
    def create(self, source_data_range):
        logger.debug('initializing %s class',self)
        self.utc = 1
        logger.debug('current utc is %s',self.utc)
        # data_weather = sql_con.get_data_ws()
        # data_weather = sql_con.get_data_ws()
        # data_weather = sql_con.get_data_ws()
        self.plot_weather = plots.get_weather_plot()
        self.plot_ceil = plots.get_ceil_plot()
        self.plot_data_range = plots.get_date_range_plot(source_data_range)
        self._id_weather = self.plot_weather._id
        self._id_ceil = self.plot_ceil._id
        self._id_data_range = self.plot_data_range._id



        # df=source_data_range.to_df()
        #
        # t_max,t_min = plots.get_first_time_interval()
        # index=df[df.x>=(t_min-3600*50)*1000].index.values
        # source_data_range.selected['1d']['indices']=index

    def input_change(self, app, obj, attrname, old, new):

        logger.debug('input change detected wiht atrr %s', attrname)
        logger.debug('current utc is %f',self.utc)
        assert isinstance(obj, ColumnDataSource)
        data_frame = obj.to_df()
        t_min, t_max = get_t_min_max_from_sel(data_frame, new)
        t_int = get_time_int(t_max - t_min)

        if self.utc == 0:
            t_min -= cs.utc_shift
            t_max -= cs.utc_shift

        new_plot_weather = plots.get_weather_plot(t_int, t_min, t_max)

        plot_weather = find_plot(app, self._id_weather)

        plot_weather.select(ColumnDataSource)[0].data = new_plot_weather.select(ColumnDataSource)[0].data
        plots.update_y_ranges(
            cs.column_names_weewx,
            new_plot_weather.select(ColumnDataSource)[0].to_df(),
            plot_weather
        )

        plot_weather.title = new_plot_weather.title

        new_plot_ceil = plots.get_ceil_plot(t_int, t_min, t_max)
        plot_ceil = find_plot(app, self._id_ceil)
        plot_ceil.select(ColumnDataSource)[0].data = new_plot_ceil.select(ColumnDataSource)[0].data

        plot_ceil.title = new_plot_ceil.title

        plot_weather.x_range.start = new_plot_weather.x_range.start
        plot_weather.x_range.end = new_plot_weather.x_range.end

        old_utc = self.utc
        self.utc = 1  # retrieval of data is always in utc
        self.shift_time(app, old_utc, change_data_range=False)

    def shift_time(self, app, utc, change_data_range=True):
        if utc == self.utc:
            return
        plots_id = [
            self._id_weather, self._id_ceil
        ]

        time_column = ['dateTime', 'x']

        if change_data_range:
            plots_id.append(self._id_data_range)
            time_column.append('x')

        if utc == 1:
            sign = -1
        else:
            sign = 1
        logger.debug('sign =%f',sign)
        for i, id in enumerate(plots_id):
            plot = find_plot(app, id)
            column_data_source = plot.select_one(ColumnDataSource)
            df_miliseconds = column_data_source.to_df()
            df_miliseconds[time_column[i]] += sign * cs.utc_shift * 1000
            new_csd = ColumnDataSource(df_miliseconds)
            column_data_source.data = new_csd.data
        find_plot(app, plots_id[0]).x_range.start += sign*cs.utc_shift * 1000
        find_plot(app, plots_id[0]).x_range.end += sign*cs.utc_shift * 1000

        self.utc = utc


def get_time_int(t_span):
    list = cs.data_average_interval_list
    for t_max, t_int in list:
        if t_span <= t_max:
            return t_int
    return list[-1][1]


def get_t_min_max_from_sel(data_frame, new):
    ind = new['1d']['indices']
    # print type(df)
    # print df
    # print ind
    sel_df = data_frame.iloc[ind]
    sel_df = sel_df.sort_values('x')
    # print sel_df

    times = [int(i / 1000) for i in sel_df['x'].iloc[[0, -1]].values]
    t_min = times[0]
    t_max = times[1]
    return t_min, t_max


def find_plot(app, id):
    for name, plot in app.__dict__.iteritems():
        try:
            plot._id
            if plot._id == id:
                return plot
        except:
            pass
    raise
