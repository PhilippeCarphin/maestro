
this_file=$(realpath ${BASH_SOURCE[0]})
this_dir=$(cd $(dirname ${this_file}) && pwd)
domain_dir=$(cd ${this_dir}/.. && pwd)

# export SEQ_BIN=/fs/ssm/eccc/cmo/isst/maestro/1.7.0/maestro_1.7.0_ubuntu-18.04-skylake-64/bin
export SEQ_BIN=${this_dir}/bin
export MAESTRO_BIN=${this_dir}/bin
# export SEQ_MAESTRO_DOMAIN=/fs/ssm/eccc/cmo/isst/maestro/1.7.0
export SEQ_MAESTRO_DOMAIN=${domain_dir}
export MAESTRO_DOMAIN=${SEQ_MAESTRO_DOMAIN}
export SEQ_MAESTRO_SHORTCUT=". ssmuse-sh -d ${domain_dir}"
export SEQ_MAESTRO_VERSION=1.7.0
export SEQ_MANAGER_BIN=${this_dir}/bin
export SEQ_MANAGER_DOMAIN=${domain_dir}
# export SEQ_MANAGER_SRC=/fs/ssm/eccc/cmo/isst/maestro/1.7.0/maestro_1.7.0_ubuntu-18.04-skylake-64/src/xm
export SEQ_MANAGER_SRC=${this_dir}
export SEQ_PACKAGE_HOME=${this_dir}
# export SEQ_SRC=/fs/ssm/eccc/cmo/isst/maestro/1.7.0/maestro_1.7.0_ubuntu-18.04-skylake-64/src
export SEQ_SRC=${this_dir}/src
# export SEQ_TCL_BIN=/fs/ssm/eccc/cmo/isst/maestro/1.7.0/maestro_1.7.0_ubuntu-18.04-skylake-64/tcl_bin
export SEQ_TCL_BIN=${this_dir}/bin
# export SEQ_TCL_LIB=/fs/ssm/eccc/cmo/isst/maestro/1.7.0/maestro_1.7.0_ubuntu-18.04-skylake-64/src/tcl/lib
export SEQ_TCL_LIB=${this_dir}/lib
# export SEQ_TCL_SRC=/fs/ssm/eccc/cmo/isst/maestro/1.7.0/maestro_1.7.0_ubuntu-18.04-skylake-64/src/tcl
export SEQ_TCL_SRC=${this_dir}/src
export SEQ_UTILS_BIN=${this_dir}/bin
export SEQ_UTILS_DOMAIN=${domain_dir}
# export SEQ_WRAPPERS=/fs/ssm/eccc/cmo/isst/maestro/1.7.0/maestro_1.7.0_ubuntu-18.04-skylake-64/src/core
export SEQ_WRAPPERS=${this_dir}/wrappers
export SEQ_XFLOW_BIN=${this_dir}/bin
export SEQ_XFLOW_DOMAIN=${domain_dir}

# MANPATH
#     ADDED:
#       /fs/ssm/eccc/cmo/isst/maestro/1.7.0/maestro_1.7.0_ubuntu-18.04-amd64-64/man
#       /fs/ssm/eccc/cmo/isst/maestro/1.7.0/ubuntu-18.04-skylake-64/share/man
#       /fs/ssm/eccc/cmo/isst/maestro/1.7.0/maestro_1.7.0_ubuntu-18.04-skylake-64/man
#       /fs/ssm/eccc/cmo/isst/maestro/1.7.0/ubuntu-18.04-amd64-64/share/man

# PATH
#     ADDED:
#       /fs/ssm/eccc/cmo/isst/maestro/1.7.0/ubuntu-18.04-skylake-64/bin
#       /fs/ssm/eccc/cmo/isst/maestro/1.7.0/ubuntu-18.04-amd64-64/bin
export PATH=${this_dir}/bin:${PATH}

export LD_LIBRARY_PATH=${this_dir}/lib:${LD_LIBRARY_PATH}

# PYTHONPATH
#     ADDED:
#       /fs/ssm/eccc/cmo/isst/maestro/1.7.0/ubuntu-18.04-amd64-64/lib/python
#       /fs/ssm/eccc/cmo/isst/maestro/1.7.0/ubuntu-18.04-skylake-64/lib/python
# TCL_LIBRARY
#     ADDED:
#       /fs/ssm/eccc/cmo/isst/maestro/1.7.0/ubuntu-18.04-skylake-64/lib/tcl
#       /fs/ssm/eccc/cmo/isst/maestro/1.7.0/ubuntu-18.04-amd64-64/lib/tcl
export TCL_LIBRARY=${this_dir}/lib
