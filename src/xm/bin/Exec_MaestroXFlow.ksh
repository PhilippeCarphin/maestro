#!/bin/ksh


export SEQ_EXP_HOME=$1
if [[ "${MAESTRO_BIN}" == "" ]]; then 
   echo "MAESTRO_BIN not defined..."
   errMsg="MAESTRO_BIN not defined, cannot start xflow!"
   kdialogFound=0
   test $(which kdialog) && kdialogFound=1
   if [[ ${kdialogFound} == "1"  ]] ; then
      kdialog --title "xflow Startup Error" --error "${errMsg}"
   else
      echo ${errMsg}
   fi
   exit 1
else
   ${MAESTRO_BIN}/xflow
fi
