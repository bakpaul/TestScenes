def createScene(rootNode):

	rootNode.name = "rootNode"
	rootNode.dt = 0.01
	rootNode.gravity = [ 0., -9.81 ,0.]

	rootNode.addObject("DefaultAnimationLoop", computeBoundingBox=False)
	
	rootNode.addObject('RequiredPlugin', pluginName=['Sofa.Component.StateContainer','Sofa.Component.Mass','Sofa.Component.MechanicalLoad',
												     'Sofa.Component.LinearSolver.Iterative','Sofa.Component.ODESolver.Backward',
													 'Sofa.Component.IO.Mesh','Sofa.Component.Topology.Container.Dynamic',
													 'Sofa.Component.SolidMechanics.FEM.Elastic','Sofa.Component.Topology.Container.Constant',
													 'Sofa.Component.Visual','Sofa.Component.Mapping.Linear','Sofa.GL.Component.Rendering3D',
													 'Sofa.Component.Constraint.Projective','Sofa.Component.Engine.Select','Sofa.Component.Collision.Geometry',
													 'Sofa.Component.Collision.Detection.Intersection','Sofa.Component.Collision.Detection.Algorithm',
													 'Sofa.Component.Collision.Response.Contact', 'Sofa.GUI.Component'])

	rootNode.addObject("MeshVTKLoader", name="meshLoaderCoarse", filename="../PneuNets_remeshed.vtk")
	rootNode.addObject('AttachBodyButtonSetting',stiffness=1)
	
	rootNode.addObject('VisualStyle', displayFlags='showForceFields showCollisionModels showBehaviorModels showDetectionOutputs')

    ##########################################
    # Collision pipeline definition : broad phase / narrow phase / response
	rootNode.addObject('CollisionPipeline')
	rootNode.addObject('BruteForceBroadPhase') # Broad phase
	rootNode.addObject('BVHNarrowPhase') # Narrow phase
	rootNode.addObject('MinProximityIntersection', name="Proximity", alarmDistance="0.5", contactDistance="0.25") #Intersection method used for the narrow phase
	rootNode.addObject('CollisionResponse', name="Response", response="PenalityContactForceField") # Reponse method when a contact is detected in the narrow phase
	##########################################
	
	mechanicalModel = rootNode.addChild("Finger")
	
	mechanicalModel.addObject("EulerImplicitSolver")
	mechanicalModel.addObject("CGLinearSolver", iterations=200, tolerance=1e-09, threshold=1e-09)
	
	mechanicalModel.addObject("MeshTopology", name="topologyContainer", src="@../meshLoaderCoarse" )

	mechanicalModel.addObject("MechanicalObject", template="Vec3", name="StateContainer", showObject=True)
	
	mechanicalModel.addObject('TetrahedronFEMForceField', template='Vec3', poissonRatio=0.3, youngModulus=100)
	mechanicalModel.addObject('MeshMatrixMass', template='Vec3,Vec3', totalMass=0.5)
	
	mechanicalModel.addObject('BoxROI', name='boxROI', box=[-10, 0, -20, 0, 30, 20], drawBoxes=True,
						      position=mechanicalModel.StateContainer.position.linkpath,
							  tetrahedra=mechanicalModel.topologyContainer.tetrahedra.linkpath)
	mechanicalModel.addObject('FixedProjectiveConstraint', indices=mechanicalModel.boxROI.indices.linkpath)

	
	visualModel = mechanicalModel.addChild("Visual")
	visualModel.addObject('MeshSTLLoader', name="loader", filename="../PneuNets_remeshed.stl")
	visualModel.addObject('OglModel', name="VisualModel", src=visualModel.loader.linkpath, color=[0.7, 0.7, 0.7, 1])
	visualModel.addObject('BarycentricMapping', name="VisualMapping", input="@../StateContainer", output="@VisualModel")
	
	##########################################
	# Collision representation of the finger object
	collisionlModel = mechanicalModel.addChild("Collision")
	collisionlModel.addObject("MeshTopology", name="topologyContainer", src=visualModel.loader.linkpath) # Use the same mesh topology than the visual model
	collisionlModel.addObject('MechanicalObject', name="StoringForces") # Mechanical object storing the DoFs corresponding to the contact points and associated forces
	collisionlModel.addObject('TriangleCollisionModel', name="CollisionModel", contactStiffness=3) # Triangular primitives used at the narrow phase
	collisionlModel.addObject('BarycentricMapping', name="VisualMapping", input="@../StateContainer", output="@StoringForces") # Barycentric mapping connecting the two representations with different topologies
	
    
    ##########################################
	# Additional object which will collide with the finger
	# fallingParticle = rootNode.addChild("ParticleToCollideWith")
	# fallingParticle.addObject("EulerImplicitSolver")
	# fallingParticle.addObject("CGLinearSolver", iterations=200, tolerance=1e-09, threshold=1e-09)
	# fallingParticle.addObject("MechanicalObject", template="Rigid3", name="myParticle", position=[-170, 80, 0,  0,0,0,1], showObject=True)
	# fallingParticle.addObject("UniformMass", totalMass=0.1)
	# fallingParticle.addObject("ConstantForceField", totalForce=[0,-50,0,0,0,0], indices=0)
	# fallingParticle.addObject("SphereCollisionModel", radius=10, contactStiffness=100)
	##########################################
    
    