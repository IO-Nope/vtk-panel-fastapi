from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import panel as pn
import vtk
from panel.pane import VTK
import utils
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

pn.extension('vtk')

options = ["cube", "sphere", "cone"]
seldrop = pn.widgets.Select(name='选择几何体', options=options, value='cube')
output = pn.widgets.StaticText(name="显示选项", value="")


render_window = utils.Create_vtk_cube()
vtk_pane = VTK(render_window)

#外部定义静态样式
with open("templates/index.html", "r", encoding="utf-8") as f:
    html_template = f.read()

panel_app = pn.Column(templates,seldrop,output, vtk_pane)
htmlpane = pn.pane.HTML(html_template)

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
    html_content = utils.Tohtml(panel_app)
    return HTMLResponse(content=html_content)

@app.get("/html", response_class=HTMLResponse)
async def read_html(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

