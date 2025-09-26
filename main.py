from bokeh.core.enums import SizingMode
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import panel as pn
from fastapi.responses import RedirectResponse
from param.parameterized import instance_descriptor
import vtk
from panel.pane import VTK
import vtkmodules
import vtkmodules.vtkRenderingCore
import utils
import vtk_core
import time
import httpx

app = FastAPI()

pn.extension('vtk')

options = ["cube", "sphere", "cone"]


render_window = vtk_core.VtkManager.Create_vtk('cube')
vtk_pane = pn.pane.VTK(render_window,sizing_mode='stretch_both')

seldrop = pn.widgets.Select(name='选择几何体', options=options, value='cube')
output = pn.widgets.StaticText(name="显示选项", value="显示立方体")
colorpicker = pn.widgets.ColorPicker(name='背景颜色', value='#99ef78',sizing_mode='stretch_width')
buttonReC = pn.widgets.Button(name = '重置摄像机位置',sizing_mode='stretch_width')
buttonflash = pn.widgets.Button(name = '刷新',sizing_mode='stretch_width')


vtk_pane.get_renderer().SetBackground(utils.hex_to_rgb('#99ef78')) #type:ignore




@pn.depends(seldrop.param.value,watch=True)
def update_vtk(value):
    if value == "cube":
        render_ = vtk_core.VtkManager.Create_vtk('cube')
        output.value = "显示立方体"
    elif value == "sphere":
        render_ = vtk_core.VtkManager.Create_vtk('sphere')
        output.value = "显示球体"
    elif value == "cone":
        render_ = vtk_core.VtkManager.Create_vtk('cone')
        output.value = "显示圆锥体"
    if vtk_pane is not None : 
        vtk_pane.object = render_
        vtk_pane.get_renderer().SetBackground(utils.hex_to_rgb(colorpicker.value)) #type:ignore
        time.sleep(0.01) #两次更新之间需要等待一会 不然会无法显示
        vtk_pane.param.trigger('object')
        

def reset_camera(event):
    if vtk_pane is not None:
        assert isinstance(vtk_pane, pn.pane.vtk.vtk.VTKRenderWindowSynchronized)
        renderer = vtk_pane.get_renderer()
        assert isinstance(renderer, vtkmodules.vtkRenderingCore.vtkRenderer)
        renderer.ResetCamera()
        vtk_pane.param.trigger('object')
buttonReC.on_click(reset_camera)

def flash(event):
        vtk_pane.param.trigger('object') #type:ignore
buttonflash.on_click(flash)


@pn.depends(colorpicker.param.value,watch=True)
def update_bgcolor(value):
    assert isinstance(vtk_pane, pn.pane.vtk.vtk.VTKRenderWindowSynchronized)
    render =  vtk_pane.get_renderer()
    assert isinstance(render, vtkmodules.vtkRenderingCore.vtkRenderer)
    render.SetBackground(utils.hex_to_rgb(value))
    vtk_pane.param.trigger('object') #显式更新


template = pn.template.FastListTemplate(
    title="VTK SHOW",
    sidebar=[seldrop,output,colorpicker,buttonReC,buttonflash],
    main=[vtk_pane],
)

pn.serve(
    template,
    port=5006,
    allow_websocket_origin=["127.0.0.1:5006", "localhost:5006"],  
    show=False,
    )

@app.get("/panel")
def serve_panel():
    return RedirectResponse(url="http://127.0.0.1:5006")\
