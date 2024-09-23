import Sofa
import random
import numpy as np

s_numberOfStars = 10
s_numberOfRound = 100
s_timeBetweenRounds = 0.01

def addRountOfStars(numberOfStars, node,roundNumber):
    starPos = [np.array([random.uniform(a=-3,b=3) for i in range(numberOfStars)]), np.array([random.uniform(a=-3,b=3) for i in range(numberOfStars)]), np.array([random.uniform(a=-3,b=3) for i in range(numberOfStars)]) * 0.2]


    for i in range(numberOfStars):
        star_n = node.addChild('Star' + str(roundNumber* s_numberOfStars + i))

        star_n.addObject("MechanicalObject",name="mstate", template="Rigid3", position=[starPos[0][i],starPos[1][i],starPos[2][i],0,0,0,1],
                         showObject=True,showObjectScale=0.05)
        star_n.addObject("UniformMass",name="mass",totalMass="0.1")
        star_n.addObject("PlaneForceField",name="plane", template="Rigid3", normal="0 0 1", d=-3, stiffness=5000, damping=0, showPlane=True)


class EmptyController(Sofa.Core.Controller):

    def __init__(self, root):
        Sofa.Core.Controller.__init__(self)
        self.root = root
        self.last = 0
        self.numberOfRound = 0

    def onAnimateBeginEvent(self, event):
        if (self.numberOfRound<s_numberOfRound) and ((self.root.getTime() - self.last)>s_timeBetweenRounds):
            for i in range(s_numberOfStars):
                star = self.root.getChild('Star' + str(self.numberOfRound* s_numberOfStars + i))
            self.numberOfRound += 1
            self.last = self.root.getTime()
        pass




def createScene(node):
    node.gravity=[0,0,-9.81]
    node.dt = 0.01
    node.addObject('VisualStyle', displayFlags="showVisualModels showCollisionModels showForceFields")
    node.addObject('BackgroundSetting', color=[0.8,0.8,0.8])

    node.addObject("RequiredPlugin", name="requiredPlugins", pluginName=['Sofa.Component.Constraint.Projective',
                                                                         'Sofa.Component.Engine.Select',
                                                                         'Sofa.Component.LinearSolver.Direct',
                                                                         'Sofa.Component.Mass',
                                                                         'Sofa.Component.ODESolver.Backward',
                                                                         'Sofa.Component.SolidMechanics.FEM.Elastic',
                                                                         'Sofa.Component.StateContainer',
                                                                         'Sofa.Component.Topology.Container.Grid',
                                                                         'Sofa.Component.IO.Mesh',
                                                                         'Sofa.Component.LinearSolver.Direct',
                                                                         'Sofa.Component.ODESolver.Forward',
                                                                         'Sofa.Component.Topology.Container.Dynamic',
                                                                         'Sofa.Component.Visual',
                                                                         ])

    node.addObject('DefaultAnimationLoop',name="animation",computeBoundingBox=False)

    stars = node.addChild("Stars")
    stars.addObject("EulerImplicitSolver",name="ODESolver")
    stars.addObject('CGLinearSolver', iterations=25, tolerance=1e-5, threshold=1e-5)

    for i in range(s_numberOfRound):
        addRountOfStars(s_numberOfStars, stars,i)
    node.addObject(EmptyController(stars))

    Floor = node.addChild("Floor")
    Floor.addObject("TriangleSetTopologyContainer",name="container",position = "-5 -5 -3  5 -5 -3  5 5 -3  -5 5 -3",triangles="0 2 1  0 3 2")
    Floor.addObject("MechanicalObject",name="mstate", template="Vec3")
    Floor.addObject("OglModel", name="VisualModel", src="@container")


    return node


def main():
    import SofaRuntime
    import Sofa.Gui

    root=Sofa.Core.Node("root")
    createScene(root)

    Sofa.Gui.GUIManager.Init("myscene", "qglviewer")
    Sofa.Gui.GUIManager.createGUI(root, __file__)
    Sofa.Gui.GUIManager.SetDimension(1080, 1080)
    Sofa.Gui.GUIManager.MainLoop(root)
    Sofa.Gui.GUIManager.closeGUI()

    print("End of simulation.")


if __name__ == '__main__':
    main()
