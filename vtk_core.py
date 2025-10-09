from pooch import create
import vtk
import utils
from queue import Queue
import vtkmodules.vtkRenderingCore
import math
import threading
import time
from typing import Union,Callable

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
    def Create_vtk(cls,type = 'Any',length=5.0,width=5.0,height=5.0,radius=5.0,n_elem=10,pdata=None):
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
            case 'mesh':
                coords, elements = utils.gen_mesh_from_elements(n_elem,length,width,height)
                render_window = instance.build_vtk_from_mesh(coords, elements, point_data=pdata)  
            case any:
                render_window = instance.Create_cube()
        instance.__dicpool[type] = render_window
        return render_window
    
    @staticmethod
    def build_vtk_from_mesh(coords, elements, point_data=None):
        """
        将 coords(节点坐标)、elements(8点索引列表) 转为 vtkRenderWindow（包含 actor）
        point_data: 可选 list/np.array，对应每个节点的标量场（如应力）
        返回 vtkRenderWindow
        """
        points = vtk.vtkPoints()
        for p in coords:
            points.InsertNextPoint(p)
        ugrid = vtk.vtkUnstructuredGrid()
        ugrid.SetPoints(points)
        for elm in elements:
            hex_cell = vtk.vtkHexahedron()
            for idx_local, pid in enumerate(elm):
                hex_cell.GetPointIds().SetId(idx_local, int(pid))
            ugrid.InsertNextCell(hex_cell.GetCellType(), hex_cell.GetPointIds())
        if point_data is not None:
            arr = vtk.vtkFloatArray()
            arr.SetName("Scalar")
            for v in point_data:
                arr.InsertNextValue(float(v))
            ugrid.GetPointData().AddArray(arr)
            ugrid.GetPointData().SetActiveScalars("Scalar")
        # mapper/actor/renderer -> render window
        mapper = vtk.vtkDataSetMapper()
        mapper.SetInputData(ugrid)
        if point_data is not None:
            mapper.SetScalarRange(min(point_data), max(point_data))
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().EdgeVisibilityOn()
        renderer = vtk.vtkRenderer()
        renderer.AddActor(actor)
        renwin = vtk.vtkRenderWindow()
        renwin.AddRenderer(renderer)
        return renwin
    

#todo:一个效果器 要提供一个和有限元计算对接的接口，自适应的时间更新
class Vtkeffector():
    '''
    vtk指定actor效果器，update是更新函数
    #todo:实现一个效果器基类或者接口 让子类可以调用update
    '''



    def __init__(self, steps, actor, iren):
        self.steps = steps
        self.actor = actor
        self.iren = iren
    
    def update(self):
        pass


#todo:一个定时触发器

class NNtimer:
    '''
    一个定时器的类，所有的时间请以秒为单位，eff是绑定的函数或者效果器，如果是效果器会默认调用update方法，
    '''
    __total_time : float
    __cycle : float
    __isloop : bool
    __isrunning :bool
    __close : bool


    __timer : float #内置计时器
    __effector : Union[Callable,Vtkeffector]

    __lock = threading.Lock()
    __runcond = threading.Condition()
    #两个锁，有点蠢，不确定，再看看



    def __init__(self,eff:Union[Callable,Vtkeffector],total_time = 10, cycle = 0.5, isloop = False):
        self.__total_time = total_time
        self.__cycle = cycle
        self.__effector = eff
        self.__isloop = isloop
        self.__close = False
        self.__timer = 0
        self.__isrunning = True

    def __tar(self):
        while(1):
            start_real = time.perf_counter()

            if isinstance(self.__effector,Vtkeffector):
                self.__effector.update()
            else : 
                self.__effector()
            
            end_real = time.perf_counter()
            pass_time  = end_real - start_real

            add_time = 0
            if pass_time < self.__cycle:
                last_time = self.__cycle - pass_time
                add_time = self.__cycle
            else:
                last_time =0
                print("Warn: NNtimer can't Keep up!")
                add_time= pass_time

            with self.__lock:
                self.__timer+=add_time
            
            if not self.__isloop :
                if self.__timer>= self.__total_time:
                    break
            with self.__lock:
                temp = self.__isrunning
            #避免两个锁一起用导致deadlock


            if not temp :
                self.__runcond.wait()
                if self.__close:
                    self.__close = False
                    break
            
            
            time.sleep(last_time)

            


    def Start(self):
        if not self.__isrunning:
            self.__runcond.notify_all()
            #可能有问题
            self.__isrunning = True
        if self.__timer :
            return
        t=threading.Thread(target=self.__tar)
        t.start()

    def Stop(self):
        with self.__lock:
            self.__isrunning = False

    def Reset(self):
        with self.__lock:
            self.__isrunning=False
            self.__timer = 0
            self.__close = True

    def __del__(self):
        pass




