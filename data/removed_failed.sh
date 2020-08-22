#!/bin/bash

i=0
passed=0
failed=0
while IFS='' read -r TCGA || [[ -n "$TCGA" ]]; do
	#echo "TCGA: ${TCGA}"
        tcga_id=`echo ${TCGA} | awk 'BEGIN{FS=", ";OFS=", "}{print $1}'`
        pass_fail=`echo ${TCGA} | awk 'BEGIN{FS=", ";OFS=", "}{print $2}'`
        #echo "${tcga_id} -- ${pass_fail}"
        if [[ "${pass_fail}" == "FAILED" ]]; then
              echo "Deleting ${tcga_id} -- ${pass_fail}"
              gsutil -m rm -rf gs://iron-eye-6998/tcga_wgs_results/${tcga_id}
        fi
	#b=`gsutil ls -l gs://iron-eye-6998/tcga_wgs_results/${TCGA}/varscan_results/TCGA* | awk '{FS="("; if(NR > 1) {print $2;}}' | awk '{FS=" "; gsub(")",""); print $2;}'`
        #echo ${b}
	#if [[ "${b}" == "MiB" ]]; then
	#	echo ${TCGA}", PASSED" >> verification.csv
#		passed=$((passed+1))
#	else
##		echo ${TCGA}", FAILED" >> verification.csv 
#		failed=$((failed+1))
#	fi 
#i=$((i+1))
#echo "On line ${i}"
#echo "Passed: ${passed}"
#echo "Failed: ${failed}"
done < "$1"
