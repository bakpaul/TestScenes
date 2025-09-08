from CGAL.CGAL_Polyhedron_3 import Polyhedron_3
from CGAL.CGAL_Mesh_3 import Polyhedral_mesh_domain_3
from CGAL.CGAL_Mesh_3 import Mesh_3_parameters
from CGAL.CGAL_Mesh_3 import Default_mesh_criteria
from CGAL.CGAL_Kernel import Point_3
from CGAL.CGAL_Convex_hull_3 import convex_hull_3, is_strongly_convex_3
from CGAL import CGAL_Mesh_3

import sys
import argparse 
import os
import random
import time


from cgal_utils import CGAL_Mesh_from, CGAL_Mesh_3_IO_Util, ReadPolyData, tic, toc
from mesh_from_polyhedron import CGAL_Mesh_from_polyhedron

class CGAL_Mesh_from_pointcloud(CGAL_Mesh_from):
    def __init__(self, pointcloud ):
        print(f"Transformaing input data into CGAL data structure...")
        tic()
        self.pointcloud = []
        for point in pointcloud:
            self.pointcloud.append(Point_3(point[0],point[1],point[2]))
        print(f"Done ! Took {toc()}")


    def generate(self, criteria , refiner = CGAL_Mesh_from.Refiner_input(refiner_type=CGAL_Mesh_from.Refiner.NONE)):
        print(f"Generating convex hull...")
        tic()

        self.polyhedron = Polyhedron_3()
        convex_hull_3(self.pointcloud, self.polyhedron)



        print(f"Done ! Took {toc()}")
        print(f"Convex hull has {self.polyhedron.size_of_vertices()} vertices and is strongly convex: {is_strongly_convex_3(self.polyhedron)}")

        cmfp = CGAL_Mesh_from_polyhedron(polyhedron=self.polyhedron)
        cmfp.generate(criteria)
        self.IOUtil = cmfp.IOUtil

    def write_out(self, filename):
        self.IOUtil.write_out(filename)
        

if __name__ == "__main__":    

    parser = argparse.ArgumentParser(description="Creates a mesh from a point cloud using convex hull.")   

    parser.add_argument("nbPoints", help="Number of random point in the point cloud") 
    parser.add_argument( "-o", "--output", default='data/mesh/pointCloudMesh.vtk', help="The output file to save the computed volumetric mesh")  

    args = parser.parse_args() 

    random.seed(time.time_ns())

    PC = []
    for i in range(int(args.nbPoints)):
        PC.append([random.random() * 2, random.random() * 1, random.random() * 1])

    tic(1)
    cmfp = CGAL_Mesh_from_pointcloud(PC)
    criteria = Default_mesh_criteria()
    criteria.facet_angle(25).facet_size(0.15).facet_distance(0.008).cell_radius_edge_ratio(3)
    cmfp.generate(criteria)

    cmfp.write_out(args.output)
    print(f"The script took a total of {toc(1)}")



