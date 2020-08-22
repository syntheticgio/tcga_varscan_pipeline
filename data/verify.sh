#!/bin/bash

i=0
passed=0
failed=0
while IFS='' read -r TCGA || [[ -n "$TCGA" ]]; do
	#echo "TCGA: ${TCGA}"
	b=`gsutil ls -l gs://iron-eye-6998/tcga_wgs_results/${TCGA}/varscan_results/TCGA* | awk '{FS="("; if(NR > 1) {print $2;}}' | awk '{FS=" "; gsub(")",""); print $2;}'`
        #echo ${b}
	if [[ "${b}" == "MiB" ]]; then
		echo ${TCGA}", PASSED" >> verification.csv
		passed=$((passed+1))
	else
		echo ${TCGA}", FAILED" >> verification.csv 
		failed=$((failed+1))
	fi 
i=$((i+1))
echo "On line ${i}"
echo "Passed: ${passed}"
echo "Failed: ${failed}"
done < "$1"
