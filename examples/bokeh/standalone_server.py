from bokeh.server.server import Server
from bokeh.application import Application
from bokeh.application.handlers.function import FunctionHandler
from bokeh.plotting import figure, ColumnDataSource
import random

def make_document(doc):
    source = ColumnDataSource({'x': [], 'y': [], 'color': []})

    def update():
        new = {'x': [random.random()],
               'y': [random.random()],
               'color': [random.choice(['red', 'blue', 'green'])]}
        source.stream(new)

    doc.add_periodic_callback(update, 100)

    fig = figure(title='Streaming Circle Plot!', sizing_mode='scale_width',
                 x_range=[0, 1], y_range=[0, 1])
    fig.circle(source=source, x='x', y='y', color='color', size=10)

    doc.title = "Now with live updating!"
    doc.add_root(fig)

apps = {'/': Application(FunctionHandler(make_document))}

server = Server(apps)
server.start()


if __name__ == '__main__':
    print('Opening Bokeh application on http://localhost:5006/')

    server.io_loop.add_callback(server.show, "/")
    server.io_loop.start()