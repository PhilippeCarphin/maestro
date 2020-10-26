# loop_post_gem parameters
loop_post_gem_start=0
loop_post_gem_end=672
loop_post_gem_delta=24
gem_dt=450

# Current loop
START=0    # Output start in hour
END=84     # Output end   in hour
DELTA=6    # Output delta in hour, must by a multiple of POSTFREQ
#==========================
# No change below this line

((NB=(END-START)/DELTA+1))
cat <<EOF
<NODE_RESOURCES>
  <LOOP expression="${START}:${END}:${DELTA}:${NB}"/>
EOF

# get step_list
for step in $(seq ${loop_post_gem_start} ${loop_post_gem_delta} ${loop_post_gem_end});do

   step_list="${step_list} ${step}"
   
done
if [ ${step} -ne ${loop_post_gem_end} ];then
   step_list="${step_list} ${loop_post_gem_end}"
fi

# Special case for 0 hour
set ${step_list}
echo  "  <DEPENDS_ON exp=\"\${FORECAST_EXP}\" dep_name=\"\${INTXFER_GEM_TRANSFER_NAME_0hr}\" index=\"post_gem=0\" status=\"end\" type=\"node\" local_index=\"loop_prog=0\"/>"
echo  "  <DEPENDS_ON exp=\"\${FORECAST_EXP}\" dep_name=\"\${INTXFER_GEM_TRANSFER_NAME}\" index=\"post_gem=${1}\" status=\"end\" type=\"node\" local_index=\"loop_prog=0\"/>"
((begin=START+DELTA))
hour_m=${START}
for hour in $(seq ${begin} ${DELTA} ${END});do

   #echo ${hour_m} ${hour}
   # Find all loop_post_gem iterations needed
   for step in ${step_list};do
      ((prog=step*gem_dt/3600))
      if [ ${prog} -gt ${hour_m} -a ${prog} -le ${hour} ];then
         echo  "  <DEPENDS_ON exp=\"\${FORECAST_EXP}\" dep_name=\"\${INTXFER_GEM_TRANSFER_NAME}\" index=\"post_gem=${step}\" status=\"end\" type=\"node\" local_index=\"loop_prog=${hour}\"/>"         
	 LAST=${prog}
      fi
   done
   if [ ${LAST} -lt ${hour} ];then
      # The step just after ${hour} is also needed
      FOUND=0
      for step in ${step_list};do
         ((prog=step*gem_dt/3600))
         if [ ${prog} -gt ${hour} -a ${FOUND} = 0 ];then
	    echo  "  <DEPENDS_ON exp=\"\${FORECAST_EXP}\" dep_name=\"\${INTXFER_GEM_TRANSFER_NAME}\" index=\"post_gem=${step}\" status=\"end\" type=\"node\" local_index=\"loop_prog=${hour}\"/>"  
            FOUND=1
         fi
      done
   fi
     
   hour_m=${hour}
done

echo '</NODE_RESOURCES>'
