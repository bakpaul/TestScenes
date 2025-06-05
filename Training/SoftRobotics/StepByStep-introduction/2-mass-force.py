def createScene(rootNode):

	rootNode.name = "rootNode"
	rootNode.dt = 0.01
	rootNode.gravity = [ 0., 0. ,0.]

	rootNode.addObject("DefaultAnimationLoop")
	
	rootNode.addObject('RequiredPlugin', pluginName=['Sofa.Component.StateContainer','Sofa.Component.StateContainer',
												     'Sofa.Component.Mass','Sofa.Component.MechanicalLoad'])

	particleNode = rootNode.addChild("Particle", bbox=[0,0,0,1,1,1])   # bbox is only needed here to define a non-zero simulation space since the scene is a single rigid frame
	particleNode.addObject("MechanicalObject", template="Rigid3", name="myParticle", position=[0,0,0,  0,0,0,1], showObject=True)
	
    # Defining the particle mass
	particleNode.addObject("UniformMass", totalMass=1)
	# Defining an external nodal force
	particleNode.addObject("ConstantForceField", totalForce=[1,0,0,0,0,0], indices=0)
