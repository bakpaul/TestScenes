from CGAL.CGAL_Polyhedron_3 import Polyhedron_3, Polyhedron_modifier
from CGAL.CGAL_Mesh_3 import Mesh_3_Complex_3_in_triangulation_3
from CGAL.CGAL_Mesh_3 import Polyhedral_mesh_domain_3
from CGAL.CGAL_Mesh_3 import Mesh_3_parameters
from CGAL.CGAL_Mesh_3 import Default_mesh_criteria
from CGAL.CGAL_Kernel import Point_3
from CGAL import CGAL_Mesh_3

import sys
import argparse 
import os


from cgal_utils import CGAL_Mesh_from, CGAL_Mesh_3_IO_Util, ReadPolyData, tic, toc

class CGAL_Mesh_from_polyhedron(CGAL_Mesh_from):
    def __init__(self, filename = None, polyhedron = None):
        if(filename is None and polyhedron is None):
            raise ValueError("Need either a filename to load or a CGAl polyhedron already build")
        if(filename is not None):
            print(f"Loading polyhedron from {filename}...")
            tic()
            
            mesh = ReadPolyData(filename)
            self.polyhedron = Polyhedron_3()
            pm =  Polyhedron_modifier()

            pm.begin_surface(3,1)
            for i in range(mesh.GetNumberOfPoints()):
                pt = mesh.GetPoint(i)
                pm.add_vertex(Point_3(pt[0],pt[1],pt[2]))


            for i in range(mesh.GetNumberOfCells()):
                pm.begin_facet()
                for j in range(mesh.GetCell(i).GetNumberOfPoints()):
                    pm.add_vertex_to_facet(int(mesh.GetCell(i).GetPointId(j)))
                pm.end_facet()


            self.polyhedron.delegate(pm) 
            print(f"Done ! Took {toc()}")
        else:
            self.polyhedron = polyhedron
        
        print(f"Polyhedron info from input (vertices, facets, edges) = {(self.polyhedron.size_of_vertices(), self.polyhedron.size_of_facets(), self.polyhedron.size_of_halfedges()/2)}")


    def generate(self, criteria , refiner = CGAL_Mesh_from.Refiner_input(refiner_type=CGAL_Mesh_from.Refiner.NONE)):
        print(f"Generating mesh...")
        tic()

        # Create domain
        domain = Polyhedral_mesh_domain_3(self.polyhedron)
        params = Mesh_3_parameters()
        params.no_exude()
        params.no_perturb()
        match refiner.refiner_type:
            case CGAL_Mesh_from.Refiner.LLOYD:
                params.set_lloyd(refiner.time_limit, refiner.max_iteration_number, refiner.convergence, refiner.free_bound)
            case CGAL_Mesh_from.Refiner.ODT:
                params.set_odt(refiner.time_limit, refiner.max_iteration_number, refiner.convergence, refiner.free_bound)
            case CGAL_Mesh_from.Refiner.PERTURB:
                params.set_perturb(refiner.time_limit, refiner.silver_bound)


        # Mesh generation
        c3t3 = CGAL_Mesh_3.make_mesh_3(domain, criteria, params)
        print(f"Done ! Took {toc()}")

        self.IOUtil = CGAL_Mesh_3_IO_Util(c3t3)
        self.IOUtil.extract([CGAL_Mesh_3_IO_Util.Elem.POINTS, CGAL_Mesh_3_IO_Util.Elem.TETRA])

    def write_out(self, filename):
        self.IOUtil.write_out(filename)
        

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Creates a mesh from an input file containing a polyhedron representing the surface.")   

    parser.add_argument("-i", "--input", help="The input file containing the surface. Format must be taken form ['.g', '.obj', '.stl', '.ply', '.vtk', '.vtp']") 
    parser.add_argument( "-o", "--output", help="The output file to save the computed volumetric mesh")  
    args = parser.parse_args() 

    if args.input is None:
        filename = 'data/mesh/torus.obj'
    else:
        filename = args.input

    if args.output is None:
        outFilename = 'data/mesh/torusVol.vtk'
    else:
        outFilename = args.output
    
    tic(1)
    cmfp = CGAL_Mesh_from_polyhedron(filename=filename)
    criteria = Default_mesh_criteria()
    criteria.facet_angle(25).facet_size(0.15).facet_distance(0.008).cell_radius_edge_ratio(3)
    cmfp.generate(criteria)

    cmfp.write_out(outFilename)
    print(f"The script took a total of {toc(1)}")



