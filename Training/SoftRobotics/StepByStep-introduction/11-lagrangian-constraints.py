def createScene(rootNode):

	rootNode.name = "rootNode"
	rootNode.dt = 0.01
	rootNode.gravity = [ 0., -9.81 ,0.]

	rootNode.addObject('FreeMotionAnimationLoop') # 1. Required for Lagrangian constraints
	rootNode.addObject('GenericConstraintSolver', maxIterations=1000, tolerance=0.001) # 2. Solver that will compute the Lagrangian multiplier value

	
	rootNode.addObject('RequiredPlugin', pluginName=['Sofa.Component.StateContainer','Sofa.Component.Mass','Sofa.Component.MechanicalLoad',
												     'Sofa.Component.LinearSolver.Iterative','Sofa.Component.ODESolver.Backward',
													 'Sofa.Component.IO.Mesh','Sofa.Component.Topology.Container.Dynamic',
													 'Sofa.Component.SolidMechanics.FEM.Elastic','Sofa.Component.Topology.Container.Constant',
													 'Sofa.Component.Visual','Sofa.Component.Mapping.Linear','Sofa.GL.Component.Rendering3D',
													 'Sofa.Component.Constraint.Projective','Sofa.Component.Engine.Select','Sofa.Component.Collision.Geometry',
													 'Sofa.Component.Collision.Detection.Intersection','Sofa.Component.Collision.Detection.Algorithm',
													 'Sofa.Component.Collision.Response.Contact', 'Sofa.GUI.Component','Sofa.Component.AnimationLoop',
													 'Sofa.Component.Constraint.Lagrangian.Correction','Sofa.Component.Constraint.Lagrangian.Correction',
													 'Sofa.Component.Constraint.Lagrangian.Solver','Sofa.Component.LinearSolver.Direct'])

	rootNode.addObject("MeshVTKLoader", name="meshLoaderCoarse", filename="../out_coarse_sofa.vtk")
	rootNode.addObject('AttachBodyButtonSetting',stiffness=1)
	
	rootNode.addObject('VisualStyle', displayFlags='showForceFields showCollisionModels showBehaviorModels showDetectionOutputs')

	rootNode.addObject('CollisionPipeline')
	rootNode.addObject('BruteForceBroadPhase')
	rootNode.addObject('BVHNarrowPhase')
	rootNode.addObject('MinProximityIntersection', name="Proximity", alarmDistance="10", contactDistance="1")
	rootNode.addObject('CollisionResponse', name="Response", response="LagrangianContactConstraint") # 3. Formulate contacts as Lagrangian constraints, specifying response="LagrangianContactConstraint"
	# responseParams="mu=0.01"

	
	mechanicalModel = rootNode.addChild("Finger")
	
	mechanicalModel.addObject("EulerImplicitSolver")
	mechanicalModel.addObject('SparseLDLSolver', template="CompressedRowSparseMatrixd") # Linear solver used to inverse A (LDL factorization)
	
	mechanicalModel.addObject("MeshTopology", name="topologyContainer", src="@../meshLoaderCoarse" )

	mechanicalModel.addObject("MechanicalObject", template="Vec3", name="StateContainer", showObject=True)
	
	mechanicalModel.addObject('TetrahedronFEMForceField', template='Vec3', poissonRatio=0.3, youngModulus=100)
	mechanicalModel.addObject('MeshMatrixMass', template='Vec3,Vec3', totalMass=0.5)
	
	mechanicalModel.addObject('BoxROI', name='boxROI', box=[-10, 0, -20, 0, 30, 20], drawBoxes=True,
						      position=mechanicalModel.StateContainer.position.linkpath,
							  tetrahedra=mechanicalModel.topologyContainer.tetrahedra.linkpath)
	mechanicalModel.addObject('FixedLagrangianConstraint', indices=mechanicalModel.boxROI.indices.linkpath)
	mechanicalModel.addObject('LinearSolverConstraintCorrection')  # 4. Define the way the Schur complement is computed

	
	visualModel = mechanicalModel.addChild("Visual")
	visualModel.addObject('MeshSTLLoader', name="loader", filename="../out_coarse_sofa.stl")
	visualModel.addObject('OglModel', name="VisualModel", src=visualModel.loader.linkpath, color=[0.7, 0.7, 0.7, 1])
	visualModel.addObject('BarycentricMapping', name="VisualMapping", input="@../StateContainer", output="@VisualModel")
	

	collisionlModel = mechanicalModel.addChild("Collision")
	collisionlModel.addObject("MeshTopology", name="topologyContainer", src=visualModel.loader.linkpath) 
	collisionlModel.addObject('MechanicalObject', name="StoringForces")
	collisionlModel.addObject('TriangleCollisionModel', name="CollisionModel") # Remove the contactStiffness which becomes meaningless
	collisionlModel.addObject('BarycentricMapping', name="VisualMapping", input="@../StateContainer", output="@StoringForces")
	
    
	fallingParticle = rootNode.addChild("ParticleToCollideWith")
	fallingParticle.addObject("EulerImplicitSolver")
	fallingParticle.addObject("CGLinearSolver", iterations=200, tolerance=1e-09, threshold=1e-09)
	fallingParticle.addObject("MechanicalObject", template="Vec3", name="myParticle", position=[-170, 80, 0], showObject=True)
	fallingParticle.addObject("UniformMass", totalMass=0.1)
	fallingParticle.addObject("ConstantForceField", totalForce=[0,-50,0], indices=0)
	fallingParticle.addObject("SphereCollisionModel", radius=10) # Remove the contactStiffness which becomes meaningless
	fallingParticle.addObject('UncoupledConstraintCorrection', defaultCompliance=10) # 4. Define the way the Schur complement is computed
    
    
