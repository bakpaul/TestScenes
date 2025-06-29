import rpyc
import time
import threading
import Sofa
import importlib.util
import pathlib
import numpy as np
from multiprocessing import shared_memory
import operator

class SOFAService(rpyc.SlaveService):

    class SharedMemoryInfo():
        def __init__(self,shape, dtype, sharedMem):
            self.shape = shape
            self.dtype = dtype
            self.sharedMem = sharedMem
            
        def getSharedName(self):
            return self.sharedMem.name

        def getDataInfo(self):
            return {"shape" : self.shape, "dtype" : self.dtype}


    class SOFASharedMemoryProxy():

        def __init__(self,parent):
            self.parent = parent
            self.items = []

        #This method is called when the return object is of this proxy type
        def get_data(self):
            caller =  operator.attrgetter(".".join(self.items))                                          
            return caller(self.parent.exposed_sofa_root)
            

        def shared_data_name(self):
            name = ""
            if len(self.items) != 0 :
               
                for compName in self.items[:-1]:
                    name += f"/{compName}"
                
                if name != "":
                    name += '.'
                
                name += self.items[-1]

            return name

        #If this method is called, then it means the used called a method of one of the sofa object, then just return the result and let rpyc deal with it
        def __call__(self, *args, **kwds):
            caller =  operator.attrgetter(".".join(self.items))                                          
            return caller(self.parent.exposed_sofa_root).__call__(*args,**kwds)
            
        

        def getattr(self,item):
            shared_name = self.shared_data_name()
            
            #If this is true then someone tried to access the value of a shared data, the copy it and return the shared info
            if(shared_name in self.parent.sharedPaths and item == "value"):
                self.parent.copy_shared_data_into_memory(shared_name)
                return self.parent.sharedPaths(shared_name)
            
            self.items.append(item)    
            return self
        

    exposed_sofa_root : Sofa.Core.Node

    
    def __init__(self, *args, **kwargs):
        rpyc.Service.__init__(self,*args, **kwargs)
        self.animationThread = None
        self.sharedMemory = None

    def on_connect(self, conn):
        self.exposed_sofa_root = Sofa.Core.Node("root")
        self.animate = False
        pass

    def on_disconnect(self, conn):
        self.exposed_pause_simulation()
        for sm in self.sharedMemory:
            sm.sharedMem.unlink()
            sm.sharedMem.close()

    def exposed_build_scene_graph_from_method(self, createScene):
        self.exposed_sofa_root = Sofa.Core.Node("root")
        createScene(self.exposed_sofa_root)
        Sofa.Simulation.initRoot(self.exposed_sofa_root)


    def exposed_build_scene_graph_from_file(self, filename:str):

        moduleName = pathlib.Path(filename).name.split('.')[0]
        spec=importlib.util.spec_from_file_location(moduleName,filename)
        foo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(foo)

        self.exposed_sofa_root = Sofa.Core.Node("root")
        foo.createScene(self.exposed_sofa_root)
        Sofa.Simulation.initRoot(self.exposed_sofa_root)

    def __internal_getattr(self, path):
        paths = path.split('/')
        dataName = paths[-1].split('.')[1]
        paths[-1] = paths[-1].split('.')[0]

        caller =  operator.attrgetter(".".join(paths))                                          

        return caller(self.exposed_sofa_root).value

    def exposed_setup_shared_memory_for_data(self, dataPaths:list[str], delayed=False):
        self.paths_for_shared_mem = dataPaths
        if(not delayed):
            self.paths_for_shared_mem = self.__internal_setup_shared_memory()

    def __internal_setup_shared_memory(self):
        self.sharedMemory = []
        self.sharedPaths = {}
        for paths in self.paths_for_shared_mem:
            data = self.__internal_getattr(paths)
            if( isinstance(data, np.ndarray)):
                print(f"Sharing {data.size*data.itemsize} bytes for data {paths}")
                self.sharedMemory.append(SOFAService.SharedMemoryInfo(data.shape, data.dtype, shared_memory.SharedMemory(create=True, size=data.size*data.itemsize)))
                self.sharedPaths[paths] = self.sharedMemory[-1].name
            else:
                print(f"Not creating a shared memory for data {paths} because it is no a numpy array")
        return self.sharedPaths

    def getSharedMemoryNames(self):
        return self.sharedPaths


    def __wait_for_the_animation_to_stop(self):
        if(self.animationThread is not None and self.animationThread.is_alive()):
            self.animationThread.join()


    def __simulation_loop(self):
        while self.animate:
            Sofa.Simulation.animate(self.exposed_sofa_root, self.exposed_sofa_root.dt.value)
    
    
    def exposed_start_simulation(self):
        if(self.animate):
            return
        
        self.__wait_for_the_animation_to_stop()

        self.animate=True
        self.simulationThread = threading.Thread(target = self.__simulation_loop)
        self.simulationThread.start()

        
    def exposed_pause_simulation(self):
        self.animate = False
        self.__wait_for_the_animation_to_stop()
        
    
    def exposed_reset_simulation(self):
        need_restart = False
        if(self.animate):
            need_restart = True

        self.animate = False
        self.__wait_for_the_animation_to_stop()

        Sofa.Simulation.reset()
        
        if(need_restart):
            self.exposed_start_simulation()

    def exposed_step_simulation(self):
        Sofa.Simulation.animate(self.exposed_sofa_root, self.exposed_sofa_root.dt.value)

        
        
