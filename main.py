from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import panel as pn
from fastapi.responses import RedirectResponse
import vtk
from panel.pane import VTK
import utils
import io

app = FastAPI()

pn.extension('vtk')

options = ["cube", "sphere", "cone"]
seldrop = pn.widgets.Select(name='选择几何体', options=options, value='cube')
output = pn.widgets.StaticText(name="显示选项", value="")

render_window = utils.Create_vtk_cube()
vtk_pane = VTK(render_window)


template = pn.template.FastListTemplate(
    title="VTK SHOW",
    sidebar=[seldrop, output],
    main=[vtk_pane],
)

pn.serve(
    template,
    port=5006,
    allow_websocket_origin=["127.0.0.1:5006", "localhost:5006"],  
    show=True,
    )

@pn.depends(seldrop.param.value,watch=True)
async def update_vtk(value):
    render_ = utils.Create_vtk_cube()
    if value == "cube":
        render_ = utils.Create_vtk_cube()
        output.value = "显示立方体"
    elif value == "sphere":
        render_ = utils.Create_vtk_sphere()
        output.value = "显示球体"
    elif value == "cone":
        render_ = utils.Create_vtk_cone()
        output.value = "显示圆锥体"
    if vtk_pane is not None : 
        vtk_pane.object = render_


@app.get("/panel", response_class=HTMLResponse)
def serve_panel():
    return RedirectResponse(url="http://127.0.0.1:5006")