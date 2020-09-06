#!/bin/bash

i=0
passed=0
failed=0

rm -f finished_tcga_ids.txt
rm -f failed_ids.txt

gsutil ls gs://iron-eye-6998/tcga_wgs_results | awk 'BEGIN{FS="/";}{if (NR > 1) {print $5;}}' >get_ids.txt

while IFS='' read -r TCGA || [[ -n "$TCGA" ]]; do
	b=`gsutil ls -l gs://iron-eye-6998/tcga_wgs_results/${TCGA}/varscan_results/TCGA* | awk '{FS="("; if(NR > 1) {print $2;}}' | awk '{FS=" "; gsub(")",""); print $2;}'`
	if [[ "${b}" == "MiB" ]] || [[ "${b}" == "GiB" ]]; then
		echo "${TCGA}" >> finished_tcga_ids.txt
		passed=$((passed+1))
	else
		failed=$((failed+1))
                echo "${TCGA}" >> failed_ids.txt
	fi 
i=$((i+1))
echo -ne "P: ${passed} / F: ${failed}"\\r
done < "get_ids.txt"
echo ""
echo "All finished"
rm -f get_ids.txt
