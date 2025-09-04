from CGAL.CGAL_Polyhedron_3 import Polyhedron_3, Polyhedron_modifier
from CGAL.CGAL_Mesh_3 import Mesh_3_Complex_3_in_triangulation_3
from CGAL.CGAL_Mesh_3 import Polyhedral_mesh_domain_3
from CGAL.CGAL_Mesh_3 import Mesh_3_parameters
from CGAL.CGAL_Mesh_3 import Default_mesh_criteria
from CGAL.CGAL_Kernel import Point_3
from CGAL import CGAL_Mesh_3


from enum import Enum


class CGAL_Mesh_3_IO_Util(object):
    class Elem(Enum):
        POINTS = 1
        EDGES = 2
        TRIANGLES = 3
        TETRA = 4

    def __init__(self,mesh):
        self.mesh = mesh

    def extract(self, elems : list[Elem]):
        pass

    def write_out(self, filename):
        pass




# Mesh generation
c3t3 = CGAL_Mesh_3.make_mesh_3(domain, criteria, params)


for cell in c3t3.cells():
    for i in range(4):
        id = c3t3.index(cell.vertex(i))
        if id.is_of_first_type():
            print(id.get_first())
        else:
            print(id.get_second())


# Output
c3t3.write_to_file("out_1.mesh")


