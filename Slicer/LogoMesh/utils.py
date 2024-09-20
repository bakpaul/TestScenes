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
        self.data = {}
    
    def add(self, i,j):
        mi = i
        ma = j
        if i>j:
            mi = j
            ma = i
        if( mi not in self.data):
            self.data[mi] = {}

        if( ma not in self.data[mi]):
            self.data[mi][ma] = 0

        self.data[mi][ma] += 1

        
        

def findBorderEdges(triangles):
    edges=edgeList()

    for triangle in triangles:
        edges.add(triangle[0],triangle[1])
        edges.add(triangle[1],triangle[2])
        edges.add(triangle[2],triangle[0])

    outputEdges=[]

    for mi in edges.data:
        for ma in edges.data[mi]:
            if edges.data[mi][ma]==1:
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
        


