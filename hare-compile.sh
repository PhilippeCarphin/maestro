
MAESTRO_CORE="$PWD/maestro"

ssh hare "cd $MAESTRO_CORE/src

# load gnu compiler instead of default intel:
module switch PrgEnv-intel/5.2.82 PrgEnv-gnu

# put a generic environment tag instead of chipset specific name
export ORDENV_PLAT=sles-11-amd64-64

# compile with dynamic libs:
make clean
make -f Makefile.dynamic

# create ssm package:
cd $MAESTRO_CORE/ssm
make clean
make"
