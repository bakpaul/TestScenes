def createScene(rootNode):

    rootNode.name = "rootNode"
    rootNode.dt = 0.01
    rootNode.gravity = [ 0., -9.81 ,0.]

    rootNode.addObject('RequiredPlugin', pluginName=['Sofa.Component.StateContainer','Sofa.Component.Mass','Sofa.Component.MechanicalLoad',
												     'Sofa.Component.LinearSolver.Iterative','Sofa.Component.ODESolver.Backward',
													 'Sofa.Component.IO.Mesh','Sofa.Component.Topology.Container.Dynamic',
													 'Sofa.Component.SolidMechanics.FEM.Elastic','Sofa.Component.Topology.Container.Constant',
													 'Sofa.Component.Visual','Sofa.Component.Mapping.Linear','Sofa.GL.Component.Rendering3D',
													 'Sofa.Component.Constraint.Projective','Sofa.Component.Engine.Select',
                                                     'Sofa.Component.Constraint.Lagrangian.Correction','Sofa.Component.Constraint.Lagrangian.Model',
                                                     'Sofa.Component.Constraint.Lagrangian.Solver','Sofa.Component.LinearSolver.Direct',
                                                     'Sofa.Component.AnimationLoop'])
    
    rootNode.addObject('VisualStyle',
                       displayFlags='showVisualModels showBehaviorModels showCollisionModels '
                                    'hideBoundingCollisionModels hideForceFields '
                                    'showInteractionForceFields hideWireframe')

    rootNode.addObject('FreeMotionAnimationLoop')                                    ##--> Required for Lagrangian constraints
    rootNode.addObject('GenericConstraintSolver', maxIterations=1000, tolerance=0.001) ##--> Solver that will compute the Lagrangian multiplier value

    rootNode.addObject('AttachBodyButtonSetting', stiffness=1)                       ##--> Define the stiffness of the spring used for Mouse interactions

    ##########################################
    # FEM Model                              #
    ##########################################
    model = rootNode.addChild('model')
    model.addObject('EulerImplicitSolver', rayleighStiffness=0.2, rayleighMass=0.2)  ##--> Our integration scheme
    model.addObject('SparseLDLSolver', template="CompressedRowSparseMatrixd")        ##--> Linear solver used to inverse A (LDL factorization)

    model.addObject('MeshVTKLoader', name='loader', filename='../PneuNets.vtk')      ##--> Load our topology
    model.addObject('MeshTopology', src='@loader', name='container')

    model.addObject('MechanicalObject')                                              ##--> Contain all problem vectors
    model.addObject('UniformMass', totalMass=0.5)                                    ##--> Define the mass
    model.addObject('TetrahedronFEMForceField', template='Vec3', poissonRatio=0.3, youngModulus=100) ##--> Define the constitutive law

    model.addObject('BoxROI', name='boxROI', box=[-10, 0, -20, 0, 30, 20], drawBoxes=True,
                    position=model.MechanicalObject.position.linkpath,
                    tetrahedra=model.container.tetrahedra.linkpath)                  ##--> Define a region of interest. Here it select the fixed points 
    model.addObject('FixedLagrangianConstraint', indices=model.boxROI.indices.linkpath) ##--> Add springs to atttach those fixed points
    model.addObject('LinearSolverConstraintCorrection')                              ##--> Define the way the Schur complement is computed


    ##########################################
    # Visualization                          #
    ##########################################
    modelVisu = model.addChild('visu')
    modelVisu.addObject('MeshSTLLoader', filename="../PneuNets.stl", name="loader")     ##--> Add visualization
    modelVisu.addObject('OglModel', src=modelVisu.loader.linkpath, color=[0.7, 0.7, 0.7, 0.6])
    modelVisu.addObject('BarycentricMapping')

    return rootNode
