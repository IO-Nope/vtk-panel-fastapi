from pooch import create
import vtk
import utils
from queue import Queue
import vtkmodules.vtkRenderingCore

# vtk有时会资源复用爆错 ，所以用单例模式管理，包揽计算任务
#todo:支持缓存，多线程计算和显卡加速
class VtkManager:
    '''
    VtkManager单例类用来管理vtk对象池,避免频繁创建和销毁vtk对象导致的资源浪费和性能问题。
    todo: 拓展vtk对象类型 增加hash函数
    '''
    __instance = None 
    __dicpool = {}
    __initialized = False
    __maxobject = 5
    __logout = Queue(maxsize=__maxobject)
    __count = 0
    
    @classmethod
    def Instance(cls):
        if cls.__instance is None:
            cls.__instance = VtkManager()
        return cls.__instance
    
    
    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(VtkManager, cls).__new__(cls)
        cls.__count += 1
        return cls.__instance
    
    def __init__(self):
        if not self.__initialized:
            self.__initialized = True
            # 
            self.init()
            
    def init(self):
        # Initialize VTK related settings if needed
        pass
    
    def __del__(self):
        # Cleanup resources if needed
        self.__count -= 1
        if self.__count <= 0:
            if VtkManager.__instance is not None:
                VtkManager.Instance().__dicpool.clear()
            
    
    @classmethod
    def Get_type(cls,type:str):
        instance = cls.Instance()
        res = instance.__dicpool.get(type,None)
        if res is  None:
            print("Warning: vtk_core pool type not found ")
        return res
        
    @classmethod
    def Create_cube(cls,length=5.0,width=5.0,height=5.0):
        instance = cls.Instance()
        W = length
        L = width
        H = height
        #pylance闹麻

        #region 生成vtk对象
        # 渲染器
        renderer = vtkmodules.vtkRenderingCore.vtkRenderer()

        # 梁的几何模型数据
        beam_source = vtk.vtkCubeSource()

        beam_source.SetXLength(L)
        beam_source.SetYLength(H)
        beam_source.SetZLength(W)
        beam_source.Update()

        # 创建梁的映射器和演员
        beam_mapper = vtk.vtkPolyDataMapper()
        beam_mapper.SetInputConnection(beam_source.GetOutputPort())

        beam_actor = vtk.vtkActor()
        beam_actor.SetMapper(beam_mapper)
        beam_actor.GetProperty().SetColor(0.8, 0.8, 0.8)  
        # 将梁添加到渲染器
        renderer.AddActor(beam_actor)

        # 设置背景颜色
        renderer.SetBackground(1, 1, 1)  # 白色背景

        # 创建 VTK 渲染窗口
        render_window = vtkmodules.vtkRenderingCore.vtkRenderWindow()
        render_window.AddRenderer(renderer)

        # 创建 VTK 渲染窗口交互器
        # render_window_interactor = vtkmodules.vtkRenderingCore.vtkRenderWindowInteractor()
        # render_window_interactor.SetRenderWindow(render_window)

        return render_window

    @classmethod
    def Create_vtk(cls,type = 'Any',length=5.0,width=5.0,height=5.0,radius=5.0):
        instance = cls.Instance()
        if type in instance.__dicpool:
            return instance.__dicpool[type]
        if len(instance.__dicpool) >= instance.__maxobject:
            logout = cls.__logout.get()
            instance.__dicpool.pop(logout)
        match type:

            case 'cone':
                render_window = utils.Create_vtk_cone()
            case 'sphere':
                render_window = utils.Create_vtk_sphere()
            case 'cube':
                render_window = instance.Create_cube(length,width,height)
            case any:
                render_window = instance.Create_cube()
        instance.__dicpool[type] = render_window
        return render_window
    
    #todo:一个效果器 要提供一个和有限元计算对接的接口，自适应的时间更新
class vtkeffector():
    '''
    vtk指定actor效果器，update是更新函数
    '''
    def __init__(self, steps, actor, iren):
        self.timer_count = 0
        self.steps = steps
        self.actor = actor
        self.iren = iren
    
    def update(self,obj,event):
        pass