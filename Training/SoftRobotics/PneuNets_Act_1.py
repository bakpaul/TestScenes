import os


def createScene(rootNode):
    rootNode.addObject('RequiredPlugin', pluginName=['SoftRobots', 'SoftRobots.Inverse'])
    rootNode.addObject('VisualStyle',
                       displayFlags='showVisualModels showBehaviorModels showCollisionModels '
                                    'hideBoundingCollisionModels hideForceFields '
                                    'showInteractionForceFields hideWireframe')
    rootNode.addObject('AttachBodyButtonSetting',stiffness=1)

    rootNode.addObject('FreeMotionAnimationLoop')
    rootNode.addObject('GenericConstraintSolver')


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
    # Pressure Actuator                      #
    ##########################################
    cavity = model.addChild('cavity')
    cavity.addObject('MeshSTLLoader', name='loader', filename='PneuNets_Cavity.stl') ##--> Load the surface mesh on which the pressure will be applied
    cavity.addObject('MeshTopology', src=cavity.loader.linkpath, name='topo')
    cavity.addObject('MechanicalObject', name='cavity')
    cavity.addObject('SurfacePressureConstraint', name='SPC',template='Vec3', triangles=cavity.topo.triangles.linkpath,
                     maxVolumeGrowthVariation=500, minPressure=0)                    ##--> This is the pressure constraint
    cavity.addObject('BarycentricMapping')                                           ##--> Mapped on the real object


    ##########################################
    # Cable Actuator                         #
    ##########################################
    cable = model.addChild('cable')
    cable.addObject('MechanicalObject', name="points",
                    position=[-32,2,0,-45,2,0,-58,2,0,-71,2,0,-84,2,0,-97,2,0,-110,2,0,-123,2,0,-136,2,0,-149,2,0,-162,2,0,-175,2,0]) ##--> Define the actuated points rest position
    cable.addObject('CableConstraint', name='CA', template='Vec3', indices=[0,1,2,3,4,5,6,7,8,9,10,11], pullPoint=[0,2,0],
                    maxPositiveDisp=40, minForce=0)                                  ##--> This is the actual cable actuator
    cable.addObject('BarycentricMapping')                                            ##--> Mapped on the real object


    ##########################################
    # Visualization                          #
    ##########################################
    modelVisu = model.addChild('visu')
    modelVisu.addObject('MeshSTLLoader', filename="PneuNets.stl", name="loader")
    modelVisu.addObject('OglModel', src=modelVisu.loader.linkpath, color=[0.7, 0.7, 0.7, 0.6])
    modelVisu.addObject('BarycentricMapping')

    return rootNode
