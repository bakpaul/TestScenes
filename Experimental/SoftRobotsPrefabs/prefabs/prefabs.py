from splib.prefabs.utils import RootWrapper
from .softRobot import SoftRobot
from functools import wraps



class RobotRootWrapper(RootWrapper):

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

    def addSoftRobot(self,name,*args,**kwargs):
        child = self.node.addChild(name)
        ## We need to wrap the child passed to the prefab object to enforce the mechanism of "addChild"
        return SoftRobot(RobotRootWrapper(child),*args,**kwargs)



def RoboticPrefabSimulation(method):
    @wraps(method)
    def wrapper(*args, **kwargs):
        if len(args)>1:
            return method(RobotRootWrapper(args[0]),*args[1:],**kwargs)
        else:
            return method(RobotRootWrapper(args[0]),**kwargs)
    return wrapper
