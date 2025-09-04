from CGAL.CGAL_Polyhedron_3 import Polyhedron_3, Polyhedron_modifier
from CGAL.CGAL_Mesh_3 import Mesh_3_Complex_3_in_triangulation_3
from CGAL.CGAL_Mesh_3 import Polyhedral_mesh_domain_3
from CGAL.CGAL_Mesh_3 import Mesh_3_parameters
from CGAL.CGAL_Mesh_3 import Default_mesh_criteria
from CGAL.CGAL_Kernel import Point_3
from CGAL import CGAL_Mesh_3

import os
from vedo import Mesh


#writer = vtk.vtkPolyDataWriter()
#writer.SetFileVersion(42)

mesh = Mesh('data/mesh/torus.obj')

# Create input polyhedron
polyhedron = Polyhedron_3()
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


polyhedron.delegate(pm)
print(f"(v,f,e) = {(polyhedron.size_of_vertices(), polyhedron.size_of_facets(), polyhedron.size_of_halfedges()/2)}")

# Create domain
domain = Polyhedral_mesh_domain_3(polyhedron)
params = Mesh_3_parameters()
params.no_exude()
params.no_perturb()

# Mesh criteria (no cell_size set)
criteria = Default_mesh_criteria()
criteria.facet_angle(25).facet_size(0.15).facet_distance(
    0.008).cell_radius_edge_ratio(3)
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


