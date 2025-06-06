def createScene(rootNode):
	rootNode.name = "rootNode"	        # Name of the root node
	rootNode.dt = 0.01			        # Time step
	rootNode.gravity = [ 0., 0. ,0.]	# Gravitational acceleration applied on the entire scene

	rootNode.addObject("DefaultAnimationLoop")

	rootNode.addChild("myObject", bbox=[0,0,0,1,1,1])   # bbox is only needed here to define a non-zero simulation space since the scene is empty
