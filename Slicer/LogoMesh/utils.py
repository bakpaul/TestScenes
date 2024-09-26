from svgpathtools import svg2paths
import matplotlib.pyplot as mpl
import pygmsh
import numpy as np

def norm2(l):
    return (l[0]**2+l[1]**2)**(1/2)

def dist(p1,p2):
    return norm2([p2[0]- p1[0],p2[1]- p1[1]])

def bary(p1,p2):
    return [(p2[0] + p1[0])/2,(p2[1] + p1[1])/2]


def filterPath(path,minDist,maxDist,iter=1):
    FilteredPts = path
    ## filter mesh
    for k in range(iter):
        id = k%2
        tempPts = FilteredPts
        if(id == 1):
            FilteredPts = [tempPts[0]]
        else:
            FilteredPts = []
        while id<(len(tempPts)-1):
            coupleDist = dist(tempPts[id],tempPts[id+1])
            if(coupleDist<minDist):
                FilteredPts = FilteredPts + [bary(tempPts[id],tempPts[id+1])]
            elif(coupleDist>maxDist):

                FilteredPts = FilteredPts + [tempPts[id], bary(tempPts[id],tempPts[id+1]),tempPts[id+1]]
            else:
                FilteredPts = FilteredPts + [tempPts[id],tempPts[id+1]]
            id += 2

            if(id == len(tempPts)-1):
                FilteredPts = FilteredPts + [tempPts[id]]
    return FilteredPts

class edgeList():
    def __init__(self):
        self.occurences = {}
        self.ids = {}
    
    def add(self, i,j):
        mi = i
        ma = j
        if i>j:
            mi = j
            ma = i
        if( mi not in self.occurences):
            self.occurences[mi] = {}

        if( ma not in self.occurences[mi]):
            self.occurences[mi][ma] = 0

        self.occurences[mi][ma] += 1
    
    def addId(self,i,j,id):
        mi = i
        ma = j
        if i>j:
            mi = j
            ma = i
        if( mi not in self.ids):
            self.ids[mi] = {}

        if( ma not in self.ids[mi]):
            self.ids[mi][ma] = []

        self.ids[mi][ma].append(id)
        


        
        

def findBorderEdges(triangles):
    edges=edgeList()

    for triangle in triangles:
        edges.add(triangle[0],triangle[1])
        edges.add(triangle[1],triangle[2])
        edges.add(triangle[2],triangle[0])

    outputEdges=[]

    for mi in edges.occurences:
        for ma in edges.occurences[mi]:
            if edges.occurences[mi][ma]==1:
                outputEdges.append([mi,ma])


    return outputEdges

def reorientAndSortBorderEdges(edges,triangles):
    first = edges[0]
    for triangle in triangles:
        if (first[0] in triangle) and (first[1] in triangle):
            id0 = triangle.tolist().index(first[0])
            id1 = triangle.tolist().index(first[1])
            if not((id1 - id0)>0 or (id0 == 2)):
                edges[0] = [first[1],first[0]]
            else:
                #Edge is in the right direction
                None
            break

    outEdges = [edges[0]]
    it = 0
    edgeId = 0
    started = False
    while not(started) or not(edgeId==0):
        started = True
        found = False
        if it>len(edges):
            print("Error a loop has been found in the data")
            return
        for i in range(len(edges)):
            if i!= edgeId:
                if(edges[edgeId][1] in edges[i]):
                    if edges[i][0] != edges[edgeId][1]:
                        edges[i] = [edges[i][1],edges[i][0]]
                    outEdges.append(edges[i])
                    edgeId = i
                    found = True
                    break
        if not found:
            print("Error the edge list is not a closed contour")
            return
        it += 1
        
    return outEdges
        
def filterDuplicatedTriangles(triangles):
    uniqueTri = {}
    toRemoveIds = []
    id = 0
    for tri in triangles:
        sortedTri = np.sort(tri)
        if( sortedTri[0] not in uniqueTri):
            uniqueTri[sortedTri[0]] = {}
        if( sortedTri[1] not in uniqueTri[sortedTri[0]]):
            uniqueTri[sortedTri[0]][sortedTri[1]] = {}

        if( sortedTri[2] in uniqueTri[sortedTri[0]][sortedTri[1]]):
            toRemoveIds.append(id)
        else:
            uniqueTri[sortedTri[0]][sortedTri[1]][sortedTri[2]] = id
        id += 1

    return np.delete(triangles,toRemoveIds,0)
    

def getSurroundingTriangles(triangles,edges,id):

    surroundingIds=[]
    for i in range(3):
        id0 = min(triangles[id][i], triangles[id][(i+1)%3])
        id1 = max(triangles[id][i], triangles[id][(i+1)%3])
        surroundingIds.extend(edges.ids[id0][id1])

    surroundingIds = np.unique(surroundingIds)
    surroundingIds = surroundingIds[surroundingIds != id]
    return surroundingIds

def recursivReorient(triangles, edges, triangleStatus, originalTriangleId,surroundingIds,acc):

    if(triangleStatus[originalTriangleId]):
        return 
    
    acc[0] +=1

    triangleStatus[originalTriangleId] = True

    ordering = [[0,1,2],[1,2,0],[2,0,1]]
    reorder = [2,1,0]

    for id in surroundingIds:
        if((id == originalTriangleId) or triangleStatus[id]):
            continue
        for order in ordering:
            if(np.count_nonzero((triangles[originalTriangleId][order] - triangles[id])==0) >1):
                triangles[id] = triangles[id][reorder]
        newSurroundingIds=getSurroundingTriangles(triangles,edges,id)
        recursivReorient(triangles,edges,triangleStatus,id,newSurroundingIds,acc)    

    return 

def triangulateMesh(triangles,startId=0):

    triangleProcessed = np.array([0])

    edges=edgeList()

    for i in range(len(triangles)):
        edges.addId(triangles[i][0],triangles[i][1],i)
        edges.addId(triangles[i][1],triangles[i][2],i)
        edges.addId(triangles[i][2],triangles[i][0],i)

    triangleStatus = [False for i in triangles]

    recursivReorient(triangles,edges,triangleStatus,startId,getSurroundingTriangles(triangles,edges,startId),triangleProcessed)

    return triangleProcessed



def IsMeshTriangulated(mesh):
    edges = {}
    id = 0
    for tri in mesh:
        for i in range(3):
            edge = [tri[i], tri[(i+1)%3]]
            if( edge[0] not in edges):
                edges[edge[0]] = {}

            if( edge[1] in edges[edge[0]]):
                print("Triangles " + str(id) + " and " + str(edges[edge[0]][edge[1]]) + " are sharing an edge." )
                print("Here are the triangles : (" + str(id) + ") " + str(tri) + ", (" +str(edges[edge[0]][edge[1]]) + ") " + str(mesh[edges[edge[0]][edge[1]]]))
                return False
            else:
                edges[edge[0]][edge[1]] = id
        id += 1
                
    return True


def writeOBJ(filename, position,edges,triangles=[]):
    with open(filename, 'w') as file:
        for pos in position:
            file.write(f"v {pos[0]:.3f} {pos[1]:.3f} {pos[2]:.3f}\n" ) 
        
        for edge in edges:
            file.write(f"l {(edge[0]+1):d} {(edge[1]+1):d}\n" ) 
        
        for triangle  in triangles:
            file.write(f"f {(triangle[0]+1):d} {(triangle[1]+1):d} {(triangle[2]+1):d}\n" ) 