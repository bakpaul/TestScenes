#Required import for python
import Sofa
import SofaRuntime
from Sofa import SofaLinearSolver
import numpy as np
import scipy


# Function called when the scene graph is being created
def createScene(root):

    root.gravity=[0,0,0]
    root.dt = 0.01

    #Loading the dynamic libraries required for this scene
    root.addObject("PluginManager",pluginName=["Sofa.Component.IO.Mesh", "Sofa.Component.LinearSolver.Direct", "Sofa.Component.LinearSolver.Iterative",
                                               "Sofa.Component.Mapping.Linear", "Sofa.Component.Mass", "Sofa.Component.ODESolver.Backward", "Sofa.Component.Setting",
                                               "Sofa.Component.SolidMechanics.FEM.Elastic", "Sofa.Component.StateContainer", "Sofa.Component.Topology.Container.Dynamic",
                                               "Sofa.Component.Visual", "Sofa.GL.Component.Rendering3D", "Sofa.Component.AnimationLoop", "Sofa.Component.Collision.Detection.Algorithm",
                                               "Sofa.Component.Collision.Detection.Intersection", "Sofa.Component.Collision.Geometry", "Sofa.Component.Collision.Response.Contact",
                                               "Sofa.Component.Constraint.Lagrangian.Solver", "Sofa.Component.Constraint.Lagrangian.Correction", "Sofa.Component.LinearSystem",
                                               "Sofa.Component.MechanicalLoad", "MultiThreading", "Sofa.Component.SolidMechanics.Spring", "Sofa.Component.Constraint.Lagrangian.Model",
                                               "Sofa.Component.Mapping.NonLinear", "Sofa.Component.Topology.Container.Constant", "Sofa.Component.Topology.Mapping", "CSparseSolvers",
                                               "Sofa.Component.Topology.Container.Grid", "Sofa.Component.Engine.Select"])

    # Rendering settings
    root.addObject("VisualStyle", name="RenderingOptions", displayFlags="showVisualModels" )
    root.addObject("BackgroundSetting", color="0.8 0.8 0.8 1" )

    # The presence of this component sets the mouse interaction to Lagrangian-based constraints at the GUI launch
    root.addObject("ConstraintAttachButtonSetting" )

    # Header of the simulation
    root.addObject("FreeMotionAnimationLoop", name="FreeMotionAnimationLoop", parallelODESolving="true", parallelCollisionDetectionAndFreeMotion="true")
    root.addObject("GenericConstraintSolver", maxIterations="20", multithreading='true', tolerance="1.0e-4")

    # Definition of the collision pipeline
    root.addObject("CollisionPipeline", name="CollisionPipeline" )
    root.addObject("ParallelBruteForceBroadPhase", name="CollisionBroadPhase")
    root.addObject("ParallelBVHNarrowPhase", name="CollisionNarrowPhase")
    root.addObject("CollisionResponse", name="CollisionResponse", response="FrictionContactConstraint", responseParams="mu=0.5")
    root.addObject("NewProximityIntersection", name="Intersection", alarmDistance="0.3", contactDistance="0.02" )


    # Object = SOFA Logo
    SOFALogo = root.addChild("SOFALogo")
    SOFALogo.addObject("EulerImplicitSolver", name="EulerImplicitScheme", )
    SOFALogo.addObject("ConstantSparsityPatternSystem", template="CompressedRowSparseMatrixd", name="A", printLog="false")
    SOFALogo.addObject("EigenSimplicialLDLT", name="LDLTLinearSolver", template="CompressedRowSparseMatrixd",  parallelInverseProduct="true",  linearSystem="@A")

    SOFALogo.addObject("MeshVTKLoader", name="LogoLoader", filename="../Data/graph.vtk"  )
    SOFALogo.addObject("TetrahedronSetTopologyContainer", name="Container", src="@LogoLoader" )
    SOFALogo.addObject("TetrahedronSetTopologyModifier", name="Modifier",)
    SOFALogo.addObject("MechanicalObject", name="LogoDOF", template="Vec3d" )
    SOFALogo.addObject("TetrahedronFEMForceField", name="LinearElasticityFEM",  youngModulus="200", poissonRatio="0.4", method="large" )
    SOFALogo.addObject("ConstantForceField", name="ConstantForceUpwards", totalForce="0 0 -5.0" )
    SOFALogo.addObject("MeshMatrixMass", name="Mass", totalMass="0.1" )

    SOFACollision = SOFALogo.addChild("Collision")
    SOFACollision.addObject("SphereLoader", name="SphereLoader", filename="../Data/Logo.sph" )
    SOFACollision.addObject("MechanicalObject", name="CollisionDOF", position="@SphereLoader.position" )
    SOFACollision.addObject("SphereCollisionModel", name="CollisionModel", listRadius="@SphereLoader.listRadius")
    SOFACollision.addObject("BarycentricMapping", name="MappingCollision", input="@../LogoDOF", output="@CollisionDOF")


    SOFAVisu = SOFALogo.addChild("Visu")
    SOFAVisu.addObject("MeshOBJLoader", name="SurfaceLoader", filename="../Data/graph_t.obj")
    SOFAVisu.addObject("OglModel", name="VisualModel", color="0.7 .35 0 0.8", position="@SurfaceLoader.position", triangles="@SurfaceLoader.triangles" )
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
    SLICERLogo.addObject("TetrahedronFEMForceField", name="LinearElasticityFEM",  youngModulus="200", poissonRatio="0.4", method="large" )
    SLICERLogo.addObject("ConstantForceField", name="ConstantForceUpwards", totalForce="0 0 -5.0" )
    SLICERLogo.addObject("MeshMatrixMass", name="Mass", totalMass="0.1" )

    SLICERCollision = SOFALogo.addChild("Collision")
    SLICERCollision.addObject("SphereLoader", name="SphereLoader", filename="../Data/Logo.sph" )
    SLICERCollision.addObject("MechanicalObject", name="CollisionDOF", position="@SphereLoader.position" )
    SLICERCollision.addObject("SphereCollisionModel", name="CollisionModel", listRadius="@SphereLoader.listRadius")
    SLICERCollision.addObject("BarycentricMapping", name="MappingCollision", input="@../LogoDOF", output="@CollisionDOF")


    SLICERVisu = SOFALogo.addChild("Visu")
    SLICERVisu.addObject("MeshOBJLoader", name="SurfaceLoader", filename="../Data/graph_t.obj")
    SLICERVisu.addObject("OglModel", name="VisualModel", color="0.7 .35 0 0.8", position="@SurfaceLoader.position", triangles="@SurfaceLoader.triangles" )
    SLICERVisu.addObject("BarycentricMapping", name="MappingVisu", isMechanical="false", input="@../LogoDOF", output="@VisualModel" )


    SLICERLogo.addObject("LinearSolverConstraintCorrection", name="ConstraintCorrection", linearSolver="@LDLTLinearSolver")
