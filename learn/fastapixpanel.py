from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from jinja2.utils import F
import panel as pn
import io

# 初始化 FastAPI 应用
app = FastAPI()

# 初始化 Panel
pn.extension()

# 创建一个简单的 Panel 应用
def create_panel_app():
    slider = pn.widgets.FloatSlider(name="滑块", start=0, end=10, step=0.1, value=5)
    text = pn.widgets.TextInput(name="输入框", placeholder="输入一些内容")
    button = pn.widgets.Button(name="提交", button_type="primary")

    # 动态更新
    @pn.depends(slider.param.value, watch=True)
    def update_text(value):
        text.value = f"滑块值: {value}"

    # 布局
    layout = pn.Column("# Panel 应用示例", slider, text, button)
    return layout

# 创建 Panel 应用
panel_app = create_panel_app()
button = pn.widgets.Button(name="测试",sizing_mode='stretch_width')

def button_callback(event):
    print("按钮被点击！")
button.on_click(button_callback)

pn_template = pn.template.FastListTemplate(title="FastAPI 与 Panel 集成示例",sidebar=[button], main=[panel_app])

# FastAPI 路由：嵌入 Panel 应用
@app.get("/panel", response_class=HTMLResponse)
async def serve_panel():
    # 将 Panel 应用转换为 HTML
    html_buffer = io.StringIO()
    pn_template.save(html_buffer, embed=False)
    html_content = html_buffer.getvalue()
    html_buffer.close()
    return HTMLResponse(content=html_content)

pn.serve(pn_template, port=5006, show=False, allow_websocket_origin=["*"])

@app.get("/")
def serve_root():
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Panel App</title>
    </head>
    <body>
        <iframe src="http://localhost:5006" width="100%" height="800px" frameborder="0"></iframe>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

# FastAPI 路由：提供 REST API 示例
@app.get("/api/hello")
def read_root():
    return {"message": "Hello, FastAPI and Panel!"}