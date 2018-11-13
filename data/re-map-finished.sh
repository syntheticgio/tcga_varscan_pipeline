#!/bin/bash

while IFS=, read -r TCGA passed || [[ -n "$TCGA" ]]; do
	#echo "TCGA: ${TCGA}"
	#b=`gsutil ls -l gs://iron-eye-6998/tcga_wgs_results/${TCGA}/varscan_results/TCGA* | awk '{FS="("; if(NR > 1) {print $2;}}' | awk '{FS=" "; gsub(")",""); print $2;}'`
        #echo ${b}
	
	if [[ "${passed}" == " PASSED" ]]; then
		grep ${TCGA} FINISHED_DATA_.csv >> finished_and_passed.csv
	else
		grep ${TCGA} FINISHED_DATA_.csv >> finished_and_failed.csv 
	fi 
done < "$1"
