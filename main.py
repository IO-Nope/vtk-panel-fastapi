from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import panel as pn
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
 

panel_app = pn.Column(seldrop,output, vtk_pane)

@pn.depends(seldrop.param.value, watch=True)
async def update_output(value):
    output.value = f"You choose: {value}"
    match value:
        case "cube":
            render_window = utils.Create_vtk_cube()
        case "sphere":
            render_window = utils.Create_vtk_sphere()
        case "cone":
            render_window = utils.Create_vtk_cone()
    global vtk_pane
    if vtk_pane is not None :vtk_pane.object = render_window

@app.get("/panel", response_class=HTMLResponse)
def serve_panel():
    html_buffer = io.StringIO()
    panel_app.save(html_buffer, embed=True)
    html_content = html_buffer.getvalue()
    html_buffer.close()
    return HTMLResponse(content=html_content)
