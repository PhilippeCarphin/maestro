
MAESTRO_CORE="$PWD/maestro-core"
MAESTRO_TCL="$PWD/maestro-tcl"
ssm_folder="ssm"

echo "

# Load gnu compiler instead of default intel:
module switch PrgEnv-intel/5.2.82 PrgEnv-gnu

# Put a generic environment tag instead of chipset specific name
export ORDENV_PLAT=sles-11-amd64-64

cd $MAESTRO_CORE/ssm
make clean
make || exit 1

# Now compile tcl for SLES
cd $MAESTRO_TCL/ssm
make clean
make || exit 1

" | ssh hare bash --login