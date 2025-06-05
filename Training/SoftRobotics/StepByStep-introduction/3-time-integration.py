def createScene(rootNode):

	rootNode.name = "rootNode"
	rootNode.dt = 0.01
	rootNode.gravity = [ 0., 0. ,0.]

	rootNode.addObject("DefaultAnimationLoop", computeBoundingBox=False) # Deactivating computeBoundingBox prevents to recompute the rendering boundingBox since particle moves to infinity
	
	rootNode.addObject('RequiredPlugin', pluginName=['Sofa.Component.StateContainer','Sofa.Component.Mass','Sofa.Component.MechanicalLoad',
												     'Sofa.Component.LinearSolver.Iterative','Sofa.Component.ODESolver.Backward'])

	particleNode = rootNode.addChild("Particle", bbox=[0,0,0,1,1,1])   # bbox is only needed here to define a non-zero simulation space since the scene is a single rigid frame
	
    # Adding an integration scheme (ODE solver): here the backward Euler
	particleNode.addObject("EulerImplicitSolver")
	# Adding a linear solver to solve the numerical system: here the iterative Conjugate Gradient solver
	particleNode.addObject("CGLinearSolver", iterations=200, tolerance=1e-09, threshold=1e-09)
	
	particleNode.addObject("MechanicalObject", template="Rigid3", name="myParticle", position=[0,0,0,  0,0,0,1], showObject=True)
	
	particleNode.addObject("UniformMass", totalMass=1)
	particleNode.addObject("ConstantForceField", totalForce=[1,0,0,0,0,0], indices=0)
