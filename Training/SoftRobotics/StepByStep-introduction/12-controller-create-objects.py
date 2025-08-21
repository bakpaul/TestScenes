import Sofa
from math import pi, sin

uparrow = chr(19)
downarrow = chr(21)


class AddingParticles(Sofa.Core.Controller):

	def __init__(self, *args, **kwargs):
		# These are needed (and the normal way to override from a python class)
		Sofa.Core.Controller.__init__(self, *args, **kwargs)
		self.rootNode = kwargs.get("rootNode")
		self.iteration = 0

	def generateRadius(self):
		return 2.4*sin(self.iteration/5.5*pi - pi/4) + 2.5
	
	def generatXPos(self):
		return self.iteration%11 * 10  -170

	def addFallingParticle(self, node):
		iteration_loc = self.iteration
		newParticle = node.addChild("ParticleToCollideWith-"+str(iteration_loc))
		newParticle.addObject("EulerImplicitSolver")
		newParticle.addObject("CGLinearSolver", iterations=200, tolerance=1e-09, threshold=1e-09)
		newParticle.addObject("MechanicalObject", template="Rigid3", name="myParticle", position=[self.generatXPos(), 80, 0,  0,0,0,1], showObject=True)
		newParticle.addObject("UniformMass", totalMass=1)
		newParticle.addObject("ConstantForceField", totalForce=[0,-50,0,0,0,0], indices=0)
		newParticle.addObject("SphereCollisionModel", radius=self.generateRadius(), contactStiffness=100)
		newParticle.init()
		self.iteration = iteration_loc +1
    
	def removeFallingParticle(self, node):
		iteration_loc = self.iteration - 1
		if iteration_loc >= 0:
			name = 'ParticleToCollideWith-'+str(iteration_loc)
			nodeToDelete = self.rootNode.getChild(str(name))
			for obj in nodeToDelete.objects:
				nodeToDelete.removeObject(obj)

			myParticleNode = self.rootNode.removeChild(str(name))
			self.iteration = iteration_loc
    
	def onKeypressedEvent(self, event):
		key = event['key']

		if key==uparrow :
			self.addFallingParticle(self.rootNode)
        
		if key==downarrow :
			self.removeFallingParticle(self.rootNode)


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
	collisionlModel.addObject('TriangleCollisionModel', name="CollisionModel", contactStiffness=2) # Triangular primitives used at the narrow phase
	collisionlModel.addObject('BarycentricMapping', name="VisualMapping", input="@../StateContainer", output="@StoringForces") # Barycentric mapping connecting the two representations with different topologies

	rootNode.addObject( AddingParticles(name="AddingParticles", rootNode=rootNode) )

