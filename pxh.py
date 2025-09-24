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

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


pn.extension()
pn.config.css_files = ["/static/styles.css"]
# 定义 Panel 组件
slider = pn.widgets.FloatSlider(name="滑块", start=0, end=100, step=1, value=50)
output = pn.widgets.StaticText(name="显示值", value=str(slider.value))

panel_layout = pn.Column(
    slider,
    output
)
# 加载静态 HTML 文件
with open("templates/index.html", "r", encoding="utf-8") as f:
    html_content = f.read()
# 替换占位符，将 Panel 组件插入到 HTML 中
html_with_panel = html_content.replace(
    '<div id="panel-component"></div>',
    utils.Tohtml(panel_layout)  # 将 Panel 组件渲染为 HTML
)

# 创建 Panel HTML 面板
html_pane = pn.pane.HTML(html_with_panel)
html_silder = pn.pane.HTML(utils.Tohtml(slider))

@pn.depends(slider.param.value, watch=True)
def update_output(value):
    output.value = str(value)

# 显示应用
@app.get("/panel", response_class=HTMLResponse)
async def serve_panel(request: Request):
    return html_with_panel

@app.get("/html", response_class=HTMLResponse)
async def serve_html(request: Request):
    return utils.Tohtml(panel_layout)


