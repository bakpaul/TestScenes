import Sofa
from splib.simulation.headers import *
from splib.prefabs.utils import PrefabSimulation
from splib.topology.dynamic import ElementType
from splib.prefabs.parameters import *
from splib.mechanics.collision_model import *
from splib.Testing import exportScene

@PrefabSimulation
def createScene(rootNode):

    rootNode.dt = 0.01
    rootNode.gravity = [0,0,9.81]


    setupLagrangianCollision(rootNode,parallelComputing=True, frictionCoef=0.5, maxIterations=10,tolerance=1.0e-3,
                             Distance={ "alarmDistance":0.2, "contactDistance":0.02},
                             requiredPlugins={"pluginName":["Sofa.Component.IO.Mesh", "Sofa.Component.LinearSolver.Direct", "Sofa.Component.LinearSolver.Iterative",
                                                            "Sofa.Component.Mapping.Linear", "Sofa.Component.Mass", "Sofa.Component.ODESolver.Backward", "Sofa.Component.Setting",
                                                            "Sofa.Component.SolidMechanics.FEM.Elastic","Sofa.Component.StateContainer","Sofa.Component.Topology.Container.Dynamic",
                                                            "Sofa.Component.Visual","Sofa.GL.Component.Rendering3D","Sofa.Component.AnimationLoop","Sofa.Component.Collision.Detection.Algorithm",
                                                            "Sofa.Component.Collision.Detection.Intersection","Sofa.Component.Collision.Geometry","Sofa.Component.Collision.Response.Contact",
                                                            "Sofa.Component.Constraint.Lagrangian.Solver","Sofa.Component.Constraint.Lagrangian.Correction","Sofa.Component.LinearSystem",
                                                            "Sofa.Component.MechanicalLoad","MultiThreading","Sofa.Component.SolidMechanics.Spring","Sofa.Component.Constraint.Lagrangian.Model",
                                                            "Sofa.Component.Mapping.NonLinear","Sofa.Component.Topology.Container.Constant","Sofa.Component.Topology.Mapping",
                                                            "Sofa.Component.Topology.Container.Grid","Sofa.Component.Engine.Select","CSparseSolvers"]}) #"",


    Logo = rootNode.addSimulatedObject("Logo",
                                       template="Vec3d",
                                       elemType=ElementType.TETRA,
                                       collisionType=CollisionType.LAGRANGIAN,
                                       topologyParams=TopologyParameters(filename="../Data/graph.vtk"),
                                       linearSolverParams=DirectLinearSolverParameters(constantSparsity=True,parallelInverseProduct=True,template="CompressedRowSparseMatrixd"))

    Logo.addConstitutiveModel(law=ConstitutiveLaw.LINEAR_COROT,
                              lawParams=LinearConstitutiveLawParameters(youngModulus="200", poissonRatio="0.4", method="large"),
                              massParams=MassParameters(totalMass="0.1"))
    Logo.addObject("ConstantForceField",totalForce="0 0 -5.0")
    Logo.addCollisionModel(collisionParameters =CollisionParameters(spheres=True,selfCollision=True,proximity=0.2),
                           filename="../Data/Logo.sph",
                           SphereCollision={"listRadius":"@meshLoader.listRadius"})
    Logo.addVisualModel(color=[0.7, .35, 0, 0.8],
                        filename="../Data/graph_t.obj")
    Logo.addMappedTopology("AttachmentPoint","Vec3",
                           elemType=ElementType.POINTS,
                           mstate={"position":[12, 0, -9]})

    Beam = rootNode.addChild("BeamModel")
    Beam.addObject("EulerImplicitSolver", name="EulerImplicitScheme",  printLog="false" )
    Beam.addObject("SparseLUSolver", name="LULinearSolver", template="CompressedRowSparseMatrixd")
    Beam.addObject("MechanicalObject", template="Rigid3d", name="BeamDOF", position="12 0 -9  0.707 0 0.707 0 12 0 -8  0.707 0 0.707 0 12 0 -7  0.707 0 0.707 0 12 0 -6  0.707 0 0.707 0 12 0 -5.5  0.707 0 0.707 0" )
    Beam.addObject("MeshTopology", name="LineTopology", position="@BeamDOF.position", lines="0 1 1 2 2 3 3 4 ", drawEdges="1")
    Beam.addObject("BeamInterpolation", name="BeamInterpolation", radius="0.1", defaultYoungModulus="10000 10000 10000", defaultPoissonRatio="0.4")
    Beam.addObject("AdaptiveBeamForceFieldAndMass", name="BeamForceFieldAndMass",  computeMass="1", massDensity="1")
    BeamExtremities = Beam.addChild("BeamExtremities")
    BeamExtremities.addObject("MechanicalObject", name="Points", template="Vec3", position="12 0 -9 12 0 -5.5 ")
    BeamExtremities.addObject("RigidMapping", name="MappingBeamExtremities", globalToLocalCoords="true", rigidIndexPerPoint="0 4")
    Beam.addObject("LinearSolverConstraintCorrection", name="ConstraintCorrection", linearSolver="@LULinearSolver")



    S = rootNode.addSimulatedObject("S",
                                    template="Vec3d",
                                    elemType=ElementType.TETRA,
                                    collisionType=CollisionType.LAGRANGIAN,
                                    topologyParams=TopologyParameters(filename="../Data/S.vtk"),
                                    linearSolverParams=DirectLinearSolverParameters(constantSparsity=True,parallelInverseProduct=True,template="CompressedRowSparseMatrixd"))

    S.addConstitutiveModel(law=ConstitutiveLaw.LINEAR_COROT,
                           lawParams=LinearConstitutiveLawParameters(youngModulus="200", poissonRatio="0.45", method="large"),
                           massParams=MassParameters(totalMass="0.15"))
    S.addCollisionModel(collisionParameters =CollisionParameters(triangles=True,selfCollision=False,proximity=0.2),
                        extractSurfaceFromParent=True)
    S.addVisualModel(color=[0.7, 0.7, 0.7, 0.8],
                     filename="../Data/S_t.obj")
    S.addMappedTopology("AttachmentPoint","Vec3",
                        elemType=ElementType.POINTS,
                        mstate={"position":[12, 0, -5.5]})

    rootNode.addObject("BilateralInteractionConstraint", template="Vec3", object1="@Logo/AttachmentPoint/mstate", object2="@BeamModel/BeamExtremities/Points", first_point="0", second_point="0")
    rootNode.addObject("BilateralInteractionConstraint", template="Vec3", object1="@S/AttachmentPoint/mstate", object2="@BeamModel/BeamExtremities/Points", first_point="0", second_point="1")

    O = rootNode.addSimulatedObject("O",
                                    template="Vec3d",
                                    elemType=ElementType.HEXA,
                                    collisionType=CollisionType.LAGRANGIAN,
                                    topologyParams=TopologyParameters(filename="../Data/O_t.obj",generateSparseGrid=True,sparseGridSize="4 2 4"),
                                    SparseGrid={"nbVirtualFinerLevels":"2", "finestConnectivity":"0"},
                                    linearSolverParams=DirectLinearSolverParameters(constantSparsity=True,parallelInverseProduct=True,template="CompressedRowSparseMatrixd"))

    O.addConstitutiveModel(law=ConstitutiveLaw.LINEAR_COROT,
                           lawParams=LinearConstitutiveLawParameters(youngModulus="200", poissonRatio="0.45", method="large"),
                           massParams=MassParameters(totalMass="0.15"))
    O.addCollisionModel(collisionParameters =CollisionParameters(edges=True,selfCollision=False,proximity=0.2),
                        source="@../meshLoader")
    O.addVisualModel(color="white",
                     source="@../meshLoader")


    F = rootNode.addSimulatedObject("F",
                                    template="Rigid3",
                                    collisionType=CollisionType.LAGRANGIAN,
                                    mstate={"position":"23.15 0 -2.7 0 0 0 1"},
                                    linearSolverParams=DirectLinearSolverParameters(constantSparsity=True,template="CompressedRowSparseMatrixd"))

    F.addConstitutiveModel(massParams=MassParameters(totalMass="0.1"))
    F.addCollisionModel(collisionParameters =CollisionParameters(edges=True,selfCollision=False,proximity=0.5),
                        filename="../Data/F_Skel.obj")
    F.addVisualModel(color=[0.7, 0.7, 0.7, 0.8],
                     filename="../Data/F_t.obj")


    A = rootNode.addSimulatedObject("A",
                                    template="Vec3d",
                                    elemType=ElementType.TETRA,
                                    collisionType=CollisionType.LAGRANGIAN,
                                    topologyParams=TopologyParameters(filename="../Data/A.vtk"),
                                    linearSolverParams=DirectLinearSolverParameters(constantSparsity=True,parallelInverseProduct=True,template="CompressedRowSparseMatrixd"))

    A.addConstitutiveModel(law=ConstitutiveLaw.LINEAR_COROT,
                           lawParams=LinearConstitutiveLawParameters(youngModulus="30", poissonRatio="0.4", method="large"),
                           massParams=MassParameters(totalMass="0.1"))
    A.addCollisionModel(collisionParameters =CollisionParameters(points=True,selfCollision=False,proximity=0.3),
                        filename="../Data/A-coarse.obj")
    A.addVisualModel(color=[0.7, 0.7, 0.7, 0.8],
                     filename="../Data/A_t.obj")


    Floor = rootNode.addNonSimulatedObject("Floor","Vec3",elemType = ElementType.TRIANGLES,
                                           container={"position":"-20 -15 1  50 -15 1  50 15 1  -20 15 1","triangles":"0 2 1  0 3 2"})
    addCollisionModels(Floor,triangles=True,proximity="0.02", moving="0", simulated="0" )
    Floor.addObject(  "OglModel", name="VisualModel", src="@container")

    Ceil = rootNode.addNonSimulatedObject("Ceil","Vec3",elemType = ElementType.TRIANGLES,
                                           container={"position":"-20 -15 -20   50 -15 -20    50 15 -20    -20 15 -20","triangles":"0 1 2  3 0 2"})
    addCollisionModels(Ceil,triangles=True,proximity="0.02", moving="0", simulated="0" )
    Ceil.addObject(  "OglModel", name="VisualModel", src="@container")


    return rootNode

if __name__ == "__main__":
    Node = exportScene()
    createScene(Node)



