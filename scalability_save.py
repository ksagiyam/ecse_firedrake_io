from firedrake import *
from petsc4py import PETSc
import os


# Set the refinement level.
refinements = 1

mesh_name = "m"
func_name = "f"
input_file = "scalability_base_mesh.h5"
output_file_base = "scalability_load_"


def _expr(x, y, z):
    return sin(16 * 2 * pi * (x + y + z))


def _initialise(f):
    V = f.function_space()
    elem = V.ufl_element()
    m = V.mesh()
    x, y, z = SpatialCoordinate(m)
    if elem.value_shape() == ():
        f.interpolate(_expr(x, y, z))
    else:
        raise ValueError(f"Not for shape = {elem.value_shape()}")


# Set Parameters.
comm = COMM_WORLD
output_file = os.path.join(output_file_base + str(refinements) + ".h5")
distribution_parameters = {"overlap_type": (DistributedMeshOverlapType.NONE, 0), }
# Load base Mesh.
PETSc.Sys.Print("Loading Mesh ...", flush=True)
with CheckpointFile(input_file, "r", comm=comm) as afile:
    mesh = afile.load_mesh(mesh_name, distribution_parameters=distribution_parameters)
# Refine Mesh.
if refinements != 0:
    PETSc.Sys.Print("Refining ...", flush=True)
    meshes = MeshHierarchy(mesh, refinements, distribution_parameters=distribution_parameters)
    mesh = meshes[-1]
    mesh.name = mesh_name
# Construct DP4 Function.
PETSc.Sys.Print("Constructing Function ...", flush=True)
V = FunctionSpace(mesh, "DG", 4)
f = Function(V, name=func_name)
_initialise(f)
x, y, z = SpatialCoordinate(mesh)
expr = _expr(x, y, z)
l2err = assemble(inner(f - expr, f - expr) * dx)
# Compute Error of interpolation.
PETSc.Sys.Print("||f_interp - f|| = ", l2err, flush=True)
# Save Mesh/Function.
with CheckpointFile(output_file, "w", comm=comm) as afile:
    PETSc.Sys.Print("Saving Mesh ...", flush=True)
    afile.save_mesh(mesh)
    PETSc.Sys.Print("Saving Function ...", flush=True)
    afile.save_function(f)
