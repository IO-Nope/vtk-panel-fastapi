from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import panel as pn
import vtk
from panel.pane import VTK
import utils
import io

app = FastAPI()

pn.extension('vtk')

def create_panel_app():
    render_window = utils.create_vtk_cube()
    vtk_pane = VTK(render_window)  # 使用 Panel 的 VTK Pane
    return pn.Column("# 立方体展示", vtk_pane)

panel_app = create_panel_app()

@app.get("/panel", response_class=HTMLResponse)
def serve_panel():
    html_buffer = io.StringIO()
    panel_app.save(html_buffer, embed=True)
    html_content = html_buffer.getvalue()
    html_buffer.close()
    return HTMLResponse(content=html_content)
