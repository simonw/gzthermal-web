from sanic import Sanic
from sanic import response
import aiohttp
import os
import subprocess
import tempfile

OPTIONS = (
    'e', 's', 'm', 'l', 'n', 'w', 'b', 'z', 'g'
)
TIMEOUT = 3


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
GZTHERMAL = os.path.realpath(os.path.join(os.path.dirname(__file__), 'gzthermal_04c_linux64'))


async def run_gzthermal(url, args=None):
    args = args or []
    tmp = tempfile.TemporaryDirectory()
    os.chdir(tmp.name)
    try:
        async with aiohttp.ClientSession(auto_decompress=False) as session:
            async with session.get(url) as response:
                gzipped = await response.read()
                open('tmp.gz', 'wb').write(gzipped)

        subprocess.run(
            [GZTHERMAL] +
            args +
            ['tmp.gz'],
            timeout=TIMEOUT,
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
        url = url[0]
        args = []
        for option in OPTIONS:
            if request.args.get(option):
                args = ['-{}'.format(option)]
        if (
            not url.startswith('http://') and
            not url.startswith('https://')
        ):
            url = 'http://' + url
        data = await run_gzthermal(url, args)
        return response.raw(data, content_type='image/png')
    else:
        return response.html(INDEX)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8006)
