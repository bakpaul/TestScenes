import rpyc
import time
import threading
import Sofa
import importlib.util
import pathlib
import numpy as np
from multiprocessing import shared_memory
import multiprocessing
import operator


class SOFAClient():


    class SOFASharedMemoryProxy():

        def __init__(self, client, server, path = ""):
            self.client = client
            self.server = server
            self.path = path

        #If this method is called, then it means the used called a method of one of the sofa object, then just return the result and let rpyc deal with it
        def __call__(self, *args, **kwds):
            caller =  operator.attrgetter(self.path)                                          
            return caller(self.server.exposed_sofa_root).__call__(*args,**kwds)
        

        def __getattr__(self,item):
            
            #Check if until now we are still on the path of a tracked data
            tracked_data = False
            for path in self.server.sharedPaths:
                if self.path in path:
                    tracked_data = True
                    break

            #If we are exactly a tracked data and the value is accessed, then use shared memory
            if tracked_data and self.path in self.server.sharedPaths and item == "value":
                self.server.copy_shared_data_into_memory(self.path)
                if not self.path in self.client.sharedMemory :
                    self.client.sharedMemory[self.path] = shared_memory.SharedMemory(name=self.server.sharedMemory[self.path].getSharedName())
                # Now create a NumPy array backed by shared memory
                return np.ndarray(self.server.sharedMemory[self.path].shape,str(self.server.sharedMemory[self.path].dtype), buffer = self.client.sharedMemory[self.path].buf)
            

            #If we either are not a tracked path anymore or we are the actual data but it is not the value that is accessed
            elif not tracked_data or (self.path in self.server.sharedPaths and item != "value"):
                if(self.path != ""):
                    self.path += '.'
                self.path += item    
            
                caller =  operator.attrgetter(self.path)                                          
                return caller(self.server.exposed_sofa_root)
           
            #We arrive here only if we are still in a ptracked path but we are not exactly one tracked path
            if(self.path != ""):
                self.path += '.'
            self.path += item    
            return self
        
    def __init__(self):
        self.sharedMemory = {}
        
    def start_server(self, port=18813):

        self.server = rpyc.ForkingServer(service=SOFAService(), hostname="localhost", port=port,protocol_config={'allow_public_attrs': True, 'allow_all_attrs': True,'allow_pickle': True })

        self.serverProcess = multiprocessing.Process(target = self.server.start)
        self.serverProcess.start()


    def connect_client(self,hostename="localhost", port=18813,  number_of_attempt = 10, wait_time = 0.1):
        it = 0
        connected = self.__internal_connect_to_client(hostename=hostename, port=port)
        
        while(not connected and it < number_of_attempt):
            time.sleep(wait_time)
            connected = self.__internal_connect_to_client(hostename=hostename, port=port)
            it += 1

        if(connected):
            self.async_step_executor = rpyc.async_(self.connection.root.step_simulation)

        return connected


    def __internal_connect_to_client(self, hostename, port):
        try:
            self.connection = rpyc.connect(hostename, port, config = {'allow_public_attrs': True, "allow_all_attrs": True, "allow_pickle": True})
        except ConnectionRefusedError:
            return False
        return True
    
    def load_scene(self, filename):
        self.connection.root.exposed_build_scene_graph_from_file(filename)

    def asynch_step(self):
        return self.async_step_executor()

    def stop_server(self):
        self.connection.close()
        self.serverProcess.terminate()

    def get_data_from_shared_memory(self,dataPath):
        pass

    def __getattr__(self, item):
        if item == "sofa_root" and self.connection.root.sharedMemoryIsSet and self.connection.root.sharedMemoryIsUsed :
            return SOFAClient.SOFASharedMemoryProxy(client = self, server = self.connection.root)
        return(getattr(self.connection.root,item))
        

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
                self.sharedMemory[paths] = SOFAService.SharedMemoryInfo(data.shape, data.dtype, shared_memory.SharedMemory(create=True, size=data.nbytes))
                self.sharedPaths.append(paths)
                print(f"Sharing {data.nbytes} bytes for data {paths}.")

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

        
        
