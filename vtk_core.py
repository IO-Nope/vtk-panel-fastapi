import vtk
import utils
from queue import Queue


# vtk有时会资源复用爆错 ，所以用单例模式管理
class VtkManager:
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
    def Create_vtk(cls,type = 'cube'):
        instance = cls.Instance()
        if type in instance.__dicpool:
            return instance.__dicpool[type]
        if len(instance.__dicpool) >= instance.__maxobject:
            logout = cls.__logout.get()
            instance.__dicpool.pop(logout)
        if type == 'cone':
            render_window = utils.Create_vtk_cone()
        elif type == 'sphere':
            render_window = utils.Create_vtk_sphere()
        else:
            render_window = utils.Create_vtk_cube()
        instance.__dicpool[type] = render_window
        return render_window