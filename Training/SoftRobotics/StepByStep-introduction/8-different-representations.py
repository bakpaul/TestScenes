def createScene(rootNode):

	rootNode.name = "rootNode"
	rootNode.dt = 0.01
	rootNode.gravity = [ 0., -9.81 ,0.]

	rootNode.addObject("DefaultAnimationLoop", computeBoundingBox=False)
	
	rootNode.addObject('RequiredPlugin', pluginName=['Sofa.Component.StateContainer','Sofa.Component.Mass','Sofa.Component.MechanicalLoad',
												     'Sofa.Component.LinearSolver.Iterative','Sofa.Component.ODESolver.Backward',
													 'Sofa.Component.IO.Mesh','Sofa.Component.Topology.Container.Dynamic',
													 'Sofa.Component.SolidMechanics.FEM.Elastic','Sofa.Component.Topology.Container.Constant',
													 'Sofa.Component.Visual','Sofa.Component.Mapping.Linear','Sofa.GL.Component.Rendering3D'])
	
	rootNode.addObject("MeshVTKLoader", name="meshLoaderCoarse", filename="../PneuNets.vtk")
	
	mechanicalModel = rootNode.addChild("Finger")
	mechanicalModel.addObject('VisualStyle', displayFlags='showForceFields showWireframe')
	
	mechanicalModel.addObject("EulerImplicitSolver")
	mechanicalModel.addObject("CGLinearSolver", iterations=200, tolerance=1e-09, threshold=1e-09)
	
	mechanicalModel.addObject("MeshTopology", name="topologyContainer", src="@../meshLoaderCoarse" )

	mechanicalModel.addObject("MechanicalObject", template="Vec3", name="StateContainer", showObject=True)
	
	mechanicalModel.addObject('TetrahedronFEMForceField', template='Vec3', poissonRatio=0.3, youngModulus=100)
	mechanicalModel.addObject('DiagonalMass', template='Vec3,Vec3', totalMass=0.5)
	
    # Adding a rendering model using the same mesh as for the mechanics
    # in a dedicated node connected to the mechanical model using a Mapping
	visualModel = mechanicalModel.addChild("Visual")
	visualModel.addObject('MeshSTLLoader', name="loader", filename="../PneuNets.stl") # Loading a mesh containing ONLY the surface triangles
	visualModel.addObject('OglModel', name="VisualModel", src=visualModel.loader.linkpath, color=[0.7, 0.7, 0.7, 0.6]) # Note the different way to write the link "src"
	visualModel.addObject('BarycentricMapping', name="VisualMapping", input="@../StateContainer", output="@VisualModel") # Barycentric mapping connecting the two representations with different topologies
