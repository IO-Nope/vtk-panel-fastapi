from fastapi.responses import HTMLResponse
import panel as pn
from panel.io.notifications import NotificationAreaBase
from panel.pane.vtk.vtk import VTKRenderWindowSynchronized
from panel.template import DarkTheme
from panel.widgets.speech_to_text import Language
from vtkmodules.vtkRenderingCore import vtkRenderWindow, vtkRenderer, vtkActor, vtkPolyDataMapper
import vtkmodules
import vtkmodules.vtkRenderingCore
import utils
from utils import Dprint
import vtk_core
import time
import math
from panel.io.server import get_server
pn.extension('vtk',notifications=True)

def notification(type='info',message:str = "This is a notification message",position='top-right',duration=3000):
    '''
    通知提示
    '''
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

class BeamPage:
    page = pn.template.MaterialTemplate(title='素混凝土梁四点加载可视化',theme=DarkTheme)
    __vtk_pane = pn.pane.VTK(vtk_core.VtkManager.Create_vtk(type='mesh',length=5.0,width=0.5,height=0.5,n_elem=10),sizing_mode='stretch_both')
    __init_campos = {
        'position': [2.5, 0.25, 10.005372652697917], 
        'focalPoint': [2.5, 0.25, 0.25], 
        'viewUp': [0, 1, 0], 
        'parallelProjection': False, 
        'useHorizontalViewAngle': False, 
        'viewAngle': 30, 
        'parallelScale': 1, 
        'clippingRange': [9.124313553240633, 10.573276588815226], 
        'windowCenter': [0, 0], 
        'useOffAxisProjection': False, 
        'screenBottomLeft': [-0.5, -0.5, -0.5], 
        'screenBottomRight': [0.5, -0.5, -0.5], 
        'screenTopRight': [0.5, 0.5, -0.5], 
        'freezeFocalPoint': False, 
        'projectionMatrix': None, 
        'viewMatrix': None, 
        'physicalTranslation': [0, 0, 0], 
        'physicalScale': 1, 
        'physicalViewUp': [0, 1, 0], 
        'physicalViewNorth': [0, 0, -1], 
        'mtime': 49, 
        'remoteId': '00000214ab4e9be0', 
        'distance': 9.755372652697917
        }
    __is_running = False
    __last_beam_size = [5.0,0.5,0.5,10] #L,H,W,n_elem
    __widgets = {}
    __precision = 5
    def __func_tab_init(self):
        '''
        功能区初始化
        '''
        #region 输入参数
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
        self.__widgets.update(
            {
                'width': width_input,
                'length': length_input,
                'height': height_input,
                'density': density_input,
                'E': E_input,
                'race': race_input,
                'limnum': limnum_input
            }
        )
        #endregion
        #region 运行按钮
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

        self.__widgets.update(
            {
                'buttonGen': buttonGen,
                'buttonProcess': buttonProcess,
                'buttonStopKeepon': buttonStopKeepon,
                'buttonReset': buttonReset
            }
        )
        #endregion
        functionTab = pn.Column(
            factor_input,
            buttonRow,
            sizing_mode='stretch_width'
            )
        
        Dprint('Info:Beam page function tab initialized.')
        return functionTab
    
    def __view_tab_init(self):
        '''
        视图区初始化
        '''
        background_colorpick = pn.widgets.ColorPicker(name='背景颜色', value='#FFFFFF',sizing_mode='stretch_width')
        button_camera_reset = pn.widgets.Button(name = '重置摄像机',sizing_mode='stretch_width')

        self.__widgets.update(
            {
                'background_colorpick': background_colorpick,
                'button_camera_reset': button_camera_reset
            }
        )

        viewTab = pn.Column(
            background_colorpick,
            button_camera_reset,
            sizing_mode='stretch_width'
        )

        Dprint('Info:Beam page view tab initialized.')
        return viewTab
    
    def __dev_tab_init(self):
        '''
        开发者功能区初始化
        '''
        button_print_camera_pos = pn.widgets.Button(name = '打印摄像机位置',sizing_mode='stretch_width')
        button_function_test = pn.widgets.Button(name = '测试功能',sizing_mode='stretch_width')
        devTab = pn.Column(
            button_print_camera_pos,
            button_function_test,
        )
        self.__widgets.update(
            {
                'button_print_camera_pos': button_print_camera_pos,
                'button_function_test': button_function_test
            }
        )
        Dprint('Info:Beam page developer tab initialized.')
        return devTab
    
    def __sidebar_init(self):
        '''
        侧边栏初始化
        '''
        tabs = pn.Tabs(
            ('功能',self.__func_tab_init()),
            ('视图',self.__view_tab_init()),
            ('开发者功能',self.__dev_tab_init()),
            sizing_mode='stretch_width'
        )
        sidebar = pn.Column(
            tabs,
            sizing_mode='stretch_height'
        )
        assert isinstance(self.page.sidebar, pn.layout.base.ListLike)   
        self.page.sidebar.append(sidebar)
        Dprint('Info:Beam page sidebar initialized.')

    def __main_init(self):
        assert isinstance(self.page.main,pn.layout.base.ListLike)
        self.__vtk_pane.object.GetRenderers().GetFirstRenderer().SetBackground(utils.hex_to_rgb('#FFFFFF')) #type:ignore
        self.page.main.append(
            self.__vtk_pane
        )
        Dprint('Info:Beam page main area initialized.')
        
    def __bind_events(self):
        #region 别名
        background_colorpick = self.__widgets.get('background_colorpick',None)
        button_camera_reset = self.__widgets.get('button_camera_reset',None)
        vtk_pane = self.__vtk_pane
        init_cam_pos = self.__init_campos
        last_beam_size = self.__last_beam_size
        buttonGen = self.__widgets.get('buttonGen',None)
        buttonProcess = self.__widgets.get('buttonProcess',None)
        buttonStopKeepon = self.__widgets.get('buttonStopKeepon',None)
        buttonReset = self.__widgets.get('buttonReset',None)
        width_input = self.__widgets.get('width',None)
        length_input = self.__widgets.get('length',None)
        height_input = self.__widgets.get('height',None)
        density_input = self.__widgets.get('density',None)
        E_input = self.__widgets.get('E',None)
        race_input = self.__widgets.get('race',None)
        limnum_input = self.__widgets.get('limnum',None)
        button_print_camera_pos = self.__widgets.get('button_print_camera_pos',None)
        button_function_test = self.__widgets.get('button_function_test',None)
        #endregion
        #region 变量断言
        assert isinstance(vtk_pane, VTKRenderWindowSynchronized)
        assert isinstance(background_colorpick, pn.widgets.ColorPicker)
        assert isinstance(button_camera_reset, pn.widgets.Button)
        assert isinstance(buttonGen, pn.widgets.Button)
        assert isinstance(buttonProcess, pn.widgets.Button)
        assert isinstance(buttonStopKeepon, pn.widgets.Button)
        assert isinstance(buttonReset, pn.widgets.Button)
        assert isinstance(width_input, pn.widgets.FloatInput)
        assert isinstance(length_input, pn.widgets.FloatInput)
        assert isinstance(height_input, pn.widgets.FloatInput)
        assert isinstance(density_input, pn.widgets.FloatInput)
        assert isinstance(E_input, pn.widgets.FloatInput)
        assert isinstance(race_input, pn.widgets.FloatInput)
        assert isinstance(limnum_input, pn.widgets.IntInput)
        assert isinstance(button_print_camera_pos, pn.widgets.Button)
        assert isinstance(button_function_test, pn.widgets.Button)
        #闹麻了
        #endregion
        #region 视图区

        @pn.depends(background_colorpick.param.value,watch=True)
        def set_vtkbackground_color(value):
            if vtk_pane is None:
                notification('error',"请先生成几何体")
                return
            
            render =  vtk_pane.get_renderer()
            assert isinstance(render, vtkmodules.vtkRenderingCore.vtkRenderer)
            render.SetBackground(utils.hex_to_rgb(value)) #type:ignore
            vtk_pane.param.trigger('object') #显式更新
            notification('info',f"已设置背景颜色为{value}")

        def reset_camera(event):
            if vtk_pane is None:
                notification('error',"请先生成几何体")
                return
            vtk_pane.camera = init_cam_pos
            vtk_pane.param.trigger('object')
            notification('info',"已重置摄像机位置")


        button_camera_reset.on_click(reset_camera)
        #endregion

        #region 功能区

        def gen_vtk(event):
            #To Do:计算需要的参数 生成vtk图像

            W = width_input.value
            L = length_input.value
            H = height_input.value
            N = limnum_input.value
            assert isinstance(L, (int,float))
            assert isinstance(H, (int,float))
            assert isinstance(W, (int,float))
            assert isinstance(N, int)
            #pylance闹麻

            for i in range(len(self.__last_beam_size)):
                if self.__last_beam_size[i] != [L,H,W,N][i]:
                    break
            else:
                notification('error',"几何体尺寸与有限元数量未改变，无需重新生成")
                return

            self.__last_beam_size = [L,H,W,N]
            assert isinstance(limnum_input.value,int)
            #todo:在这计算stress

            render_window = vtk_core.VtkManager.Create_vtk(type='mesh',length=L,width=W,height=H,n_elem=N)
        
            #Issue: 这里本来是先判断page.main[0]是否为vtkrenderwindowsynchronized的 
            #然后page.main.clear()再 page.main.append(vtk_pane)
            #点击按钮后页面不更新
            #尝试过手动trigger page.param.trigger('main') , vtk_pane.param.trigger('object')，  page.serable() 都没效果

            render_window.GetRenderers().GetFirstRenderer().SetBackground(utils.hex_to_rgb(background_colorpick.value)) #type:ignore
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
            if vtk_pane is not None:
                vtk_pane.param.trigger('object') #type:ignore

        def reset_vtk(event):
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
        #region 开发者功能区
        def print_camera_pos(event):
            if vtk_pane is None:
                notification('error',"请先生成几何体")
                return
            assert isinstance(vtk_pane, VTKRenderWindowSynchronized)
            camera = vtk_pane.camera
            assert isinstance(camera, dict)
            assert isinstance(pn.state.notifications, NotificationAreaBase)
            notification('info',f"摄像机位置：{camera}")
        button_print_camera_pos.on_click(print_camera_pos)

        animation_state = {"running": False, "color_value": 0.0, "increment": 0.01}

        def animate_vtk():
            if animation_state["running"]:
                # 颜色渐变（红到蓝）
                animation_state["color_value"] += animation_state["increment"]
                if animation_state["color_value"] > 1.0 or animation_state["color_value"] < 0.0:
                    animation_state["increment"] *= -1
                    animation_state["color_value"] += animation_state["increment"]
                r = 1.0 - animation_state["color_value"]
                g = 0.0
                b = animation_state["color_value"]
                # 获取第一个actor并设置颜色
                assert isinstance(vtk_pane, VTKRenderWindowSynchronized)
                assert isinstance(vtk_pane.object,vtkRenderWindow)
                renderer = vtk_pane.object.GetRenderers().GetFirstRenderer()
                actor = renderer.GetActors().GetLastActor()
                actor.GetProperty().SetColor(r, g, b)
                vtk_pane.param.trigger('object')  # 刷新显示

        cb = pn.state.add_periodic_callback(animate_vtk, period=50)
        cb.stop()  # 初始时停止动画

        def function_test(event):
            animation_state["running"] = not animation_state["running"]
            if animation_state["running"]:
                cb.start()
            else:
                cb.stop()
            notification('info',"成功触发测试功能")
        button_function_test.on_click(function_test)
        #endregion

    def __init__(self):
        self.__sidebar_init()
        self.__main_init()
        self.__bind_events()

        Dprint('Info:Beam page initialized.')