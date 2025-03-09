from splib.simulation.headers import *


@ReusableMethod
def setupSoftRobotsInverseHeader(node,  displayFlags = "showVisualModels",backgroundColor=[1,1,1,1], parallelComputing=False, stick=False, alarmDistance=DEFAULT_VALUE, contactDistance=DEFAULT_VALUE, frictionCoef=0.0, tolerance=0.0, maxIterations=100, **kwargs):
    node.addObject('VisualStyle', displayFlags=displayFlags)
    node.addObject('BackgroundSetting', color=backgroundColor)

    node.addObject("RequiredPlugin", name="requiredPlugins", pluginName=['Sofa.Component.Constraint.Lagrangian',
                                                                         'Sofa.Component.Constraint.Projective',
                                                                         'Sofa.Component.Engine.Select',
                                                                         'Sofa.Component.LinearSolver.Direct',
                                                                         'Sofa.Component.Mass',
                                                                         'Sofa.Component.ODESolver.Backward',
                                                                         'Sofa.Component.SolidMechanics.FEM.Elastic',
                                                                         'Sofa.Component.StateContainer',
                                                                         'Sofa.Component.Topology.Container.Grid',
                                                                         'Sofa.Component.IO.Mesh',
                                                                         'Sofa.Component.LinearSolver.Direct',
                                                                         'Sofa.Component.ODESolver.Forward',
                                                                         'Sofa.Component.Topology.Container.Dynamic',
                                                                         'Sofa.Component.Visual',
                                                                         ],
                   **kwargs)


    node.addObject('FreeMotionAnimationLoop',name="animation",
                   parallelCollisionDetectionAndFreeMotion=parallelComputing,
                   parallelODESolving=parallelComputing,
                   **kwargs)

    parallelPrefix = ""
    if(parallelComputing):
        parallelPrefix="Parallel"

    node.addObject('CollisionPipeline', name="collisionPipeline",
                   **kwargs)

    node.addObject(parallelPrefix+'BruteForceBroadPhase', name="broadPhase",
                   **kwargs)

    node.addObject(parallelPrefix+'BVHNarrowPhase',  name="narrowPhase",
                   **kwargs)

    if(stick):
        node.addObject('CollisionResponse',name="ContactManager", response="StickContactConstraint", responseParams="tol="+str(tolerance),**kwargs)
    else:
        node.addObject('CollisionResponse',name="ContactManager", response="FrictionContactConstraint", responseParams="mu="+str(frictionCoef),**kwargs)

    node.addObject('NewProximityIntersection' ,name="Distance", alarmDistance=alarmDistance, contactDistance=contactDistance, **kwargs)
    node.addObject('QPInverseProblemSolver',name="ConstraintSolver", tolerance=tolerance, maxIterations=maxIterations,**kwargs)
    node.addObject("ConstraintAttachButtonSetting")

    return node
