import Sofa
from SoftRobotsPrefabs.prefabs.prefabs import RoboticPrefabSimulation
from SoftRobotsPrefabs.reusableMethods.goals import addCartesianGoal
from SoftRobotsPrefabs.simulation.headers import setupSoftRobotsInverseHeader
from splib.prefabs.parameters import *
from splib.topology.dynamic import ElementType
from splib.simulation.headers import CollisionType
from splib.core.enum_types import *


cables_pullPoints = [[0, 10, 30], [-10, 0, 30], [0, -10, 30], [10, 0, 30]]
cables_slidingPoints = [[0, 97, 45], [-97, 0, 45], [0, -97, 45], [97, 0, 45],  [0, 0, 115]]
cables_names = ["nord", "west", "south", "est"]


@RoboticPrefabSimulation
def createScene(rootNode):
    rootNode.dt = 1
    rootNode.gravity = [0, 0, -9810]

    setupSoftRobotsInverseHeader(rootNode,parallelComputing=True, frictionCoef=0.5, maxIterations=10,tolerance=1.0e-3,
                             Distance={ "alarmDistance":3, "contactDistance":0.5}, backgroundColor=[0,0,0,0.5],
                             displayFlags="showForceFields",
                             requiredPlugins={"pluginName":["SoftRobots", "SoftRobots.Inverse", "Sofa.Component.IO.Mesh", "Sofa.Component.LinearSolver.Direct", "Sofa.Component.LinearSolver.Iterative",
                                                                "Sofa.Component.Mapping.Linear", "Sofa.Component.Mass", "Sofa.Component.ODESolver.Backward", "Sofa.Component.Setting",
                                                            "Sofa.Component.SolidMechanics.FEM.Elastic","Sofa.Component.StateContainer","Sofa.Component.Topology.Container.Dynamic",
                                                            "Sofa.Component.Visual","Sofa.GL.Component.Rendering3D","Sofa.Component.AnimationLoop","Sofa.Component.Collision.Detection.Algorithm",
                                                            "Sofa.Component.Collision.Detection.Intersection","Sofa.Component.Collision.Geometry","Sofa.Component.Collision.Response.Contact",
                                                            "Sofa.Component.Constraint.Lagrangian.Solver","Sofa.Component.Constraint.Lagrangian.Correction","Sofa.Component.LinearSystem",
                                                            "Sofa.Component.MechanicalLoad","MultiThreading","Sofa.Component.SolidMechanics.Spring","Sofa.Component.Constraint.Lagrangian.Model",
                                                            "Sofa.Component.Mapping.NonLinear","Sofa.Component.Topology.Container.Constant","Sofa.Component.Topology.Mapping",
                                                            "Sofa.Component.Topology.Container.Grid","Sofa.Component.Engine.Select","CSparseSolvers"]}) #"",

    addCartesianGoal(rootNode, initPose=[[0, 0, 125]], radius=5, group=1)
    
    robot = rootNode.addSoftRobot("Diamond",
                                    template="Vec3d",
                                    elemType=ElementType.TETRA,
                                    topologyParams=TopologyParameters(filename="../Data/diamond.vtk"),
                                    collisionType=CollisionType.LAGRANGIAN,
                                    mstate={"rx":90, "dz":35})

    robot.addConstitutiveModel(law=ConstitutiveLaw.LINEAR_COROT,
                                         lawParams=LinearConstitutiveLawParameters(youngModulus=180, poissonRatio=0.45, method='large'),
                                         massParams=MassParameters(totalMass=0.5))
    
    robot.addVisualModel(color=[1.0,1.0,0.2],extractSurfaceFromParent=True)


    robot.addDirichletConditions(ConstraintType.PROJECTIVE,
                                fixationParams=FixationParameters(boxROIs=[-15, -15, -40, 15, 15, 10]))
    
    

    for i in range(len(cables_pullPoints)):
        robot.addCableActuator(cables_pullPoints[i],[ cables_slidingPoints[i]],name=cables_names[i],maxPositiveDisp=20, minForce=0) 
    robot.addCartesianEffector([[0, 0, 125]], "@../../goal/goalMO.position")


    return rootNode
