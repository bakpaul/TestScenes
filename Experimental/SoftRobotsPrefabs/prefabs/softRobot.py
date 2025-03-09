from splib.prefabs.simulated_object import SimulatedObject
from splib.core.utils import DEFAULT_VALUE

class SoftRobot(SimulatedObject):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

    def addCableActuator(self, pullPoint, slidingPositions,name="actuatedCables", hasPullPoint=DEFAULT_VALUE, cableInitialLength=DEFAULT_VALUE,maxForce=DEFAULT_VALUE, minForce=DEFAULT_VALUE, maxPositiveDisp=DEFAULT_VALUE, maxNegativeDisp=DEFAULT_VALUE):
        controlledPoints = self.node.addChild(name)
        controlledPoints.addObject('MechanicalObject', name="actuatedPoints",
                                position=slidingPositions)
        controlledPoints.addObject('CableActuator',  indices=[i for i in range(len(slidingPositions))], pullPoint=pullPoint,
                                   hasPullPoint=hasPullPoint, cableInitialLength=cableInitialLength,
                                   maxForce=maxForce, minForce=minForce, maxPositiveDisp=maxPositiveDisp, maxNegativeDisp=maxNegativeDisp)
        controlledPoints.addObject('BarycentricMapping')

    def addCartesianEffector(self, effectorPosition, effectorGoal, name="EEF", limitShiftToTarget=DEFAULT_VALUE, maxShiftToTarget=DEFAULT_VALUE, maxSpeed=DEFAULT_VALUE):
        controlledPoints = self.node.addChild(name)
        controlledPoints.addObject('MechanicalObject', name="actuatedPoints",
                                position=effectorPosition)
        controlledPoints.addObject('PositionEffector', indices=[i for i in range(len(effectorPosition))], effectorGoal=effectorGoal, limitShiftToTarget=limitShiftToTarget, maxShiftToTarget=maxShiftToTarget, maxSpeed=maxSpeed)

        controlledPoints.addObject('BarycentricMapping')