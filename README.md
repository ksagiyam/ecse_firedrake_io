# ecse_firedrake_io

This repository contains supporting code and data for the scalability tests performed in:
"ARCHER2-eCSE01-20: Scalable I/O and checkpointing for Firedrake"

Follow the instructions at https://www.firedrakeproject.org/zenodo.html
to install the archived version of Firedrake with the DOI referenced in the technical report.

For saving, set the "refinements" parameter (for refinement level) at the beginning of "scalability_save.py" and run:

$ mpiexec -n nproc_for_save python scalability_save.py -log_view :output_save.txt:ascii_flamegraph

For loading, set the "refinements" parameter (for refinement level) at the beginning of "scalability_load.py" and run:

$ mpiexec -n nproc_for_load python scalability_load.py -log_view :output_load.txt:ascii_flamegraph

output_save.txt and output_load.txt will contain timing results, which one can visualise with flamegraph; see https://www.firedrakeproject.org/optimising.html.

Each loading example checks if the loaded function is identical to the saved one.

Note that 1-, 8-, 64-node examples for saving presented in Section 4.2 of
the technical report correspond refinement_levels of 2, 3, 4, respectively.

Before running loading examples, saving examples with the matching refinement_levels
must be run.
