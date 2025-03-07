import Sofa
from splib.simulation.headers import *
from splib.prefabs.utils import PrefabSimulation
from splib.topology.dynamic import ElementType
from splib.prefabs.parameters import *
from splib.mechanics.collision_model import *
from splib.Testing import exportScene


@PrefabSimulation
def createScene(rootNode):
    rootNode.dt = 1
    rootNode.gravity = [0, 0, -9810]

    setupLagrangianCollision(rootNode,parallelComputing=True, frictionCoef=0.5, maxIterations=10,tolerance=1.0e-3,
                             Distance={ "alarmDistance":3, "contactDistance":0.5}, backgroundColor=[0,0,0,0.5],
                             requiredPlugins={"pluginName":["SoftRobots", "Sofa.Component.IO.Mesh", "Sofa.Component.LinearSolver.Direct", "Sofa.Component.LinearSolver.Iterative",
                                                                "Sofa.Component.Mapping.Linear", "Sofa.Component.Mass", "Sofa.Component.ODESolver.Backward", "Sofa.Component.Setting",
                                                            "Sofa.Component.SolidMechanics.FEM.Elastic","Sofa.Component.StateContainer","Sofa.Component.Topology.Container.Dynamic",
                                                            "Sofa.Component.Visual","Sofa.GL.Component.Rendering3D","Sofa.Component.AnimationLoop","Sofa.Component.Collision.Detection.Algorithm",
                                                            "Sofa.Component.Collision.Detection.Intersection","Sofa.Component.Collision.Geometry","Sofa.Component.Collision.Response.Contact",
                                                            "Sofa.Component.Constraint.Lagrangian.Solver","Sofa.Component.Constraint.Lagrangian.Correction","Sofa.Component.LinearSystem",
                                                            "Sofa.Component.MechanicalLoad","MultiThreading","Sofa.Component.SolidMechanics.Spring","Sofa.Component.Constraint.Lagrangian.Model",
                                                            "Sofa.Component.Mapping.NonLinear","Sofa.Component.Topology.Container.Constant","Sofa.Component.Topology.Mapping",
                                                            "Sofa.Component.Topology.Container.Grid","Sofa.Component.Engine.Select","CSparseSolvers"]}) #"",

    goal = rootNode.addSimulatedObject("goal",
                                       template="Vec3d",
                                       collisionType=CollisionType.LAGRANGIAN,
                                       mstate = {"position" : [[0, 0, 125]]})
    addCollisionModels(goal, spheres=True, spheresRadius=5, group=1)


    #robot
    robot = rootNode.addChild('robot')
    robot.addObject('EulerImplicitSolver')
    robot.addObject('SparseLDLSolver', template="CompressedRowSparseMatrixd")
    robot.addObject('GenericConstraintCorrection')
    robot.addObject('MeshVTKLoader', name="loader", filename="../Data/diamond.vtk")
    robot.addObject('MeshTopology', src="@loader")
    robot.addObject('MechanicalObject', showIndicesScale=4e-5, rx=90, dz=35)
    robot.addObject('UniformMass', totalMass=0.5)
    robot.addObject('TetrahedronFEMForceField', youngModulus=180, poissonRatio=0.45)
    robot.addObject('BoxROI', box=[-15, -15, -40, 15, 15, 10], drawBoxes=True)
    robot.addObject('FixedProjectiveConstraint', indices="@BoxROI.indices")


    for i in range(4):
        controlledPoints.addObject('CableConstraint', name="cable"+str(i), indices=i+1,
                                   pullPoint=[[0, 10, 30], [-10, 0, 30], [0, -10, 30], [10, 0, 30]][i],
                                   maxPositiveDisp=20, minForce=0)

    controlledPoints.addObject('BarycentricMapping', mapForces=False, mapMasses=False)

    return rootNode
