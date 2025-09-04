import gmsh

# Initialize Gmsh
gmsh.initialize()
gmsh.open('surface_watertight.obj')  # Replace with your OBJ filename

# Synchronize geometry
gmsh.model.geo.synchronize()

# Remove duplicate nodes and elements
gmsh.model.mesh.removeDuplicateNodes()
gmsh.model.mesh.removeDuplicateElements()

# Try to fill small holes automatically
gmsh.model.mesh.removeDuplicateNodes()

# Reconstruct geometry from the surface mesh
gmsh.model.mesh.classifySurfaces(
    40 * (3.14159 / 180),   # angle threshold for sharp features
    True,
    False,
    180 * (3.14159 / 180)
)
gmsh.model.mesh.createGeometry()
gmsh.model.geo.synchronize()

# Create a volume from the closed surface
surfaces = gmsh.model.getEntities(2)
sl = gmsh.model.geo.addSurfaceLoop([s[1] for s in surfaces])
gmsh.model.geo.addVolume([sl])
gmsh.model.geo.synchronize()

# Generate tetrahedral mesh
gmsh.model.mesh.generate(3)

# Save the mesh in VTK format
gmsh.write("volume_mesh.vtk")

# -------------------------
# Visualization step
# -------------------------
gmsh.fltk.run()

# Finalize
gmsh.finalize()