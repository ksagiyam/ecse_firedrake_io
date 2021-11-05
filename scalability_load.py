from firedrake import *
from petsc4py import PETSc
import os


# Set the refinement level.
refinements = 1

mesh_name = "m"
func_name = "f"
input_file_base = "scalability_load_"


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


# Set Parameters
comm = COMM_WORLD
input_file = os.path.join(input_file_base + str(refinements) + ".h5")
distribution_parameters = {"overlap_type": (DistributedMeshOverlapType.NONE, 0), }
# Load
with CheckpointFile(input_file, "r", comm=comm) as afile:
    PETSc.Sys.Print("Loading Mesh ...", flush=True)
    mesh = afile.load_mesh(mesh_name, distribution_parameters=distribution_parameters)
    PETSc.Sys.Print("Loading Function ...", flush=True)
    f = afile.load_function(mesh, func_name)
# Check loaded function against directly interpolated one.
# These two should virtually be identical.
V = f.function_space()
fe = Function(V)
_initialise(fe)
err = assemble(inner(f - fe, f - fe) * dx)
PETSc.Sys.Print("||f_interpolated - f_loaded||^2 = ", err, flush=True)
