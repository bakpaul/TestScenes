from svgpathtools import svg2paths
import matplotlib.pyplot as mpl
import pygmsh
import numpy as np
import utils


# Slicer
splineNbPts = 30
minDist = 6
maxDist = 13
iter = 30
meshScale = 0.3
mesh_size = 10
width = 5
filename = 'Slicer_LOGO.svg'

#SOFA 
# splineNbPts = 3
# minDist = 6
# maxDist = 13
# iter = 30
# mesh_size = 10
# meshScale = 1
# width = 5
# filename = 'SOFA_LOGO.svg'


paths, attributes = svg2paths(filename)

mpl.figure()

Pts_x = []
Pts_y = []
Pts = []



for Geom in paths[0]:
    if('control1' in Geom.__dict__):
        nbPt = splineNbPts
    else:
        nbPt = 1

    Pts_y = Pts_y + [Geom.point(i/nbPt).real*meshScale for i in range(nbPt) ]
    Pts_x = Pts_x + [-Geom.point(i/nbPt).imag*meshScale for i in range(nbPt) ]
    Pts = Pts + [[Pts_x[-(nbPt-i)],Pts_y[-(nbPt-i)]] for i in range(nbPt)]


FilteredPts_x = []
FilteredPts_y = []
FilteredPts = utils.filterPath(Pts,minDist,maxDist,iter)





for pt in FilteredPts:
    FilteredPts_x.append(pt[0])
    FilteredPts_y.append(pt[1])


with pygmsh.geo.Geometry() as geom:
    geom.add_polygon(FilteredPts, mesh_size=mesh_size)
    # mesh = geom.generate_mesh()
    mesh = geom.generate_mesh(dim=3,order=1,algorithm=5)

meshNbPoints = len(mesh.points)

#Duplicate and move points to have two surfaces
front = np.copy(mesh.points)
front[:,2] = width
back = np.copy(mesh.points)
back[:,2] = -width
mesh.points = np.concatenate((front,back))


#Duplicate triangles to have triangles on both surfaces
frontTriangles = np.copy(mesh.cells[1].data)
backTriangles = np.copy(mesh.cells[1].data)
backTriangles += meshNbPoints

#Find border edges and construct width triangles
unsortedBoderEdges = utils.findBorderEdges(mesh.cells[1].data)
sortedBorderEdges = utils.reorientAndSortBorderEdges(unsortedBoderEdges,mesh.cells[1].data)

widthTriangles = []
for edge in sortedBorderEdges:
    firstTriangle = [edge[0], edge[1], edge[1]+ meshNbPoints]
    secondTriangle = [edge[1]+ meshNbPoints, edge[0]+ meshNbPoints,edge[0] ]
    widthTriangles.append(firstTriangle)
    widthTriangles.append(secondTriangle)


mesh.cells[1].data = np.concatenate((frontTriangles,backTriangles,np.array(widthTriangles)))



#2D mesh algorithm (
# 1: MeshAdapt, 
# 2: Automatic, 
# 3: Initial mesh only, 
# 5: Delaunay, 
# 6: Frontal-Delaunay, 
# 7: BAMG, 
# 8: Frontal-Delaunay for Quads, 
# 9: Packing of Parallelograms, 
# 11: Quasi-structured Quad)

mesh.write("test.vtk")


mpl.plot(Pts_x,Pts_y,'b-')
mpl.plot(FilteredPts_x,FilteredPts_y,'r+')
mpl.show()

