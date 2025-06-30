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

        def shared_data_name(self):
            name = ""
            if len(self.items) != 0 :
               
                for compName in self.items[:-1]:
                    name += f"{compName}."
                
                name += self.items[-1]

            return name

        #If this method is called, then it means the used called a method of one of the sofa object, then just return the result and let rpyc deal with it
        def __call__(self, *args, **kwds):
            caller =  operator.attrgetter(".".join(self.items))                                          
            return caller(self.parent.exposed_sofa_root).__call__(*args,**kwds)
            
        

        def __getattr__(self,item):
            shared_name = self.shared_data_name()
            
            #Check if until now we are still on the path of a tracked data
            tracked_data = False
            for path in self.parent.sharedPaths:
                if shared_name in path:
                    tracked_data = True
                    break

            #If we are exactly a tracked data and the value is accessed, then use shared memory
            if tracked_data and shared_name in self.parent.sharedPaths and item == "value":
                self.parent.copy_shared_data_into_memory(shared_name)
                shm = shared_memory.SharedMemory(name=self.parent.sharedMemory[shared_name].getSharedName())
                print(f"USING SHARED MEMORY {shared_name} as {str(self.parent.sharedMemory[shared_name].dtype)}")
                # Now create a NumPy array backed by shared memory
                return np.ndarray(self.parent.sharedMemory[shared_name].shape,str(self.parent.sharedMemory[shared_name].dtype), buffer = shm.buf)
            

            #If we either are not a tracked path anymore or we are the actual data but it is not the value that is accessed
            elif not tracked_data or (shared_name in self.parent.sharedPaths and item != "value"):
                print(f"GOING OUT AT {shared_name + '.' +item}")
                caller =  operator.attrgetter(".".join(self.items + [item]))                                          
                return caller(self.parent.exposed_sofa_root)
           
            #We arrive here only if we are still in a ptracked path but we are not exactly one tracked path
            self.items.append(item)    
            return self
        

    exposed_sofa_root : Sofa.Core.Node
    sharedPaths : dict
    
    def __init__(self, *args, **kwargs):
        rpyc.Service.__init__(self,*args, **kwargs)
        self.animationThread = None
        self.sharedMemory = None
        self.sharedMemoryIsSet = False
        self.sharedMemoryIsUsed = False

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

    def exposed_setup_shared_memory_for_data(self, dataPaths:list[str], delayed=False):
        self.paths_for_shared_mem = dataPaths
        if(not delayed):
            self.paths_for_shared_mem = self.__internal_setup_shared_memory()

    def __internal_setup_shared_memory(self):
        self.sharedMemory = {}
        self.sharedPaths = []
        self.sharedMemoryIsSet = True
        for paths in self.paths_for_shared_mem:

            paths = paths.replace('/','.')
            while len(paths) > 1 and paths[0] in "@." :
                paths = paths[1:]

            caller =  operator.attrgetter(paths)                                          
            data = caller(self.exposed_sofa_root).value
            if( isinstance(data, np.ndarray)):
                print(f"Sharing {data.size*data.itemsize} bytes for data {paths}")
                self.sharedMemory[paths] = SOFAService.SharedMemoryInfo(data.shape, data.dtype, shared_memory.SharedMemory(create=True, size=data.size*data.itemsize))
                self.sharedPaths.append(paths)
            else:
                print(f"Not creating a shared memory for data {paths} because it is no a numpy array")
        self.sharedMemoryIsUsed = len(self.sharedPaths) != 0
        return self.sharedPaths
    
    def exposed_copy_shared_data_into_memory(self,shared_name):
        shm = shared_memory.SharedMemory(name=self.sharedMemory[shared_name].getSharedName())
        caller =  operator.attrgetter(shared_name)                                          
        data = caller(self.exposed_sofa_root).value
        b = np.ndarray(data.shape, dtype=data.dtype, buffer=shm.buf)
        b[:] = data[:]  

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
        if(not self.sharedMemoryIsSet):
            self.__internal_setup_shared_memory()

        
        
