#!/bin/bash

i=0
while IFS='' read -r TCGA || [[ -n "$TCGA" ]]; do
	#echo "TCGA: ${TCGA}"
	b=`gsutil ls -l gs://iron-eye-6998/tcga_wgs_results/${TCGA}/varscan_results/TCGA* | awk '{FS="("; if(NR > 1) {print $2;}}' | awk '{FS=" "; gsub(")",""); print $2;}'`
        #echo ${b}
	if [[ "${b}" == "MiB" ]]; then
		echo ${TCGA}", PASSED" >> verification.csv
	else
		echo ${TCGA}", FAILED" >> verification.csv 
	fi 
i=$((i+1))
echo "On line ${i}"
done < "$1"
