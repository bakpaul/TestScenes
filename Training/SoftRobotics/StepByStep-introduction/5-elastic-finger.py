def createScene(rootNode):

	rootNode.name = "rootNode"
	rootNode.dt = 0.01
	rootNode.gravity = [ 0., -9.81 ,0.] # Defining gravity along -Y

	rootNode.addObject("DefaultAnimationLoop", computeBoundingBox=False)
	
	rootNode.addObject('RequiredPlugin', pluginName=['Sofa.Component.StateContainer','Sofa.Component.Mass','Sofa.Component.MechanicalLoad',
												     'Sofa.Component.LinearSolver.Iterative','Sofa.Component.ODESolver.Backward',
													 'Sofa.Component.IO.Mesh','Sofa.Component.Topology.Container.Dynamic',
													 'Sofa.Component.SolidMechanics.FEM.Elastic','Sofa.Component.Topology.Container.Constant',
													 'Sofa.Component.Visual'])
	rootNode.addObject('VisualStyle', displayFlags='showForceFields')
	
	rootNode.addObject("MeshVTKLoader", name="meshLoaderCoarse", filename="../PneuNets.vtk") # Using a VTK file format, thus using MeshVTKLoader
	
	mechanicalModel = rootNode.addChild("Finger")
	
	mechanicalModel.addObject("EulerImplicitSolver")
	mechanicalModel.addObject("CGLinearSolver", iterations=200, tolerance=1e-09, threshold=1e-09)
	
    # MeshTopology is a static topology container, i.e. it does not support topology changes (unlike TetrahedronSetTopologyContainer)
	mechanicalModel.addObject("MeshTopology", name="topologyContainer", src="@../meshLoaderCoarse" )

	mechanicalModel.addObject("MechanicalObject", template="Vec3", name="StateContainer", showObject=True) # Define the template as Vec3 for 3D deformable bodies
	
	mechanicalModel.addObject('TetrahedronFEMForceField', template='Vec3', poissonRatio=0.3, youngModulus=100) # Define an elastic constitutive law
	mechanicalModel.addObject('DiagonalMass', template='Vec3,Vec3', totalMass=0.5) # Use a mass integrated over the volume
