#Required import for python
import Sofa
import SofaRuntime
from Sofa import SofaLinearSolver
import numpy as np
import scipy


# Function called when the scene graph is being created
def createScene(sofa_root_node : Sofa.Core.Node):

    sofa_root_node.gravity = [0,-100,0]
    sofa_root_node.dt = 0.01

    #Loading the dynamic libraries required for this scene
    sofa_root_node.addObject("RequiredPlugin",pluginName=["Sofa.Component.IO.Mesh", "Sofa.Component.LinearSolver.Direct", "Sofa.Component.LinearSolver.Iterative",
                                               "Sofa.Component.Mapping.Linear", "Sofa.Component.Mass", "Sofa.Component.ODESolver.Backward", "Sofa.Component.Setting",
                                               "Sofa.Component.SolidMechanics.FEM.Elastic", "Sofa.Component.StateContainer", "Sofa.Component.Topology.Container.Dynamic",
                                               "Sofa.Component.Visual", "Sofa.GL.Component.Rendering3D", "Sofa.Component.AnimationLoop", "Sofa.Component.Collision.Detection.Algorithm",
                                               "Sofa.Component.Collision.Detection.Intersection", "Sofa.Component.Collision.Geometry", "Sofa.Component.Collision.Response.Contact",
                                               "Sofa.Component.Constraint.Lagrangian.Solver", "Sofa.Component.Constraint.Lagrangian.Correction", "Sofa.Component.LinearSystem",
                                               "Sofa.Component.MechanicalLoad", "MultiThreading", "Sofa.Component.SolidMechanics.Spring", "Sofa.Component.Constraint.Lagrangian.Model",
                                               "Sofa.Component.Mapping.NonLinear", "Sofa.Component.Topology.Container.Constant", "Sofa.Component.Topology.Mapping",
                                               "Sofa.Component.Topology.Container.Grid", "Sofa.Component.Engine.Select", "Sofa.Component.Constraint.Projective"])

    # Rendering settings
    sofa_root_node.addObject("VisualStyle", name="RenderingOptions", displayFlags="showVisualModels showBehaviorModels" )
    sofa_root_node.addObject("BackgroundSetting", color=[0.8, 0.8, 0.8, 1] )



    # Header of the simulation
    sofa_root_node.addObject("FreeMotionAnimationLoop", name="FreeMotionAnimationLoop")#, parallelODESolving="true", parallelCollisionDetectionAndFreeMotion=True)
    sofa_root_node.addObject("GenericConstraintSolver", maxIterations=50, tolerance=1.0e-3)# ,multithreading=True)
    # sofa_root_node.addObject("ConstraintAttachButtonSetting" )

    # Object = Slicer Logo
    SLICERLogo = sofa_root_node.addChild("SlicerLogo")
    SLICERLogo.addObject("EulerImplicitSolver", name="EulerImplicitScheme", rayleighMass=0.1, rayleighStiffness=0.1)
    SLICERLogo.addObject("ConstantSparsityPatternSystem", template="CompressedRowSparseMatrixd", name="A", printLog=False)
    SLICERLogo.addObject("EigenSimplicialLDLT", name="LDLTLinearSolver", template="CompressedRowSparseMatrixd",  linearSystem="@A")#,  parallelInverseProduct=True)

    SLICERLogo.addObject("MeshVTKLoader", name="LogoLoader", filename="../../Data/Slicer_volume.vtk"  )
    SLICERLogo.addObject("TetrahedronSetTopologyContainer", name="Container", src="@LogoLoader" )
    SLICERLogo.addObject("TetrahedronSetTopologyModifier", name="Modifier",)
    SLICERLogo.addObject("MechanicalObject", name="LogoDOF", template="Vec3d" )
    SLICERLogo.addObject("TetrahedronFEMForceField", name="LinearElasticityFEM",  youngModulus=1, poissonRatio=0.3, method="large" )
    SLICERLogo.addObject("MeshMatrixMass", name="Mass", totalMass=0.05 )

    AttachementIndices = SLICERLogo.addObject("SphereROI",name="AttachementIndices",centers=[-120, 25, 0], radii=40, drawROI=True)
    SLICERLogo.addObject("RestShapeSpringsForceField", points=AttachementIndices.indices.linkpath, stiffness=1000)

    ExternalForcesIndices=SLICERLogo.addObject("BoxROI",name="ExternalForces", box=[-70, 90, -11, 0, 160, 11], drawROI=True)
    SLICERLogo.addObject("ConstantForceField", indices=ExternalForcesIndices.indices.linkpath, totalForce=[0,-50,40])



    SLICERCollisionBorder = SLICERLogo.addChild("CollisionBorder")
    SLICERCollisionBorder.addObject("MeshOBJLoader", name="SurfaceLoader", filename="../../Data/Slicer_surface.obj")
    SLICERCollisionBorder.addObject("MeshTopology", name="CollisionTopo", src="@SurfaceLoader")
    SLICERCollisionBorder.addObject("MechanicalObject", name="CollisionDOF", src="@CollisionTopo" )
    SLICERCollisionBorder.addObject("LineCollisionModel", selfCollision=False, topology="@CollisionTopo")
    SLICERCollisionBorder.addObject("BarycentricMapping", name="MappingCollision", input="@../LogoDOF", output="@CollisionDOF")


    SLICERVisu = SLICERLogo.addChild("Visu")
    SLICERVisu.addObject("MeshOBJLoader", name="SurfaceLoader", filename="../../Data/Slicer_surface.obj")
    SLICERVisu.addObject("OglModel", name="VisualModel", color=[0.7, 0.7, 0.7, 1], position="@SurfaceLoader.position", triangles="@SurfaceLoader.triangles" )
    SLICERVisu.addObject("BarycentricMapping", name="MappingVisu", isMechanical="false", input="@../LogoDOF", output="@VisualModel" )


    SLICERLogo.addObject("LinearSolverConstraintCorrection", name="ConstraintCorrection", linearSolver="@LDLTLinearSolver")

