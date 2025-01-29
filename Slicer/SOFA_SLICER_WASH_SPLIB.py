#Required import for python
import Sofa
import SofaRuntime
from Sofa import SofaLinearSolver
import numpy as np
import scipy

from splib.prefabs.utils import PrefabSimulation
from splib.prefabs.parameters import *
from splib.simulation.headers import setupLagrangianCollision, CollisionType
from splib.core.enum_types import *


@PrefabSimulation
def createScene(root):

    root.gravity=[0,-100,0]
    root.dt = 0.01

    # Loading the dynamic libraries required for this scene
    # Rendering settings
    # Header of the simulation
    # Definition of the collision pipeline

    setupLagrangianCollision(root,
                             backgroundColor=[0.8, 0.8, 0.8, 1],
                             requiredPlugins={"pluginName":["Sofa.Component.IO.Mesh", "Sofa.Component.LinearSolver.Direct", "Sofa.Component.LinearSolver.Iterative",
                                                                    "Sofa.Component.Mapping.Linear", "Sofa.Component.Mass", "Sofa.Component.ODESolver.Backward", "Sofa.Component.Setting",
                                                                    "Sofa.Component.SolidMechanics.FEM.Elastic", "Sofa.Component.StateContainer", "Sofa.Component.Topology.Container.Dynamic",
                                                                    "Sofa.Component.Visual", "Sofa.GL.Component.Rendering3D", "Sofa.Component.AnimationLoop", "Sofa.Component.Collision.Detection.Algorithm",
                                                                    "Sofa.Component.Collision.Detection.Intersection", "Sofa.Component.Collision.Geometry", "Sofa.Component.Collision.Response.Contact",
                                                                    "Sofa.Component.Constraint.Lagrangian.Solver", "Sofa.Component.Constraint.Lagrangian.Correction", "Sofa.Component.LinearSystem",
                                                                    "Sofa.Component.MechanicalLoad", "MultiThreading", "Sofa.Component.SolidMechanics.Spring", "Sofa.Component.Constraint.Lagrangian.Model",
                                                                    "Sofa.Component.Mapping.NonLinear", "Sofa.Component.Topology.Container.Constant", "Sofa.Component.Topology.Mapping",
                                                                    "Sofa.Component.Topology.Container.Grid", "Sofa.Component.Engine.Select", "Sofa.Component.Constraint.Projective"]},
                             parallelComputing=True,
                             alarmDistance=10, contactDistance=5,
                             maxIterations=50,
                             tolerance=1.0e-3,
                             frictionCoef=0.2,
                             )
    # Object = SOFA Logo
    SOFALogo = root.addSimulatedObject("SofaLogo",
                                        template="Vec3d",
                                        elemType=ElementType.TETRA,
                                        topologyParams=TopologyParameters(filename="../Data/SOFA_volume.vtk"),
                                        meshLoader={"translation":[-120, 20, 0], "rotation":[180, 0, 90]},
                                        linearSolverParams=DirectLinearSolverParameters(constantSparsity=True,parallelInverseProduct=True,template="CompressedRowSparseMatrixd"),
                                        collisionType=CollisionType.LAGRANGIAN)

    SOFALogo.addConstitutiveModel(law=ConstitutiveLaw.LINEAR_COROT,
                                  lawParams=LinearConstitutiveLawParameters(youngModulus=5, poissonRatio=0.3, method="large"),
                                  massParams=MassParameters(totalMass=0.1))

    SOFALogo.addCollisionModel(name="Collision",
                               collisionParameters=CollisionParameters(points=False,edges=True,triangles=False,selfCollision=True,group=[2, 3, 5]),
                               filename="../Data/SOFA_collision_no_face.obj",
                               meshLoader={"translation":[-120, 20, 0], "rotation":[180, 0, 90]}
                               )

    SOFALogo.addCollisionModel(name="BorderCollision",
                               collisionParameters=CollisionParameters(points=False,edges=True,triangles=False,selfCollision=False,group=[3, 4]),
                               filename="../Data/SOFA_collision_center.obj",
                               meshLoader={"translation":[-120, 20, 0], "rotation":[180, 0, 90]}
                               )

    SOFALogo.addVisualModel(color=[0.7, .35, 0, 1],
                            filename="../Data/SOFA_surface.obj",
                            meshLoader={"translation":[-120, 20, 0], "rotation":[180, 0, 90]},
                            )

    # Object = Slicer Logo
    SLICERLogo = root.addSimulatedObject("SlicerLogo",
                                       template="Vec3d",
                                       elemType=ElementType.TETRA,
                                       topologyParams=TopologyParameters(filename="../Data/Slicer_volume.vtk"),
                                       linearSolverParams=DirectLinearSolverParameters(constantSparsity=True,parallelInverseProduct=True,template="CompressedRowSparseMatrixd"),
                                       collisionType=CollisionType.LAGRANGIAN)

    SLICERLogo.addConstitutiveModel(law=ConstitutiveLaw.LINEAR_COROT,
                                  lawParams=LinearConstitutiveLawParameters(youngModulus=1, poissonRatio=0.3, method="large"),
                                  massParams=MassParameters(totalMass=0.05))

    SLICERLogo.addCollisionModel(name="Collision",
                               collisionParameters=CollisionParameters(points=False,edges=True,triangles=False,selfCollision=False,group=[1, 4, 6]),
                               filename="../Data/Slicer_collision_no_face.obj"
                               )

    SLICERLogo.addCollisionModel(name="BorderCollision",
                               collisionParameters=CollisionParameters(points=False,edges=True,triangles=False,selfCollision=False,group=[5, 6]),
                               filename="../Data/Slicer_collision_center.obj",
                               )

    SLICERLogo.addVisualModel(color=[0.7, 0.7, 0.7, 1],
                            filename="../Data/Slicer_surface.obj",
                            )




    BOX = root.addSimulatedObject("Box",
                            template="Rigid3",
                            mstate={"position":[0, 0, 0, 0, 0, 0, 1]},
                            linearSolverParams=DirectLinearSolverParameters(constantSparsity=False,parallelInverseProduct=False,template="CompressedRowSparseMatrixd"))
    BOX.addObject("LinearVelocityProjectiveConstraint",indices="0",keyTimes="0 2", velocities="0 0 0 0 0 0 0 0 0 0 0 0.3 ",continueAfterEnd=True)

    CollisionBoxCollision = BOX.addMappedTopology(name="Collision",
                                                  template="Vec3d",
                                                  elemType=ElementType.TRIANGLES,
                                                  dynamicTopo=True,
                                                  container={"position":[-200, -200, 15,  200, -200, 15,  200, 200, 15,  -200, 200, 15,  -200, -200, -15,  200, -200, -15,  200, 200, -15,  -200, 200, -15],
                                                             "triangles":[0, 2, 1,  0, 3, 2,  4, 6, 5,  4, 7, 6,  0, 1, 4,  5, 4, 1,  3, 6, 2,  3, 7, 6,  1, 2, 6,  1, 6, 5,  0, 4, 3,  3, 4, 7]},
                                                  algorithms={"template":"Vec3d"},
                                                  isMechanical=False)
    CollisionBoxCollision.addObject("TriangleCollisionModel", selfCollision="0", topology="@container",simulated="0",group=[1, 2],proximity="3" )

    # TODO: Make addVisualModel accessible here. Maybe wrap the child with a better wrapper ? Add new abstraction layer with function not in prefab but working as is
    CollisionBoxCollisionVisu = CollisionBoxCollision.addChild("Visu")
    CollisionBoxCollisionVisu.addObject("OglModel", name="VisualModel", color="0.5 0.5 0.5 0.2", src="@../container" )
    CollisionBoxCollisionVisu.addObject("IdentityMapping", name="MappingVisu", isMechanical="false", input="@../mstate", output="@VisualModel" )


