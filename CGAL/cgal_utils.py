from CGAL.CGAL_Polyhedron_3 import Polyhedron_3, Polyhedron_modifier
from CGAL.CGAL_Mesh_3 import Mesh_3_Complex_3_in_triangulation_3
from CGAL.CGAL_Mesh_3 import Polyhedral_mesh_domain_3
from CGAL.CGAL_Mesh_3 import Mesh_3_parameters
from CGAL.CGAL_Mesh_3 import Default_mesh_criteria
from CGAL.CGAL_Kernel import Point_3
from CGAL import CGAL_Mesh_3

import numpy as np
import dataclasses
from typing import List, Optional

from enum import Enum


class CGAL_Mesh_3_IO_Util(object):
    
    points    : np.array
    triangles : np.array
    tetras    : np.array
    
    class Elem(Enum):
        POINTS = 1
        TRIANGLES = 3
        TETRA = 4

    def __init__(self,mesh):
        self.mesh = mesh

    def extract(self, elems : list[Elem]):
        for elem in elems:
            vnbe = {}
            match elem:
                case CGAL_Mesh_3_IO_Util.Elem.TRIANGLES:
                    for elem in self.mesh.facets():
                        for i in range(3):
                            if not elem.vertex in vnbe:
                                vnbe[elem.vertex(i)] = 1 
                            else:
                                vnbe[elem.vertex(i)] += 1 
                case CGAL_Mesh_3_IO_Util.Elem.TETRA:
                    for elem in self.mesh.cells():
                        for i in range(4):
                            if not elem.vertex in vnbe:
                                vnbe[elem.vertex(i)] = 1 
                            else:
                                vnbe[elem.vertex(i)] += 1 

            if CGAL_Mesh_3_IO_Util.Elem.POINTS in elems:
                self.points = np.array([])
            else: 
                self.points = None
            
            V = {}
            it = 0
            for vertice in self.mesh.triangluation().finite_vertices():
                if vertice in vnbe:
                    V[vertice] = it
                    if self.points is not None:
                        self.points.append(self.mesh.triangluation().point(vertice))
                    it += 1 

            match elem:
                case CGAL_Mesh_3_IO_Util.Elem.TRIANGLES:
                    self.triangles = np.array([])
                    for elem in self.mesh.facets():
                        self.triangles.append(np.array([V[elem.vertex(0)],V[elem.vertex(1)],V[elem.vertex(2)]]))
                case CGAL_Mesh_3_IO_Util.Elem.TETRA:
                    self.tetras = np.array([])
                    for elem in self.mesh.cells():
                        self.tetras.append(np.array([V[elem.vertex(0)],V[elem.vertex(1)],V[elem.vertex(2), V[elem.vertex(3)]]]))
                        

    def write_out(self, filename):
        pass



class CGAL_Mesh_from(object):
    
    class Refiner(Enum):
        NONE = 0
        LLOYD = 1
        ODT = 3
        PERTURB = 4

    @dataclasses.dataclass
    class Refiner_input():
        refiner_type : Enum

        time_limit : Optional[float] = 20.0         #(ALL)              to set up, in seconds, a CPU time limit after which the optimization process is stopped. This time is measured using CGAL::Real_timer. 0 means that there is no time limit. 
        max_iteration_number : Optional[int] = 200  #(LLOYD & ODT only) limit on the number of performed iterations. 0 means that there is no limit on the number of performed iterations.   
        convergence : Optional[int] = 0.0           #(LLOYD & ODT only) threshold ratio of stopping criterion based on convergence: the optimization process is stopped when at the last iteration the displacement of any vertex is less than a given fraction of the length of the shortest edge incident to that vertex.
        free_bound : Optional[bool] = False         #(LLOYD & ODT only) designed to reduce running time of each optimization iteration. Any vertex that has a displacement less than a given fraction of the length of its shortest incident edge, is frozen (i.e. is not relocated). The parameter freeze_bound gives the threshold ratio. If it is set to 0, freezing of vertices is disabled. 
        silver_bound : Optional[bool] = False       #(PERTURB only)     is designed to give, in degrees, a targeted lower bound on dihedral angles of mesh cells. The exudation process considers in turn all the mesh cells that have a smallest dihedral angle less than sliver_bound and tries to make them disappear by weighting their vertices. The optimization process stops when every cell in the mesh achieves this quality. The default value is 0 and means that there is no targeted bound: the exuder then runs as long as it can improve the smallest dihedral angles of the set of cells incident to some vertices. 
        

    IOUtil : CGAL_Mesh_3_IO_Util

    def __init__(self):
        pass

    def generate(self):
        pass


    def __getattr__(self, name):
        match name:
            case "points":
                return self.IOUtil.points
            case "triangles":
                return self.IOUtil.triangles
            case "tetras":
                return self.IOUtil.tetras
            case _:
                if name in self.__dict__:
                    return self.__dict__[name]
                else:
                    raise AttributeError()
    


