from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import panel as pn
import vtk
from panel.pane import VTK
import io

# 初始化 FastAPI 应用
app = FastAPI()

# 初始化 Panel
pn.extension('vtk')

# 创建 VTK 场景
def create_vtk_cube():
    # 创建一个立方体
    cube_source = vtk.vtkCubeSource()
    cube_source.SetXLength(1.0)
    cube_source.SetYLength(1.0)
    cube_source.SetZLength(1.0)
    cube_source.Update()

    # 创建 Mapper
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(cube_source.GetOutputPort())

    # 创建 Actor
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    # 设置颜色
    colors = vtk.vtkNamedColors()
    actor.GetProperty().SetColor(colors.GetColor3d("CornflowerBlue"))

    # 创建 Renderer
    renderer = vtk.vtkRenderer()
    renderer.AddActor(actor)
    renderer.SetBackground(colors.GetColor3d("DarkSlateGray"))

    # 创建 Render Window
    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(renderer)

    # 创建 Render Window Interactor
    render_window_interactor = vtk.vtkRenderWindowInteractor()
    render_window_interactor.SetRenderWindow(render_window)

    return render_window

# 创建 Panel 应用
def create_panel_app():
    render_window = create_vtk_cube()
    vtk_pane = VTK(render_window)  # 使用 Panel 的 VTK Pane
    return pn.Column("# 立方体展示", vtk_pane)

panel_app = create_panel_app()

# FastAPI 路由：嵌入 Panel 应用
@app.get("/panel", response_class=HTMLResponse)
def serve_panel():
    html_buffer = io.StringIO()
    panel_app.save(html_buffer, embed=True)
    html_content = html_buffer.getvalue()
    html_buffer.close()
    return HTMLResponse(content=html_content)
