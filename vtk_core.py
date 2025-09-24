import vtk

# vtk有时会资源复用爆错 ，所以用单例模式管理
class VtkManager:
    __instance = None 
    __dicpool = {}
    __initialized = False
    
    @classmethod
    def Instance(cls):
        if cls.__instance is None:
            cls.__instance = VtkManager()
        return cls.__instance
    
    
    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(VtkManager, cls).__new__(cls)
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
        pass
        