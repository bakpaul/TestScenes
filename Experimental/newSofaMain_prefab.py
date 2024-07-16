import Sofa
from splib.simulation.headers import *
from splib.prefabs.utils import PrefabSimulation
from splib.topology.dynamic import ElementType
from splib.prefabs.parameters import *
from splib.Testing import exportScene

@PrefabSimulation
def createScene(rootNode):


    ## TODO : make this affect the actual dt and gravity of the SOFA node
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
                                       linearSolverParams=DirectLinearSolverParameters(constantSparsity=True,template="CompressedRowSparseMatrixd"))

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
                                    linearSolverParams=DirectLinearSolverParameters(constantSparsity=True,template="CompressedRowSparseMatrixd"))

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
                                    topologyParams=TopologyParameters(filename="../Data/O.vtk",generateSparseGrid=True,sparseGridSize="4 2 4"),
                                    linearSolverParams=DirectLinearSolverParameters(constantSparsity=True,template="CompressedRowSparseMatrixd"))

    O.addConstitutiveModel(law=ConstitutiveLaw.LINEAR_COROT,
                           lawParams=LinearConstitutiveLawParameters(youngModulus="200", poissonRatio="0.45", method="large"),
                           massParams=MassParameters(totalMass="0.15"))
    O.addCollisionModel(collisionParameters =CollisionParameters(edges=True,selfCollision=False,proximity=0.2),
                        filename="../Data/O.vtk")
    O.addVisualModel(color="white",
                     filename="../Data/O_t.obj")


    return rootNode

if __name__ == "__main__":
    Node = exportScene()
    createScene(Node)



# <?xml version="1.0"?>
#
# <Node name="root" dt="0.01" gravity="0 0 9.81" >
#     <!-- Loading the dynamic libraries required for this scene -->
#     <RequiredPlugin name="PluginManager"
#         pluginName="Sofa.Component.IO.Mesh Sofa.Component.LinearSolver.Direct Sofa.Component.LinearSolver.Iterative
#         Sofa.Component.Mapping.Linear Sofa.Component.Mass Sofa.Component.ODESolver.Backward Sofa.Component.Setting
#         Sofa.Component.SolidMechanics.FEM.Elastic Sofa.Component.StateContainer Sofa.Component.Topology.Container.Dynamic
#         Sofa.Component.Visual Sofa.GL.Component.Rendering3D Sofa.Component.AnimationLoop Sofa.Component.Collision.Detection.Algorithm
#         Sofa.Component.Collision.Detection.Intersection Sofa.Component.Collision.Geometry Sofa.Component.Collision.Response.Contact
#         Sofa.Component.Constraint.Lagrangian.Solver Sofa.Component.Constraint.Lagrangian.Correction Sofa.Component.LinearSystem
#         Sofa.Component.MechanicalLoad MultiThreading Sofa.Component.SolidMechanics.Spring Sofa.Component.Constraint.Lagrangian.Model
#         Sofa.Component.Mapping.NonLinear Sofa.Component.Topology.Container.Constant Sofa.Component.Topology.Mapping CSparseSolvers
#         Sofa.Component.Topology.Container.Grid Sofa.Component.Engine.Select" />
#
#     <!-- Rendering settings -->
#     <VisualStyle name="RenderingOptions" displayFlags="showVisualModels" />
#     <BackgroundSetting color="0.8 0.8 0.8 1" />
#
#     <!-- Define Mouse left click as a Bilateral Lagrangian constraint -->
#     <!-- TODO -->
#     <!-- <ConstraintAttachButtonSetting /> in #4601 -->
#
#     <!-- Header of the simulation -->
#     <FreeMotionAnimationLoop name="FreeMotionAnimationLoop" parallelODESolving="true" parallelCollisionDetectionAndFreeMotion="true"/>
#     <GenericConstraintSolver maxIterations="10" multithreading='true' tolerance="1.0e-3"/>
#
#     <!-- Definition of the collision pipeline -->
#     <CollisionPipeline name="CollisionPipeline" />
#     <ParallelBruteForceBroadPhase name="CollisionBroadPhase"/>
#     <ParallelBVHNarrowPhase name="CollisionNarrowPhase"/>
#     <CollisionResponse name="CollisionResponse" response="FrictionContactConstraint" responseParams="mu=0.5" />
#     <NewProximityIntersection name="Intersection" alarmDistance="0.2" contactDistance="0.02" />
#
#
#     <!-- Object = SOFA Logo -->
#     <Node name="Logo" >
#         <EulerImplicitSolver name="EulerImplicitScheme" />
#         <ConstantSparsityPatternSystem template="CompressedRowSparseMatrixd" name="A" printLog="false"/>
#         <EigenSimplicialLDLT name="LDLTLinearSolver" template="CompressedRowSparseMatrixd"  parallelInverseProduct="true"  linearSystem="@A"/>
#
#         <MeshVTKLoader name="LogoLoader" filename="../Data/graph.vtk"  />
#         <TetrahedronSetTopologyContainer name="Container" src="@LogoLoader" />
#         <TetrahedronSetTopologyModifier name="Modifier"/>
#         <MechanicalObject name="LogoDOF" template="Vec3d" />
#         <TetrahedronFEMForceField name="LinearElasticityFEM"  youngModulus="200" poissonRatio="0.4" method="large" />
#         <ConstantForceField name="ConstantForceUpwards" totalForce="0 0 -5.0" />
#         <MeshMatrixMass name="Mass" totalMass="0.1" />
#
#         <Node name="Collision">
#             <SphereLoader name="SphereLoader" filename="../Data/Logo.sph" />
#             <MechanicalObject name="CollisionDOF" position="@SphereLoader.position" />
#             <SphereCollisionModel name="CollisionModel" listRadius="@SphereLoader.listRadius"/>
#             <BarycentricMapping name="MappingCollision" input="@../LogoDOF" output="@CollisionDOF"/>
#         </Node>
#
#         <Node name="Visu">
#             <MeshOBJLoader name="SurfaceLoader" filename="../Data/graph_t.obj"/>
#             <OglModel name="VisualModel" color="0.7 .35 0 0.8" position="@SurfaceLoader.position" triangles="@SurfaceLoader.triangles" />
#             <BarycentricMapping name="MappingVisu" isMechanical="false" input="@../LogoDOF" output="@VisualModel" />
#         </Node>
#
#         <Node name="AttachmentPoint">
#             <MechanicalObject name="Points" template="Vec3" position="12 0 -9"  />
#             <BarycentricMapping name="MappingAttachmentPoint" input="@../LogoDOF" output="@Points" />
#         </Node>
#
#         <LinearSolverConstraintCorrection name="ConstraintCorrection" linearSolver="@LDLTLinearSolver"/>
#     </Node>
#
#
#     <!-- Object = beam connecting the SOFA logo and the S letter -->
#     <Node name="BeamModel">
#         <EulerImplicitSolver name="EulerImplicitScheme"  printLog="false" />
#         <SparseLUSolver name="LULinearSolver" template="CompressedRowSparseMatrixd" />
#
#         <MechanicalObject template="Rigid3d" name="BeamDOF" position="12 0 -9  0.707 0 0.707 0
#                                                                    12 0 -8  0.707 0 0.707 0
#                                                                    12 0 -7  0.707 0 0.707 0
#                                                                    12 0 -6  0.707 0 0.707 0
#                                                                    12 0 -5.5  0.707 0 0.707 0" />
#         <MeshTopology name="LineTopology" position="@BeamDOF.position" lines="0 1 1 2 2 3 3 4 " drawEdges="1"/>
#         <BeamInterpolation name="BeamInterpolation" radius="0.1" defaultYoungModulus="10000 10000 10000" defaultPoissonRatio="0.4"/>
#         <AdaptiveBeamForceFieldAndMass name="BeamForceFieldAndMass"  computeMass="1" massDensity="1"/>
#
#         <Node name="BeamExtremities">
#             <MechanicalObject name="Points" template="Vec3" position="12 0 -9 12 0 -5.5 " />
#             <RigidMapping name="MappingBeamExtremities" globalToLocalCoords="true" rigidIndexPerPoint="0 4" />
#         </Node>
#
#         <LinearSolverConstraintCorrection name="ConstraintCorrection" linearSolver="@LULinearSolver"/>
#     </Node>
#
#
#     <!-- Object = S letter as a 3D deformable object -->
#     <Node name="S" >
#         <EulerImplicitSolver name="EulerImplicitScheme" rayleighMass="0.1" rayleighStiffness="0.1" />
#         <ConstantSparsityPatternSystem template="CompressedRowSparseMatrixd" name="A" printLog="false"/>
#         <SparseLDLSolver name="LDLLinearSolver" template="CompressedRowSparseMatrixd" parallelInverseProduct="true" linearSystem="@A"/>
#
#         <MeshVTKLoader name="SLoader" filename="../Data/S.vtk"  />
#         <TetrahedronSetTopologyContainer name="Container" src="@SLoader" />
#         <TetrahedronSetTopologyModifier name="Modifier"/>
#         <MechanicalObject name="SDOF" template="Vec3d" />
#         <TetrahedronFEMForceField name="LinearElasticityFEM" youngModulus="200" poissonRatio="0.45" method="large" />
#         <MeshMatrixMass name="Mass" totalMass="0.15" />
#
#         <Node name="Collision">
#             <TriangleSetTopologyContainer name="Container" />
#             <TriangleSetTopologyModifier name="Modifier"/>
#             <Tetra2TriangleTopologicalMapping name="MappingExtractingSurface" input="@../Container" output="@Container" />
#
#             <MechanicalObject name="CollisionDOF" rest_position="@../SDOF.rest_position"  />
#             <TriangleCollisionModel name="CollisionModel" proximity="0.02" />
#             <IdentityMapping name="MappingCollision" input="@../SDOF" output="@CollisionDOF"/>
#         </Node>
#
#         <Node name="Visu">
#             <MeshOBJLoader name="SurfaceLoader" filename="../Data/S_t.obj"/>
#             <OglModel name="VisualModel" color="0.7 0.7 0.7 0.8" position="@SurfaceLoader.position" triangles="@SurfaceLoader.triangles" />
#             <BarycentricMapping name="MappingVisu" input="@../SDOF" output="@VisualModel" isMechanical="false" />
#         </Node>
#
#         <Node name="AttachmentPoint">
#             <MechanicalObject name="Points" template="Vec3" position="12 0 -5.5"  />
#             <BarycentricMapping name="MappingAttachmentPoint" input="@../SDOF" output="@Points" />
#         </Node>
#
#         <LinearSolverConstraintCorrection name="ConstraintCorrection" linearSolver="@LDLLinearSolver"/>
#     </Node>
#
#
#     <!-- Connect the two beam extremities with the SOFA logo and the S letter -->
#     <!-- TODO : rename BilateralLagrangianConstraint -->
#     <BilateralInteractionConstraint template="Vec3" object1="@Logo/AttachmentPoint/Points" object2="@BeamModel/BeamExtremities/Points" first_point="0" second_point="0" />
#     <BilateralInteractionConstraint template="Vec3" object1="@S/AttachmentPoint/Points" object2="@BeamModel/BeamExtremities/Points" first_point="0" second_point="1" />
#
#
#     <!-- Object = O letter as a 3D deformable object (FEM grid) -->
#     <Node name="O" >
#         <MeshOBJLoader name="OLoader" filename="../Data/O_t.obj"/>
#
#         <SparseGridRamificationTopology name="SparseGrid" n="4 2 4" position="@OLoader.position" nbVirtualFinerLevels="2" finestConnectivity="0"/>
#         <HexahedronSetTopologyContainer name="HexaTopology" src="@SparseGrid"/>
#
#         <EulerImplicitSolver name="EulerImplicitScheme" />
#         <ConstantSparsityPatternSystem template="CompressedRowSparseMatrixd" name="A" printLog="false"/>
#         <SparseLDLSolver name="precond" template="CompressedRowSparseMatrixd"  parallelInverseProduct="true"  linearSystem="@A"/>
#
#         <MechanicalObject name="ODOF" position="@HexaTopology.position"  />
#         <UniformMass name="Mass" totalMass="0.1" />
#         <HexahedronFEMForceField name="LinearElasticityFEM" youngModulus="20" poissonRatio="0.49" method="large" updateStiffnessMatrix="false" printLog="0" />
#         <UncoupledConstraintCorrection name="UncoupledConstraintCorrection" defaultCompliance="38240" useOdeSolverIntegrationFactors="0"/>
#
#         <Node name="Collision">
#             <MeshTopology name="CollisionTopology" src="@../OLoader"/>
#             <MechanicalObject name="CollisionDOF" src="@CollisionTopology" />
#             <LineCollisionModel name="LineCollisionModel" selfCollision="0" topology="@CollisionTopology" />
#             <BarycentricMapping name="MappingCollision" input="@../ODOF" output="@CollisionDOF" />
#         </Node>
#
#         <Node name="Visu" >
#             <OglModel  name="VisualModel" src="@../OLoader" color="white" />
#             <BarycentricMapping name="MappingVisu" input="@../ODOF" output="@VisualModel" />
#         </Node>
#     </Node>
#
#
#     <!-- Object = F letter as a rigid frame -->
#     <Node name="F" >
#         <EulerImplicitSolver name="EulerImplicitScheme" />
#         <SparseLDLSolver name="LDLLinearSolver" template="CompressedRowSparseMatrixd"  />
#         <MechanicalObject name="FDOF" template="Rigid3d" position="23.15 0 -2.7 0 0 0 1"/>
#         <UniformMass name="Mass" totalMass="0.1" />
#
#         <Node name="Collision">
#             <MeshOBJLoader name="SkeletonLoader" filename="../Data/F_Skel.obj"/>
#             <TriangleSetTopologyContainer name="Container" src="@SkeletonLoader"/>
#             <TriangleSetTopologyModifier name="Modifier"/>
#
#             <MechanicalObject name="CollisionDOF" src="@SkeletonLoader" template="Vec3d"  />
#             <LineCollisionModel name="CenterLineCollisionModel" proximity="0.5" />
#             <RigidMapping name="MappingCollision" input="@../FDOF" output="@CollisionDOF" globalToLocalCoords="true"/>
#         </Node>
#
#         <Node name="Visu">
#             <MeshOBJLoader name="SurfaceLoader" filename="../Data/F_t.obj"/>
#             <OglModel name="VisualModel" color="0.7 0.7 0.7 0.8" position="@SurfaceLoader.position" triangles="@SurfaceLoader.triangles" />
#             <RigidMapping name="SurfaceMapping" input="@../FDOF" output="@VisualModel" globalToLocalCoords="true"/>
#         </Node>
#         <LinearSolverConstraintCorrection linearSolver="@LDLLinearSolver" />
#     </Node>
#
#
#     <!-- Object = A letter as a 3D deformable object -->
#     <Node name="A" >
#         <EulerImplicitSolver name="EulerImplicitScheme" />
#         <ConstantSparsityPatternSystem template="CompressedRowSparseMatrixd" name="A" printLog="false"/>
#         <SparseLDLSolver name="LDLLinearSolver" template="CompressedRowSparseMatrixd"  parallelInverseProduct="true"  linearSystem="@A"/>
#
#
#         <MeshVTKLoader name="ALoader" filename="../Data/A.vtk"  />
#         <TetrahedronSetTopologyContainer name="Container" src="@ALoader" />
#         <TetrahedronSetTopologyModifier name="Modifier"/>
#         <!-- <TetrahedronSetGeometryAlgorithms name="Modifier"/> -->
#         <MechanicalObject name="ADOF" template="Vec3d" />
#         <TetrahedronFEMForceField name="LinearElasticityFEM"  youngModulus="30" poissonRatio="0.4" method="large" />
#         <MeshMatrixMass name="Mass" totalMass="0.1" />
#
#         <Node name="Collision">
#             <MeshOBJLoader name="CoarseCollisionSurface" filename="../Data/A-coarse.obj"  />
#             <MechanicalObject name="CollisionDOF" position="@CoarseCollisionSurface.position"/>
#             <PointCollisionModel name="Surface" proximity="0.3" />
#             <BarycentricMapping name="SurfaceMapping"/>
#         </Node>
#
#         <Node name="Visu">
#             <MeshOBJLoader name="SurfaceLoader" filename="../Data/A_t.obj"/>
#             <OglModel name="VisualModel" color="0.7 0.7 0.7 0.8" position="@SurfaceLoader.position" triangles="@SurfaceLoader.triangles" />
#             <BarycentricMapping name="SurfaceMapping" input="@../ADOF" output="@VisualModel" isMechanical="false" />
#         </Node>
#
#         <LinearSolverConstraintCorrection linearSolver="@LDLLinearSolver"/>
#     </Node>
#
#
#     <!-- Floor object used to detect collision with all letters -->
#     <Node name="Floor" tags="NoBBox" >
#         <TriangleSetTopologyContainer name="FloorTopology" position="-20 -15 1  50 -15 1  50 15 1  -20 15 1" triangles="0 2 1  0 3 2" />
#         <MechanicalObject name="FloorDOF" template="Vec3d"/>
#         <TriangleCollisionModel name="FloorCM" proximity="0.02" moving="0" simulated="0"  color="0.3 0.3 0.3 0.1"/>
#         <OglModel name="VisualModel" src="@FloorTopology"/>
#     </Node>
#
#
#      <!-- Ceil object used to detect collision with the SOFA logo -->
#      <Node name="Ceil" tags="NoBBox" >
#         <TriangleSetTopologyContainer name="CeilTopology" position="-20 -15 -20   50 -15 -20    50 15 -20    -20 15 -20" triangles="0 1 2  3 0 2" />
#         <MechanicalObject name="CeilDOF" template="Vec3d"/>
#         <TriangleCollisionModel name="CeilCM" proximity="0.02" moving="0" simulated="0" color="0.3 0.3 0.3 0.1"/>
#         <OglModel name="VisualModel" src="@CeilTopology"/>
#     </Node>
# </Node >
#
