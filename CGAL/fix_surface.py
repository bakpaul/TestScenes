import pymeshfix
import pyvista as pv

# Load the triangular mesh
mesh = pv.read('data/mesh/torus.obj')

# Initialize MeshFix
meshfix = pymeshfix.MeshFix(mesh)

# Repair the mesh (closes holes, fixes non-manifold edges)
meshfix.repair()

# Export the watertight surface
meshfix.save("surface_watertight.obj")
