from os import path

from jinja2 import Environment, FileSystemLoader
from sanic import Sanic
from sanic.response import html


HERE = path.dirname(path.abspath(__file__))

app = Sanic(name='stoom')

env = Environment(loader=FileSystemLoader(path.join(HERE, 'templates')))


@app.route('/')
async def index(request):
    template = env.get_template('stoom/index.html')
    return html(template.render())


if __name__ == '__main__':
    app.run()
