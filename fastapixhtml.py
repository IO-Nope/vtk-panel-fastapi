from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

app = FastAPI()

# 静态文件目录（CSS 和 JS）
app.mount("/static", StaticFiles(directory="static"), name="static")

# 模板目录（HTML 文件）
templates = Jinja2Templates(directory="templates")

# 数据模型
class InputData(BaseModel):
    seldrop: str


# 路由：返回 HTML 页面
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# 路由：处理前端发送的数据
@app.post("/api/data")
async def handle_data(data: InputData):
    print("收到的数据：", data)
    # 返回处理后的数据
    return {"message": "数据已处理", "received": data.model_dump()}