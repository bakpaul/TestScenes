def createScene(rootNode):

	rootNode.name = "rootNode"	        # Name of the root node
	rootNode.dt = 0.01			        # Time step
	rootNode.gravity = [ 0., 0. ,0.]	# Gravitational acceleration applied on the entire scene

	rootNode.addObject("DefaultAnimationLoop")

    # MechanicalObject being a component defined in the library Sofa.Component.StateContainer, the library has to be loaded
	#rootNode.addObject('RequiredPlugin', pluginName=['Sofa.Component.StateContainer'])

	particleNode = rootNode.addChild("Particle", bbox=[0,0,0,1,1,1])   # bbox is only needed here to define a non-zero simulation space since the scene is a single rigid frame
	particleNode.addObject("MechanicalObject", template="Rigid3", name="myParticle", position=[0,0,0,  0,0,0,1], showObject=True) # Define the template as Rigid3 for 3D rigid bodies
