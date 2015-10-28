"""This file demonstrates a bokeh applet, which can be viewed directly
on a bokeh-server. See the README.md file in this directory for
instructions on running.

This example shows how to create a simple applet in Bokeh, which can
be viewed directly on a bokeh-server.

Running
=======

To view this applet directly from a bokeh server, you simply need to
run a bokeh-server and point it at the stock example script:

    bokeh-server --script sliders_app.py

Now navigate to the following URL in a browser:

    http://localhost:5006/bokeh/sliders

"""

import logging

from bokeh.server.app import bokeh_app
from bokeh.server.utils.plugins import object_page

from ceil_bokeh.tests.SlidersApp import SlidersApp
import ceil_bokeh.plots as plots

logging.basicConfig(level=logging.DEBUG)


# The following code adds a "/bokeh/sliders/" url to the bokeh-server. This
# URL will render this sine wave sliders app. If you don't want to serve this
# applet from a Bokeh server (for instance if you are embedding in a separate
# Flask application), then just remove this block of code.
@bokeh_app.route("/bokeh/sliders/")
@object_page("sin")
def make_sliders():
    app = SlidersApp.create()


    return app
