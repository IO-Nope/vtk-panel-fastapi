import panel as pn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from panel.widgets import button
from beampage import BeamPage
from beampage import notification



app=FastAPI()
beampage = BeamPage()
beampage.page.servable()
pn.extension('vtk',notifications=True)

server = pn.serve(
        beampage.page,
        port=5006,
        show=False,
        start=False
    )
server.start()
@app.get("/visualbeam")
def serve_root():
    html = """
    <!DOCTYPE html>
    <html lang="en" style="height:100%;">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Panel App</title>
        <style>
            html, body {
                height: 100%;
                margin: 0;
                padding: 0;
            }
            body {
                height: 100%;
                width: 100%;
                overflow: hidden;
            }
            iframe {
                height: 100%;
                width: 100%;
                border: none;
                display: block;
            }
        </style>
    </head>
    <body>
        <iframe src="http://localhost:5006"></iframe>
    </body>
    </html>
    """
    return HTMLResponse(content=html)