
echo "

# Load gnu compiler instead of default intel:
module switch PrgEnv-intel/5.2.82 PrgEnv-gnu

# Put a generic environment tag instead of chipset specific name
export ORDENV_PLAT=sles-11-amd64-64

cd $PWD/src/core
make clean
make || exit 1

# Now compile tcl for SLES
cd $PWD/src/tcl
make clean
make || exit 1

" | ssh hare bash --login
