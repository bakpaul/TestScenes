#Required import for python
import Sofa
import SofaRuntime
from Sofa import SofaLinearSolver
import numpy as np
import scipy


# Function called when the scene graph is being created
def createScene(root):

    root.gravity=[0,0,0]

    root.addObject('VisualStyle', displayFlags="showBehaviorModels showForceFields")

    root.addObject("RequiredPlugin", pluginName=['Sofa.Component.Mass',
                                                 'Sofa.Component.StateContainer',
                                                 'Sofa.Component.Topology.Container.Grid',
                                                 'Sofa.Component.Visual'
                                                 ])
    root.addObject('RequiredPlugin', name='Sofa.Component.ODESolver.Backward')
    root.addObject('RequiredPlugin', name='Sofa.Component.LinearSolver.Direct')
    root.addObject('RequiredPlugin', name='Sofa.Component.Engine.Select')
    root.addObject('RequiredPlugin', name='Sofa.Component.Constraint.Projective')
    root.addObject('RequiredPlugin', name='Sofa.Component.SolidMechanics.FEM.Elastic')

    root.addObject('DefaultAnimationLoop')
    root.addObject('DefaultVisualManagerLoop')


    sofaLogo = root.addChild("SofaLogo")
    sofaLogo.addObject('MeshObjLoader',name="loader",filename="sofa_logo.obj")
    sofaLogo.addObject('MeshTopology',src="@loader")
    sofaLogo.addObject("EulerImplicitSolver")
    sofaLogo.addObject("SparseLDLSolver")
    sofaLogo.addObject("MechanicalObject", template="Vec2d", src="@loader")
    sofaLogo.addObject("UniformMass", vertexMass="1 1 0.83333")
