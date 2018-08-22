
MAESTRO_CORE="$PWD/maestro"
MAESTRO_TCL="$PWD/maestro-tcl/tcl-tk_8.5.11_multi"

ssh hare "

cd $MAESTRO_CORE/src

# Load gnu compiler instead of default intel:
module switch PrgEnv-intel/5.2.82 PrgEnv-gnu

# Put a generic environment tag instead of chipset specific name
export ORDENV_PLAT=sles-11-amd64-64

# Compile with dynamic libs:
make clean
make

# Create ssm package:
cd $MAESTRO_CORE/ssm
make clean
make

# Now compile tcl for SLES
cd $MAESTRO_TCL/ssm
make clean
make

"
