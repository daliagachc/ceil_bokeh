import time
from bokeh.models import VBox, Plot, ColumnDataSource, BoxSelectTool
from bokeh.plotting import figure
from bokeh.properties import Instance
import pandas as pd
import sys
from ceil_bokeh import sql_con
from ceil_bokeh.PlotManager import PlotManager
import ceil_bokeh.plots as plots
from bokeh.models.widgets import RadioButtonGroup
import ceil_bokeh.constants as cs
__author__ = 'diego'


class SlidersApp(VBox):
    """An example of a browser-based, interactive plot with slider controls."""

    extra_generated_classes = [["SlidersApp", "SlidersApp", "VBox"]]

    plot_data_range = Instance(Plot)
    plot_ceil = Instance(Plot)
    source_data_range = Instance(ColumnDataSource)
    source_weather = Instance(ColumnDataSource)
    plot_weather = Instance(Plot)
    p_manager = PlotManager()
    utc_button = Instance(RadioButtonGroup)



    def __init__(self, *args, **kwargs):
        super(SlidersApp, self).__init__(*args, **kwargs)

    @classmethod
    def create(cls):
        """One-time creation of app's objects.

        This function is caalled once, and is responsible for
        creating all objects (plots, datasources, etc)
        """
        obj = cls()

        obj.utc_button = RadioButtonGroup(
            labels=["local time", "UTC"], active=cs.utc_start)

        obj.source_data_range=ColumnDataSource(data=dict(x=[], y=[]))
        obj.p_manager.create(obj.source_data_range)

        obj.plot_weather = obj.p_manager.plot_weather
        obj.plot_ceil = obj.p_manager.plot_ceil
        obj.plot_data_range = obj.p_manager.plot_data_range

        obj.plot_ceil.x_range = obj.plot_weather.x_range

        obj.children.append(obj.utc_button)
        obj.children.append(obj.plot_data_range)
        obj.children.append(obj.plot_ceil)
        obj.children.append(obj.plot_weather)

        if cs.utc_start == 0:
            print 'changing to utc '
            sys.stdout.flush()
            obj.p_manager.shift_time(obj,0)



        return obj

    def setup_events(self):
        """Attaches the on_change event to the value property of the widget.

        The callback is set to the input_change method of this app.
        """
        super(SlidersApp, self).setup_events()

        if self.source_data_range:
            self.source_data_range.on_change('selected', self, 'input_change')

        # if self.utc_button:
        #     self.utc_button.on_change('active', self, 'input_change')

        if self.utc_button:
            self.utc_button.on_click(lambda x: self.p_manager.shift_time(self,x) )

            # Slider event registration

    def input_change(self, obj, attrname, old, new):
        """Executes whenever the input form changes.

        It is responsible for updating the plot, or anything else you want.

        Args:
            obj : the object that changed
            attrname : the attr that changed
            old : old value of attr
            new : new value of attr
        """
        self.p_manager.input_change(self,obj,attrname,old,new)


