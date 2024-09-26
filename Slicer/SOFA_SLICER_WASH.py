#Required import for python
import Sofa
import SofaRuntime
from Sofa import SofaLinearSolver
import numpy as np
import scipy


# Function called when the scene graph is being created
def createScene(root):

    root.gravity=[0,-100,0]
    root.dt = 0.01

    #Loading the dynamic libraries required for this scene
    root.addObject("RequiredPlugin",pluginName=["Sofa.Component.IO.Mesh", "Sofa.Component.LinearSolver.Direct", "Sofa.Component.LinearSolver.Iterative",
                                               "Sofa.Component.Mapping.Linear", "Sofa.Component.Mass", "Sofa.Component.ODESolver.Backward", "Sofa.Component.Setting",
                                               "Sofa.Component.SolidMechanics.FEM.Elastic", "Sofa.Component.StateContainer", "Sofa.Component.Topology.Container.Dynamic",
                                               "Sofa.Component.Visual", "Sofa.GL.Component.Rendering3D", "Sofa.Component.AnimationLoop", "Sofa.Component.Collision.Detection.Algorithm",
                                               "Sofa.Component.Collision.Detection.Intersection", "Sofa.Component.Collision.Geometry", "Sofa.Component.Collision.Response.Contact",
                                               "Sofa.Component.Constraint.Lagrangian.Solver", "Sofa.Component.Constraint.Lagrangian.Correction", "Sofa.Component.LinearSystem",
                                               "Sofa.Component.MechanicalLoad", "MultiThreading", "Sofa.Component.SolidMechanics.Spring", "Sofa.Component.Constraint.Lagrangian.Model",
                                               "Sofa.Component.Mapping.NonLinear", "Sofa.Component.Topology.Container.Constant", "Sofa.Component.Topology.Mapping",
                                               "Sofa.Component.Topology.Container.Grid", "Sofa.Component.Engine.Select", "Sofa.Component.Constraint.Projective"])

    # Rendering settings
    root.addObject("VisualStyle", name="RenderingOptions", displayFlags="showVisualModels" )
    root.addObject("BackgroundSetting", color="0.8 0.8 0.8 1" )


    # Header of the simulation
    root.addObject("FreeMotionAnimationLoop", name="FreeMotionAnimationLoop", parallelODESolving="true", parallelCollisionDetectionAndFreeMotion="true")
    root.addObject("GenericConstraintSolver", maxIterations="50", multithreading='true', tolerance="1.0e-3")

    # Definition of the collision pipeline
    root.addObject("CollisionPipeline", name="CollisionPipeline" )
    root.addObject("ParallelBruteForceBroadPhase", name="CollisionBroadPhase")
    root.addObject("ParallelBVHNarrowPhase", name="CollisionNarrowPhase")
    root.addObject("CollisionResponse", name="CollisionResponse", response="FrictionContactConstraint", responseParams="mu=0.2")
    root.addObject("NewProximityIntersection", name="Intersection", alarmDistance="10", contactDistance="5" )


    # Object = SOFA Logo
    SOFALogo = root.addChild("SOFALogo")
    SOFALogo.addObject("EulerImplicitSolver", name="EulerImplicitScheme", )
    SOFALogo.addObject("ConstantSparsityPatternSystem", template="CompressedRowSparseMatrixd", name="A", printLog="false")
    SOFALogo.addObject("EigenSimplicialLDLT", name="LDLTLinearSolver", template="CompressedRowSparseMatrixd",  parallelInverseProduct="true",  linearSystem="@A")

    SOFALogo.addObject("MeshVTKLoader", name="LogoLoader", filename="../Data/SOFA_volume.vtk", translation="-120 20 0", rotation="180 0 90")
    SOFALogo.addObject("TetrahedronSetTopologyContainer", name="Container", src="@LogoLoader" )
    SOFALogo.addObject("TetrahedronSetTopologyModifier", name="Modifier",)
    SOFALogo.addObject("MechanicalObject", name="LogoDOF", template="Vec3d" )
    SOFALogo.addObject("TetrahedronFEMForceField", name="LinearElasticityFEM",  youngModulus="5", poissonRatio="0.3", method="large" )
    SOFALogo.addObject("MeshMatrixMass", name="Mass", totalMass="0.1" )

    SOFACollision = SOFALogo.addChild("Collision")
    SOFACollision.addObject("MeshOBJLoader", name="SurfaceLoader", filename="../Data/SOFA_collision_no_face.obj", translation="-120 20 0",rotation="180 0 90")
    SOFACollision.addObject("MeshTopology", name="CollisionTopo", src="@SurfaceLoader")
    SOFACollision.addObject("MechanicalObject", name="CollisionDOF", src="@CollisionTopo" )
    SOFACollision.addObject("LineCollisionModel", selfCollision="1", topology="@CollisionTopo",group=[2, 3, 5])
    SOFACollision.addObject("BarycentricMapping", name="MappingCollision", input="@../LogoDOF", output="@CollisionDOF")


    SOFACollisionBorder = SOFALogo.addChild("BorderCollision")
    SOFACollisionBorder.addObject("MeshOBJLoader", name="SurfaceLoader", filename="../Data/SOFA_collision_center.obj", translation="-120 20 0",rotation="180 0 90")
    SOFACollisionBorder.addObject("MeshTopology", name="CollisionTopo", src="@SurfaceLoader")
    SOFACollisionBorder.addObject("MechanicalObject", name="CollisionDOF", src="@CollisionTopo" )
    SOFACollisionBorder.addObject("LineCollisionModel", selfCollision="1", topology="@CollisionTopo",group=[3, 4 ])
    SOFACollisionBorder.addObject("BarycentricMapping", name="MappingCollision", input="@../LogoDOF", output="@CollisionDOF")



    SOFAVisu = SOFALogo.addChild("Visu")
    SOFAVisu.addObject("MeshOBJLoader", name="SurfaceLoader", filename="../Data/SOFA_surface.obj", translation="-120 20 0", rotation="180 0 90")
    SOFAVisu.addObject("OglModel", name="VisualModel", color="0.7 .35 0 1", position="@SurfaceLoader.position", triangles="@SurfaceLoader.triangles" )
    SOFAVisu.addObject("BarycentricMapping", name="MappingVisu", isMechanical="false", input="@../LogoDOF", output="@VisualModel" )

    SOFALogo.addObject("LinearSolverConstraintCorrection", name="ConstraintCorrection", linearSolver="@LDLTLinearSolver")

    # Object = Slicer Logo
    SLICERLogo = root.addChild("SlicerLogo")
    SLICERLogo.addObject("EulerImplicitSolver", name="EulerImplicitScheme", )
    SLICERLogo.addObject("ConstantSparsityPatternSystem", template="CompressedRowSparseMatrixd", name="A", printLog="false")
    SLICERLogo.addObject("EigenSimplicialLDLT", name="LDLTLinearSolver", template="CompressedRowSparseMatrixd",  parallelInverseProduct="true",  linearSystem="@A")

    SLICERLogo.addObject("MeshVTKLoader", name="LogoLoader", filename="../Data/Slicer_volume.vtk"  )
    SLICERLogo.addObject("TetrahedronSetTopologyContainer", name="Container", src="@LogoLoader" )
    SLICERLogo.addObject("TetrahedronSetTopologyModifier", name="Modifier",)
    SLICERLogo.addObject("MechanicalObject", name="LogoDOF", template="Vec3d" )
    SLICERLogo.addObject("TetrahedronFEMForceField", name="LinearElasticityFEM",  youngModulus="1", poissonRatio="0.3", method="large" )
    SLICERLogo.addObject("MeshMatrixMass", name="Mass", totalMass="0.05" )

    SLICERCollision = SLICERLogo.addChild("Collision")
    SLICERCollision.addObject("MeshOBJLoader", name="SurfaceLoader", filename="../Data/Slicer_collision_no_face.obj")
    SLICERCollision.addObject("MeshTopology", name="CollisionTopo", src="@SurfaceLoader")
    SLICERCollision.addObject("MechanicalObject", name="CollisionDOF", src="@CollisionTopo" )
    SLICERCollision.addObject("LineCollisionModel", selfCollision="0", topology="@CollisionTopo",group=[1, 4, 6])
    SLICERCollision.addObject("BarycentricMapping", name="MappingCollision", input="@../LogoDOF", output="@CollisionDOF")


    SLICERCollisionBorder = SLICERLogo.addChild("CollisionBorder")
    SLICERCollisionBorder.addObject("MeshOBJLoader", name="SurfaceLoader", filename="../Data/Slicer_collision_center.obj")
    SLICERCollisionBorder.addObject("MeshTopology", name="CollisionTopo", src="@SurfaceLoader")
    SLICERCollisionBorder.addObject("MechanicalObject", name="CollisionDOF", src="@CollisionTopo" )
    SLICERCollisionBorder.addObject("LineCollisionModel", selfCollision="0", topology="@CollisionTopo",group=[5, 6])
    SLICERCollisionBorder.addObject("BarycentricMapping", name="MappingCollision", input="@../LogoDOF", output="@CollisionDOF")


    SLICERVisu = SLICERLogo.addChild("Visu")
    SLICERVisu.addObject("MeshOBJLoader", name="SurfaceLoader", filename="../Data/Slicer_surface.obj")
    SLICERVisu.addObject("OglModel", name="VisualModel", color="0.7 0.7 0.7 1", position="@SurfaceLoader.position", triangles="@SurfaceLoader.triangles" )
    SLICERVisu.addObject("BarycentricMapping", name="MappingVisu", isMechanical="false", input="@../LogoDOF", output="@VisualModel" )


    SLICERLogo.addObject("LinearSolverConstraintCorrection", name="ConstraintCorrection", linearSolver="@LDLTLinearSolver")


    CollisionBox = root.addChild("Box")
    CollisionBox.addObject("EulerImplicitSolver", name="EulerImplicitScheme" )
    CollisionBox.addObject("EigenSparseLU", name="LUSolver", template="CompressedRowSparseMatrixd")
    CollisionBox.addObject("MechanicalObject",name="mstate", template="Rigid3", position="0 0 0 0 0 0 1")
    CollisionBox.addObject("LinearVelocityProjectiveConstraint",indices="0",keyTimes="0 2", velocities="0 0 0 0 0 0 0 0 0 0 0 0.3 ",continueAfterEnd=True)
    CollisionBox.addObject("UniformMass", name="Mass", totalMass="0.1" )

    CollisionBoxCollision = CollisionBox.addChild("Collision")
    CollisionBoxCollision.addObject("TriangleSetTopologyContainer",name="FloorTopology", position="-200 -200 15    200 -200 15   200 200 15   -200 200 15   -200 -200 -15   200 -200 -15   200 200 -15   -200 200 -15",
                                    triangles="0 2 1  0 3 2   4 6 5  4 7 6   0 1 4  5 4 1   3 6 2  3 7 6   1 2 6  1 6 5  0 4 3  3 4 7")
    CollisionBoxCollision.addObject("MechanicalObject",name="CollisionDOF", template="Vec3")
    CollisionBoxCollision.addObject("TriangleCollisionModel", selfCollision="0", topology="@FloorTopology",simulated="0",group=[1, 2],proximity="3" )

    CollisionBoxCollisionVisu = CollisionBoxCollision.addChild("Visu")
    CollisionBoxCollisionVisu.addObject("OglModel", name="VisualModel", color="0.5 0.5 0.5 0.2", src="@../FloorTopology" )
    CollisionBoxCollisionVisu.addObject("BarycentricMapping", name="MappingVisu", isMechanical="false", input="@../CollisionDOF", output="@VisualModel" )

    CollisionBoxCollision.addObject("RigidMapping", name="MappingCollision", input="@../mstate", output="@CollisionDOF", globalToLocalCoords="true")

