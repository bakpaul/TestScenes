def createScene(rootNode):

	rootNode.name = "rootNode"
	rootNode.dt = 0.01
	rootNode.gravity = [ 0., 0. ,0.]

	rootNode.addObject("DefaultAnimationLoop", computeBoundingBox=False)
	
	rootNode.addObject('RequiredPlugin', pluginName=['Sofa.Component.StateContainer','Sofa.Component.Mass','Sofa.Component.MechanicalLoad',
												     'Sofa.Component.LinearSolver.Iterative','Sofa.Component.ODESolver.Backward',
													 'Sofa.Component.IO.Mesh','Sofa.Component.Topology.Container.Dynamic'])
	
	# Mesh loader taking a file as input (relative or absolute path)
	rootNode.addObject("MeshGmshLoader", name="meshLoaderCoarse", filename="mesh/liver.msh")

	particleNode = rootNode.addChild("Particle") # bbox is no longer needed since we do load a volumetric mesh
	
	particleNode.addObject("EulerImplicitSolver")
	particleNode.addObject("CGLinearSolver", iterations=200, tolerance=1e-09, threshold=1e-09)
	
    # Topology container (SetTopologyContainer depicts dynamic topology containers)
	# Automatically filled by the MeshLoader using the source link "src=@"
	particleNode.addObject("PointSetTopologyContainer", name="topologyContainer", src="@../meshLoaderCoarse" )

	particleNode.addObject("MechanicalObject", template="Rigid3", name="myParticle", showObject=True) # No need to manually define the "position" data field
	
	particleNode.addObject("UniformMass", totalMass=1)
	particleNode.addObject("ConstantForceField", totalForce=[[1,0,0,0,0,0]]) # Remove indices to apply to all degrees of freedom
