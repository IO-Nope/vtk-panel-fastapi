import panel as pn
from fastapi import FastAPI
from starlette.responses import HTMLResponse as HTMLR
from fastapi.responses import RedirectResponse
import utils

app = FastAPI()

pn.extension()


templatea = pn.template.FastListTemplate(
    title="VTK SHOW",
    sidebar=["# Hello Sidebar", "This is text for the *sidebar*"],
    main=["# Hello Main", "This is text for the *main* area"],
)

pn.serve(
    templatea,
    port=5006,
    allow_websocket_origin=["127.0.0.1:5006", "localhost:5006"],  
    show=True,
    )


@app.get("/panel",response_class=HTMLR)
def server_panel():
    return RedirectResponse(url="http://127.0.0.1:5006")
