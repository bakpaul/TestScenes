import os


def createScene(rootNode):
    rootNode.addObject('RequiredPlugin', pluginName=['SoftRobots', 'SoftRobots.Inverse'])
    rootNode.addObject('VisualStyle',
                       displayFlags='showVisualModels showBehaviorModels showCollisionModels '
                                    'hideBoundingCollisionModels hideForceFields '
                                    'showInteractionForceFields hideWireframe')
    rootNode.addObject('AttachBodyButtonSetting',stiffness=1)

    rootNode.addObject('FreeMotionAnimationLoop')
    rootNode.addObject('QPInverseProblemSolver')                                     ##--> Replace the generic constraint solver y the QP solver
    ##########################################
    # Goal                                   #
    ##########################################
    goal = rootNode.addChild('goal')                                                 ##--> Define a target position (goal) to reach wih the EEF
    goal.addObject('EulerImplicitSolver', firstOrder=True)
    goal.addObject('CGLinearSolver', iterations=100, tolerance=1e-5, threshold=1e-5)
    goal.addObject('MechanicalObject', name='goalMO', position=[[-230, 15, 0]])      ##--> Define a starting position
    goal.addObject('SphereCollisionModel', radius=5, group=3)
    goal.addObject('UncoupledConstraintCorrection')                                  ##--> Required to move it with the mouse

    ##########################################
    # FEM Model                              #
    ##########################################
    model = rootNode.addChild('model')
    model.addObject('EulerImplicitSolver', rayleighStiffness=0.2, rayleighMass=0.2)
    model.addObject('SparseLDLSolver')

    model.addObject('MeshVTKLoader', name='loader', filename='PneuNets_remeshed.vtk')
    model.addObject('MeshTopology', src='@loader', name='container')

    model.addObject('MechanicalObject')
    model.addObject('UniformMass', totalMass=0.5)
    model.addObject('TetrahedronFEMForceField', template='Vec3', poissonRatio=0.3,
                    youngModulus=100)

    model.addObject('BoxROI', name='boxROI', box=[-10, 0, -20, 0, 30, 20], drawBoxes=True,
                    position=model.MechanicalObject.position.linkpath,
                    tetrahedra=model.container.tetrahedra.linkpath)
    model.addObject('RestShapeSpringsForceField', points=model.boxROI.indices.linkpath, stiffness=1e12)
    model.addObject('LinearSolverConstraintCorrection')



    ##########################################
    # Effector                               #
    ##########################################
    effector = model.addChild('effector')                                            ##--> Add an effector which position is to be controlled
    effector.addObject('MechanicalObject', position=[-195, 15, 0])                   ##--> Define its rest position on the mesh
    effector.addObject('PositionEffector', template='Vec3', indices=[0], effectorGoal=goal.goalMO.position.linkpath,
                       useDirections=[1, 1, 0])                                      ##--> Add an 'effector' object and define the direction we want to solve
    effector.addObject('BarycentricMapping')                                         ##--> Map it to the actual object

    ##########################################
    # Pressure Actuator                      #
    ##########################################
    cavity = model.addChild('cavity')
    cavity.addObject('MeshSTLLoader', name='loader', filename='PneuNets_Cavity.stl')
    cavity.addObject('MeshTopology', src=cavity.loader.linkpath, name='topo')
    cavity.addObject('MechanicalObject', name='cavity')
    cavity.addObject('SurfacePressureConstraint', name='SPC',template='Vec3', triangles=cavity.topo.triangles.linkpath,
                     maxVolumeGrowthVariation=500, minPressure=0)
    cavity.addObject('BarycentricMapping')


    ##########################################
    # Cable Actuator                         #
    ##########################################
    cable = model.addChild('cable')
    cable.addObject('MechanicalObject', name="points", position=[-32,2,0,-45,2,0,-58,2,0,-71,2,0,-84,2,0,-97,2,0,-110,2,0,-123,2,0,-136,2,0,-149,2,0,-162,2,0,-175,2,0])
    cable.addObject('CableConstraint', name='CA', template='Vec3', indices=[0,1,2,3,4,5,6,7,8,9,10,11], pullPoint=[0,2,0],
                    maxPositiveDisp=40, minForce=0)
    cable.addObject('BarycentricMapping')


    ##########################################
    # Visualization                          #
    ##########################################
    modelVisu = model.addChild('visu')
    modelVisu.addObject('MeshSTLLoader', filename="PneuNets.stl", name="loader")
    modelVisu.addObject('OglModel', src=modelVisu.loader.linkpath, color=[0.7, 0.7, 0.7, 0.6])
    modelVisu.addObject('BarycentricMapping')

    return rootNode
