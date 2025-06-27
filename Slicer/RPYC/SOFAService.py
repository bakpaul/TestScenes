import rpyc
import time
import threading
import Sofa
import importlib.util
import pathlib

class SOFAService(rpyc.SlaveService):

    exposed_sofa_root : Sofa.Core.Node

    
    def __init__(self, *args, **kwargs):
        rpyc.Service.__init__(self,*args, **kwargs)
        self.animationThread = None

    def on_connect(self, conn):
        self.exposed_sofa_root = Sofa.Core.Node("root")
        self.animate = False
        pass

    def on_disconnect(self, conn):
        self.exposed_pause_simulation()
        pass

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

        
        
