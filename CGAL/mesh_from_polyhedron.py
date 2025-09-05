from CGAL.CGAL_Polyhedron_3 import Polyhedron_3, Polyhedron_modifier
from CGAL.CGAL_Mesh_3 import Mesh_3_Complex_3_in_triangulation_3
from CGAL.CGAL_Mesh_3 import Polyhedral_mesh_domain_3
from CGAL.CGAL_Mesh_3 import Mesh_3_parameters
from CGAL.CGAL_Mesh_3 import Default_mesh_criteria
from CGAL.CGAL_Kernel import Point_3
from CGAL import CGAL_Mesh_3

import os
from vedo import Mesh

from cgal_utils import CGAL_Mesh_from, CGAL_Mesh_3_IO_Util

class CGAL_Mesh_from_polyhedron(CGAL_Mesh_from):
    def __init__(self, filename = None, polyhedron = None):
        if(filename is None and polyhedron is None):
            raise ValueError("Need either a filename to load or a CGAl polyhedron already build")
        if(filename is not None):
            mesh = Mesh(filename)
            self.polyhedron = Polyhedron_3()
            pm =  Polyhedron_modifier()

            pm.begin_surface(3,1)
            for point in mesh.points:
                pm.add_vertex(Point_3(point[0],point[1],point[2]))

            for cell in mesh.cells:
                pm.begin_facet()
                pm.add_vertex_to_facet(int(cell[0]))
                pm.add_vertex_to_facet(int(cell[1]))
                pm.add_vertex_to_facet(int(cell[2]))
                pm.end_facet()


            self.polyhedron.delegate(pm) 
        else:
            self.polyhedron = polyhedron
        
        print(f"Polyhedron (vertices, facets, edges) = {(self.polyhedron.size_of_vertices(), self.polyhedron.size_of_facets(), self.polyhedron.size_of_halfedges()/2)}")





    def generate(self, criteria = Default_mesh_criteria()
                                      .facet_angle(25)
                                      .facet_size(0.15)
                                      .facet_distance(0.008)
                                      .cell_radius_edge_ratio(3),
                    refiner = CGAL_Mesh_from.Refiner_input(refiner_type=CGAL_Mesh_from.Refiner.NONE)):
        
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


        self.IOUtil = CGAL_Mesh_3_IO_Util(c3t3)
        #self.IOUtil.extract([CGAL_Mesh_3_IO_Util.Elem.POINTS, CGAL_Mesh_3_IO_Util.Elem.TETRA])

    def write_out(self, filename):
        self.IOUtil.write_out(filename)
        


#'data/mesh/torus.obj'



#writer = vtk.vtkPolyDataWriter()
#writer.SetFileVersion(42)


# Create input polyhedron



#for cell in c3t3.cells():
#    for i in range(4):
#        id = c3t3.index(cell.vertex(i))
#        if id.is_of_first_type():
#            print(id.get_first())
#        else:
#            print(id.get_second())



