SHARED_MAKE_CONFIGURATION=shared-make-configuration.cfg
include ${SHARED_MAKE_CONFIGURATION}

all: clean
	echo "VERSION = '${VERSION}'"
	echo "ORDENV_PLAT = '${ORDENV_PLAT}'"
	# Abort if VERSION was not set.
	if [[ -z "${VERSION}" ]] ; then \
		echo "Aborted. Failed to find VERSION." ;\
		exit 1 ;\
	fi
	
	mkdir -p ${MAN_FOLDER}
	if [[ ${HAS_INTERNET} = "true" ]] ; then \
		cd man ; ./create_roffs_from_markdown.sh ;\
		cp -r ${MAESTRO_PROJECT_ROOT}/man/roff/* ${MAN_FOLDER}/ ;\
		echo "Creating a man page backup which survive clean makes, for offline makes." ;\
		mkdir -p ${OFFLINE_MAN_BACKUP} ;\
		cp -r ${MAESTRO_PROJECT_ROOT}/man/roff/* ${OFFLINE_MAN_BACKUP}/ ;\
	else \
		echo "Skipping generation of man pages, as there seems to be no internet. Using roff files generated from previous online builds instead." ;\
		cp -r ${OFFLINE_MAN_BACKUP}/* ${MAN_FOLDER} ;\
		sleep 2 ;\
	fi

	if [ -n "${IS_XC}" ] ; then \
			echo "Compiling on some architectures like xc40 and xc50 requires that we specify a module for a different 'gcc'." ;\
			echo "In this case we are using this module switch:" ;\
			echo "        ${XC_MODULE_SWITCH}" ;\
			echo "And adding these compiler flags:" ;\
			echo "        ${XC_DYNAMIC_FLAG}" ;\
	fi

	mkdir -p ${BUILD_PLATFORM_FOLDER} ${BIN_FOLDER} ${WRAPPERS_BUILD_FOLDER}
	
	${SCRIPTS_FOLDER}/copy_wrappers.sh ${WRAPPER_PREFIX} ${WRAPPERS_BUILD_FOLDER}
	cp ${SHARED_MAKE_CONFIGURATION} ${BUILD_PLATFORM_FOLDER}/
	cp -r src ssm/.ssm.d bin scripts python3 config schemas csv setup ${BUILD_PLATFORM_FOLDER}/

	${BUILD_PLATFORM_FOLDER}/setup/install-python-dependencies.sh
	${XC_MODULE_SWITCH} make -C ${BUILD_PLATFORM_FOLDER}/src/core

	if [ -d "${TCL_COMPILE_BACKUP_FOLDER}" ] ; then \
		echo "Using '${TCL_COMPILE_BACKUP_FOLDER}' instead of building tcl from source." ;\
		rm -rf ${BUILD_PLATFORM_FOLDER}/src/tcl ;\
		mkdir -p ${BUILD_PLATFORM_FOLDER}/src/tcl ;\
		cp -a ${TCL_COMPILE_BACKUP_FOLDER}/tcl ${BUILD_PLATFORM_FOLDER}/src/ ;\
	elif [ -z ${IS_XC} ] ; then \
		echo "Could not find _tcl folder, building tcl from source." ;\
		sleep 4 ;\
		echo "Piping make command to bash so that the long and fragile tcl compilation does not inherit the maestro build environment. This first caused a problem after the variable VERSION was used." ;\
		echo "${XC_MODULE_SWITCH} cd ${BUILD_PLATFORM_FOLDER}/src/tcl ; make" | env -i bash ;\
		echo "Copying compiled tcl library to backup folder so future makes are faster: '${TCL_COMPILE_BACKUP_FOLDER}'" ;\
		mkdir -p ${TCL_COMPILE_BACKUP_FOLDER} ;\
		cp -a ${BUILD_PLATFORM_FOLDER}/src/tcl ${TCL_COMPILE_BACKUP_FOLDER} ;\
	fi \
	
	. ${SSM_FOLDER}/create_ssm_control_files.sh "${VERSION}" "${BUILD_PLATFORM_FOLDER}/.ssm.d"
	${SSM_FOLDER}/create_ssm_packages.sh "${VERSION}"
	
clean:
	rm -rf ${BIN_FOLDER}
	# Delete all builds for this ord environment platform
	rm -rf ${BUILD_FOLDER}/*${ORDENV_PLAT}*
	find ${SOURCE_FOLDER} -name "*\.o" -exec rm {} \;
	rm -f ${SSM_FOLDER}/*${ORDENV_PLAT}*.ssm

	mkdir -p build
