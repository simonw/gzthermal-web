from sanic import Sanic
from sanic import response
import os
import requests
import subprocess
import tempfile

INDEX = '''
<html>
<head>
    <title>gzthermal-web</title>
<style>body {font-family: Helvetica }</style>
</head>
<body>
<h1>gzthermal-web</h1>

<p>A simple web application wrapping 
    <a href="https://encode.ru/threads/1889-gzthermal-pseudo-thermal-view-of-Gzip-Deflate-compression-efficiency">gzthermal by caveman on encode.ru</a>
</p>

<form action="/">
    <p>
        <label for="url">URL:</label>
        <input type="text" name="url" id="url" size="30">
        <label><input type="checkbox" name="z"> Bicolor</label>
        <input type="submit" value="Visualize">
    </p>
</form>

<p style="font-size: 0.7em">Web app <a href="https://github.com/simonw/gzthermal-web">source code on GitHub</a></p>

</html>
'''


def run_gzthermal(url, args=None):
    args = args or []
    tmp = tempfile.TemporaryDirectory()
    os.chdir(tmp.name)
    try:
        r = requests.get(url, stream=True)
        gzipped = r.raw.read()
        open('tmp.gz', 'wb').write(gzipped)
        subprocess.call(
            ['/app/gzthermal_04c_linux64'] +
            args +
            ['tmp.gz']
        )
        png = open('gzthermal-result.png', 'rb').read()
    finally:
        tmp.cleanup()
    return png


app = Sanic(__name__)


@app.route('/')
async def handle_request(request):
    url = request.args.getlist('url')
    if url:
        args = []
        if request.args.get('z'):
            args = ['-z']
        data = run_gzthermal(url[0], args)
        return response.raw(data, content_type='image/png')
    else:
        return response.html(INDEX)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8006)
