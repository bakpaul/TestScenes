
import Sofa

class ControlConstantForce(Sofa.Core.Controller):

    def __init__(self, *args, **kwargs):
        # These are needed (and the normal way to override from a python class)
        Sofa.Core.Controller.__init__(self, *args, **kwargs)
        self.CFF = kwargs.get("ForceField")

    def onKeypressedEvent(self, event):
        key = event['key']

        if key=="+" :
            with self.CFF.totalForce.writeableArray() as wa:
                wa[1] += 4.

        if key=="-" :
            with self.CFF.totalForce.writeableArray() as wa:
                wa[1] -= 4.


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
													 'Sofa.Component.Constraint.Projective','Sofa.Component.Engine.Select', 'Sofa.GUI.Component'])

	rootNode.addObject("MeshVTKLoader", name="meshLoaderCoarse", filename="../PneuNet_remeshed.vtk")
	rootNode.addObject('AttachBodyButtonSetting',stiffness=1) # Define the stiffness of the spring used with the mouse (using CTRL)
	
	mechanicalModel = rootNode.addChild("Finger")
	mechanicalModel.addObject('VisualStyle', displayFlags='showForceFields showBehaviorModels') # See bounding box too with showBehaviorModels
	
	mechanicalModel.addObject("EulerImplicitSolver")
	mechanicalModel.addObject("CGLinearSolver", iterations=200, tolerance=1e-09, threshold=1e-09)
	
	mechanicalModel.addObject("MeshTopology", name="topologyContainer", src="@../meshLoaderCoarse" )

	mechanicalModel.addObject("MechanicalObject", template="Vec3", name="StateContainer", showObject=True)
	
	mechanicalModel.addObject('TetrahedronFEMForceField', template='Vec3', poissonRatio=0.3, youngModulus=100)
	mechanicalModel.addObject('MeshMatrixMass', template='Vec3,Vec3', totalMass=0.5)
	
	mechanicalModel.addObject('BoxROI', name='boxROI', box=[-10, 0, -20, 0, 30, 20], drawBoxes=True, # Selecting indices within the box [min_x,min_y,min_z,max_x,max_y,max_z]
						      position=mechanicalModel.StateContainer.position.linkpath,
							  tetrahedra=mechanicalModel.topologyContainer.tetrahedra.linkpath)
	mechanicalModel.addObject('FixedProjectiveConstraint', indices=mechanicalModel.boxROI.indices.linkpath) # Project constraint enforcing fixed DoFs

	mechanicalModel.addObject('SphereROI', name='selectNodesPulledDown', centers=[[-200, 15, 0]], radii=[5], drawROI=False, drawPoints=True, drawSize=10)
	CFF = mechanicalModel.addObject('ConstantForceField', totalForce=[0, 0, 0], indices=mechanicalModel.selectNodesPulledDown.indices.linkpath, showArrowSize=5) # Project constraint enforcing fixed DoFs
	
	visualModel = mechanicalModel.addChild("Visual")
	visualModel.addObject('MeshSTLLoader', name="loader", filename="../PneuNet_remeshed.stl")
	visualModel.addObject('OglModel', name="VisualModel", src=visualModel.loader.linkpath, color=[0.7, 0.7, 0.7, 0.6])
	visualModel.addObject('BarycentricMapping', name="VisualMapping", input="@../StateContainer", output="@VisualModel")
	
	mechanicalModel.addObject( ControlConstantForce(name="ControlConstantForce", ForceField=CFF) )
