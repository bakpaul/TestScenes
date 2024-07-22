import Sofa
import random
import numpy as np

s_numberOfStars = 10
s_numberOfRound = 100
s_timeBetweenRounds = 0.01

def addRountOfStars(numberOfStars, node,roundNumber):
    starPos = [np.array([random.uniform(a=-3,b=3) for i in range(numberOfStars)]), np.array([random.uniform(a=-3,b=3) for i in range(numberOfStars)]), np.array([random.uniform(a=-3,b=3) for i in range(numberOfStars)]) * 0.2]


    for i in range(numberOfStars):
        star_n = node.addChild('Star' + str(roundNumber* s_numberOfStars + i),sleeping=True)

        star_n.addObject("MechanicalObject",name="mstate", template="Rigid3", position=[starPos[0][i],starPos[1][i],starPos[2][i],0,0,0,1],
                         showObject=True,showObjectScale=0.05)
        star_n.addObject("UniformMass",name="mass",totalMass="0.1")
        star_n_col = star_n.addChild('Collision')
        star_n_col.addObject("MechanicalObject",name="mstate", template="Vec3", position=[starPos[0][i],starPos[1][i],starPos[2][i]])
        star_n_col.addObject("SphereCollisionModel",name="SphereCollision",proximity=0.01,radius=0.01,contactStiffness=100,contactRestitution=1.0)
        star_n_col.addObject("RigidMapping",isMechanical=True,globalToLocalCoords=True)

        # star_n.init()
        # star_n_col.init()


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
                star.getData("sleeping").value = False
                # star.getChild("Collision").getObject('SphereCollision').getData('listening').value=True
            self.numberOfRound += 1
            self.last = self.root.getTime()
        pass




def createScene(node):
    node.gravity=[0,0,-9.81]
    node.dt = 0.01
    node.addObject('VisualStyle', displayFlags="showVisualModels showCollisionModels")
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
    node.addObject('CollisionPipeline', name="collisionPipeline")
    node.addObject('ParallelBruteForceBroadPhase', name="broadPhase")
    node.addObject('ParallelBVHNarrowPhase',  name="narrowPhase")

    node.addObject('CollisionResponse',name="ContactManager", response="PenalityContactForceField")
    node.addObject('MinProximityIntersection' ,name="Distance",alarmDistance=0.1,contactDistance=0.005)

    stars = node.addChild("Stars")
    stars.addObject("EulerImplicitSolver",name="ODESolver",rayleighStiffness="0.1", rayleighMass="0.1")
    stars.addObject('CGLinearSolver', iterations=25, tolerance=1e-5, threshold=1e-5)

    for i in range(s_numberOfRound):
        addRountOfStars(s_numberOfStars, stars,i)
    node.addObject(EmptyController(stars))

    Floor = node.addChild("Floor")
    Floor.addObject("TriangleSetTopologyContainer",name="container",position = "-5 -5 -3  5 -5 -3  5 5 -3  -5 5 -3",triangles="0 2 1  0 3 2")
    Floor.addObject("MechanicalObject",name="mstate", template="Vec3")
    Floor.addObject("TriangleCollisionModel",name="TriangleCollision",proximity="0.03", bothSide=False, moving="0", simulated="0",contactStiffness=10,contactRestitution=1.0 )
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
