from os import name
import re
from fastapi import FastAPI, background
from fastapi.responses import HTMLResponse
from numpy import isin
import panel as pn
from fastapi.responses import RedirectResponse
from panel.io import notifications
from panel.io.notifications import NotificationAreaBase
from panel.pane.vtk.vtk import VTKRenderWindowSynchronized
from panel.template import DarkTheme
from panel.widgets.speech_to_text import Language
from vtkmodules.vtkRenderingCore import vtkRenderWindow, vtkRenderer, vtkActor, vtkPolyDataMapper
import vtk
import vtkmodules
import vtkmodules.vtkRenderingCore
import utils
from utils import Dprint
import vtk_core
from typing import Optional
import time
import math
from panel.io.server import get_server


#region 初始panel设置
pn.extension('vtk',notifications=True)
assert isinstance(pn.state.notifications, NotificationAreaBase)
def notification(type='info',message:str = "This is a notification message",position='top-right',duration=3000):
    assert isinstance(pn.state.notifications, NotificationAreaBase)
    pn.state.notifications.position = position
    if type == 'info':
        pn.state.notifications.info(message,duration=duration)
    elif type == 'warning':
        pn.state.notifications.warning(message,duration=duration)
    elif type == 'error':
        pn.state.notifications.error(message,duration=duration)
    elif type == 'success':
        pn.state.notifications.success(message,duration=duration)
    else:
        pn.state.notifications.info(message+"未指定的提示类型",duration=duration)

#endregion
page = pn.template.FastListTemplate(title = "梁加载破坏可视化")
vtk_pane = pn.pane.VTK(vtk_core.VtkManager.Create_vtk(type='cube',length=5.0,width=0.5,height=0.5),sizing_mode='stretch_both')



#region sidebar
#region 全局变量
renderer = vtk_pane.object.GetRenderers().GetFirstRenderer() #type:ignore
assert isinstance(renderer, vtkmodules.vtkRenderingCore.vtkRenderer)
initial_camera = renderer.GetActiveCamera()
init_cam_pos = {'position': [10, 0, 0], 'focalPoint': [0, 0, 0], 'viewUp': [0, 1, 0], 'parallelProjection': False, 'useHorizontalViewAngle': False, 'viewAngle': 30, 'parallelScale': 1, 'clippingRange': [9.353450634738618, 10.837993045215962], 'windowCenter': [0, 0], 'useOffAxisProjection': False, 'screenBottomLeft': [-0.5, -0.5, -0.5], 'screenBottomRight': [0.5, -0.5, -0.5], 'screenTopRight': [0.5, 0.5, -0.5], 'freezeFocalPoint': False, 'projectionMatrix': None, 'viewMatrix': None, 'physicalTranslation': [0, 0, 0], 'physicalScale': 1, 'physicalViewUp': [0, 1, 0], 'physicalViewNorth': [0, 0, -1], 'mtime': 1010, 'remoteId': '0000018facbaa370', 'distance': 10, 'focal_point': [2.5, 0.25, 0], 'view_up': [0, 1, 0]}
is_running = False




assert isinstance(vtk_pane, VTKRenderWindowSynchronized)
vtk_pane.camera = init_cam_pos

init_actor_pos : Optional[dict[str,tuple[float,float,float]]] = None

last_beam_size = [5.0,0.5,0.5]

precision = 5  

#endregion
#region 功能栏
#region 必要参数
width_input = pn.widgets.FloatInput(name="宽度/m", value=0.5, step=0.1,sizing_mode='stretch_width')
length_input = pn.widgets.FloatInput(name="跨度/m", value=5.0, step=1,sizing_mode='stretch_width')
height_input = pn.widgets.FloatInput(name="梁高/m", value=0.5, step=0.1,sizing_mode='stretch_width')
density_input = pn.widgets.FloatInput(name="重度/kN/m^2", value=25.0, step=1,sizing_mode='stretch_width')
E_input = pn.widgets.FloatInput(name="弹性模量/MPa", value=20000.0, step=1000,sizing_mode='stretch_width')
race_input = pn.widgets.FloatInput(name='加载速度/Mpa/s',value=0.1,step=0.01,sizing_mode='stretch_width')
limnum_input =pn.widgets.IntInput(name="有限元数量",value=10,step=1,sizing_mode='stretch_width')
factor_input = pn.Column(
    pn.Row(length_input, height_input,width_input,sizing_mode='stretch_width'),
    pn.Row(density_input,E_input,sizing_mode='stretch_width'),
    pn.Row(race_input,limnum_input,sizing_mode='stretch_width')
)

#endregion
#region 功能按钮
buttonGen = pn.widgets.Button(name = '生成',sizing_mode='stretch_width')
buttonProcess = pn.widgets.Button(name = '开始加载',sizing_mode='stretch_width')
buttonStopKeepon = pn.widgets.Button(name = '停止/继续',sizing_mode='stretch_width')
buttonReset = pn.widgets.Button(name = '重置',sizing_mode='stretch_width')
buttonRow = pn.Column(
    buttonGen,
    pn.Row(buttonProcess,buttonStopKeepon,sizing_mode='stretch_width'),
    buttonReset,
    sizing_mode='stretch_width'
)

#endregion
#region 回调函数

def gen_vtk(event):
    #To Do:计算需要的参数 生成vtk图像
    global vtk_pane
    global init_cam_pos
    global last_beam_size


    W = width_input.value
    L = length_input.value
    H = height_input.value
    assert isinstance(L, (int,float))
    assert isinstance(H, (int,float))
    assert isinstance(W, (int,float))
    #pylance闹麻

    for i in range(3):
        if last_beam_size[i] != [L,H,W][i]:
            break
    else:
        notification('error',"几何体尺寸未改变，无需重新生成")
        return
    
    last_beam_size = [L,H,W]
    

    render_window = vtk_core.VtkManager.Create_cube(length=L,width=W,height=H)
   
    #Issue: 这里本来是先判断page.main[0]是否为vtkrenderwindowsynchronized的 
    #然后page.main.clear()再 page.main.append(vtk_pane)
    #点击按钮后页面不更新
    #尝试过手动trigger page.param.trigger('main') , vtk_pane.param.trigger('object')，  page.serable() 都没效果

    assert isinstance(page.main,pn.layout.base.ListLike)
    render_window.GetRenderers().GetFirstRenderer().SetBackground(utils.hex_to_rgb(background_colorpick.value)) #type:ignore
    assert isinstance(vtk_pane, VTKRenderWindowSynchronized)
    vtk_pane.object = render_window
    time.sleep(0.1) #等待渲染器更新
    notification('success',"已生成梁几何体")
    reset_camera(None)
    #To Do:刷新！为什么不能做到！

buttonGen.on_click(gen_vtk)

def process_vtk(event):
    notification('info',"开始加载")
    #todo:开始加载并展示动画
    notification('error',"功能开发中，敬请期待")
    pass
buttonProcess.on_click(process_vtk)


def stopkeepon_vtk(event):
    notification('error',"功能开发中，敬请期待")
    pass
buttonStopKeepon.on_click(stopkeepon_vtk)

def resert_vtk(event):
    notification('error',"功能开发中，敬请期待")
    pass
buttonReset.on_click(resert_vtk)

def flash_vtk(event):
    global vtk_pane
    if vtk_pane is not None:
        vtk_pane.param.trigger('object') #type:ignore

def reset_vtk(event):
    global vtk_pane
    global init_cam_pos
    if vtk_pane is None:
        notification('error',"请先生成梁几何体")
        return
    assert isinstance(vtk_pane, VTKRenderWindowSynchronized)
    
buttonReset.on_click(reset_vtk)

def num_correct(event):
    #消除级小数误差
    step = event.obj.step
    factor = 10e-5 * step
    event.obj.value = round(event.obj.value / step) * step
    #取值范围
    if event.obj.value < 0:
        event.obj.value = 0
        notification('warning',f"{event.obj.name.split('/')[0]}不能为负数，已重置为0")
        return
    
width_input.param.watch(num_correct,'value')
length_input.param.watch(num_correct,'value')
height_input.param.watch(num_correct,'value')
density_input.param.watch(num_correct,'value')
E_input.param.watch(num_correct,'value')
race_input.param.watch(num_correct,'value')
limnum_input.param.watch(num_correct,'value')


#endregion
functionTab = pn.Column(
    factor_input,
    buttonRow,
)
#endregion
#region 视图栏
#region 视图控件
background_colorpick = pn.widgets.ColorPicker(name='背景颜色', value='#FFFFFF',sizing_mode='stretch_width')
button_camera_reset = pn.widgets.Button(name = '重置摄像机',sizing_mode='stretch_width')


#endregion
#region 回调函数
@pn.depends(background_colorpick.param.value,watch=True)
def set_vtkbackground_color(value):
    global vtk_pane
    if vtk_pane is None:
        notification('error',"请先生成几何体")
        return
    assert isinstance(vtk_pane, VTKRenderWindowSynchronized)
    render =  vtk_pane.get_renderer()
    assert isinstance(render, vtkmodules.vtkRenderingCore.vtkRenderer)
    render.SetBackground(utils.hex_to_rgb(value)) #type:ignore
    vtk_pane.param.trigger('object') #显式更新
    notification('info',f"已设置背景颜色为{value}")

def reset_camera(event):
    global vtk_pane
    if vtk_pane is None:
        notification('error',"请先生成几何体")
        return
    assert isinstance(vtk_pane, VTKRenderWindowSynchronized)
    vtk_pane.camera = init_cam_pos
    vtk_pane.param.trigger('object')
    notification('info',"已重置摄像机位置")

button_camera_reset.on_click(reset_camera)

#endregion

viewTab = pn.Column(
    button_camera_reset,
    background_colorpick,
)

#endregion
#region 开发者功能栏
button_print_camera_pos = pn.widgets.Button(name = '打印摄像机位置',sizing_mode='stretch_width')
button_function_test = pn.widgets.Button(name = '测试功能',sizing_mode='stretch_width')

#region 回调函数

def print_camera_pos(event):
    global vtk_pane
    if vtk_pane is None:
        assert isinstance(pn.state.notifications, NotificationAreaBase)
        notification('error',"请先生成几何体")
        return
    assert isinstance(vtk_pane, VTKRenderWindowSynchronized)
    camera = vtk_pane.camera
    assert isinstance(camera, dict)
    assert isinstance(pn.state.notifications, NotificationAreaBase)
    notification('info',f"摄像机位置：{camera}")
button_print_camera_pos.on_click(print_camera_pos)




def function_test(event):

    notification('info',"成功触发测试功能")
button_function_test.on_click(function_test)


#endregion

devtab = pn.Column(
    button_print_camera_pos,
    button_function_test,
)
#endregion

assert isinstance(page.sidebar,pn.layout.base.ListLike)
page.sidebar.append(
    pn.Tabs(
        ('功能', functionTab),
        ('视图', viewTab),
        ('开发者功能', devtab)
    )
)

#endregion

#region main(template)

assert isinstance(page.main,pn.layout.base.ListLike)
page.main.append(
    vtk_pane
)
# Issue: 在这里添加markdown先占据main 先不加vtk_pane
# page.main.append(
#     pn.pane.Markdown("""
# # <center> 请在左边仪表盘生成对象    
#                      """)
# )

#endregion
#region 网关部分
app = FastAPI()
server = pn.serve(
        page,
        port=5006,
        show=False,
        start=False
    )
server.start()

@app.get("/visualbeam")
def serve_root():
    html = """
    <!DOCTYPE html>
    <html lang="en" style="height:100%;">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Panel App</title>
        <style>
            html, body {
                height: 100%;
                margin: 0;
                padding: 0;
            }
            body {
                height: 100%;
                width: 100%;
                overflow: hidden;
            }
            iframe {
                height: 100%;
                width: 100%;
                border: none;
                display: block;
            }
        </style>
    </head>
    <body>
        <iframe src="http://localhost:5006"></iframe>
    </body>
    </html>
    """
    return HTMLResponse(content=html)
    

#endregion