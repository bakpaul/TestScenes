import numpy as np
import utils


def IsMeshTriangulated(mesh):
    edges = {}
    for tri in mesh:
        for i in range(3):
            edge = [tri[i], tri[(i+1)%3]]
            if( edge[0] not in edges):
                edges[edge[0]] = {}

            if( edge[1] in edges[edge[0]]):
                return False
            else:
                edges[edge[0]][edge[1]] = 1
                
    return True
print("---------")

print("First mesh to be tested : ")
mesh1 = [np.array([0,1,2]),np.array([2,3,4]),np.array([1,2,3])]
print(mesh1)
print("")
utils.triangulateMesh(mesh1)

print("Mesh1 after triangulation:")
print(mesh1)
print("")

if(not(IsMeshTriangulated(mesh1))):
    print("--> Mesh1 failed !")
else:
    print("--> Mesh1 succeeded !")

print("---------")
print("Second mesh to be tested : ")

mesh2 = [np.array([1,2,3]),np.array([0,1,2]),np.array([2,3,4]),np.array([0,2,4])]
print(mesh2)
print("")
utils.triangulateMesh(mesh2)

print("Mesh2 after triangulation:")
print(mesh2)
print("")

if(not(IsMeshTriangulated(mesh2))):
    print("--> Mesh2 failed !")
else:
    print("--> Mesh2 succeeded !")
print("---------")

