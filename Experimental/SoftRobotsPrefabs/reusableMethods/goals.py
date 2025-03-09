from splib.core.node_wrapper import ReusableMethod
from splib.core.utils import DEFAULT_VALUE
from splib.mechanics.collision_model import addCollisionModels

@ReusableMethod
def addCartesianGoal(node, name="goal", initPose=[0,0,0],radius=DEFAULT_VALUE, group=DEFAULT_VALUE):
    goal = node.addChild(name)
    goal.addObject('EulerImplicitSolver', firstOrder=True)
    goal.addObject('CGLinearSolver', iterations=100,threshold=1e-5, tolerance=1e-5)
    goal.addObject('MechanicalObject', name='goalMO', position=[initPose])
    addCollisionModels(goal, spheres=True, spheresRadius=5, group=1)
    goal.addObject('UncoupledConstraintCorrection')
    
    return goal
