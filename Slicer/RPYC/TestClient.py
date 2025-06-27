import multiprocessing
import threading
import time
import rpyc
from SOFAService import SOFAService
import Sofa

class SOFAClient():


    def start_server(self):

        self.server = rpyc.OneShotServer(service=SOFAService(), hostname="localhost", port=18813,protocol_config={
                                                                                        'allow_public_attrs': True,
                                                                                        'allow_all_attrs': True,
                                                                                        'allow_pickle': True })

        self.serverProcess = multiprocessing.Process(target = self.server.start)
        self.serverProcess.start()



    def connect_client(self,hostename="localhost", port=18813,  number_of_attempt = 10, wait_time = 0.1):
        it = 0
        while(not self.__internal_connect_to_client(hostename=hostename, port=port) and it < number_of_attempt):
            time.sleep(wait_time)
            it += 1
        
        self.async_step_executor = rpyc.async_(SC.connection.root.step_simulation)
        

    def __internal_connect_to_client(self, hostename, port):
        try:
            self.connection = rpyc.connect(hostename, port, config = {'allow_public_attrs': True, "allow_all_attrs": True, "allow_pickle": True})
        except ConnectionRefusedError:
            return False
        return True
    
    def load_scene(self, filename):
        SC.connection.root.exposed_build_scene_graph_from_file(filename)

    def asynch_step(self):
        return self.async_step_executor()

    def stop_server(self):
        self.connection.close()
        self.serverProcess.terminate()

    def get_data_from_shared_memory(self,dataPath):
        pass

    def __getattr__(self, item):
        return(getattr(SC.connection.root,item))
        

if __name__ == "__main__":


    SC = SOFAClient()
    SC.start_server()
    SC.connect_client()

    SC.load_scene("SlicerLogoDef.py")

    asynch_step = None
    currentTime = 0.0
    while currentTime<0.2:
        if(asynch_step is None or asynch_step.ready):
            #Time to get data from object
            currentTime = SC.sofa_root.getTime()
            print(currentTime)
            #Launch next step
            asynch_step = SC.asynch_step()
        else:
            print("waiting 0.1 sec")
            time.sleep(0.1)


    # SC.pause_simulation()
    SC.stop_server()
    