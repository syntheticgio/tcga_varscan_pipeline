#!/bin/bash

echo "This script will perform some quality assurance and final post-processing steps for the variant call pipeline."
echo "This shoudl be run from the src/ directory within the project."
echo ""
echo "Creating Quality Assurance Directory"
rm -rf ./QA
mkdir -p QA
cp post_process/generate_bar_graphs.rscrpt QA/
echo "Moving into QA Directory!"
cd QA
echo "Currently: "`pwd`

gsutil ls gs://iron-eye-6998/tcga_wgs_results | awk 'BEGIN{FS="/";}{if (NR > 1) {print $5;}}' > get_ids.txt

while IFS='' read -r TCGA || [[ -n "$TCGA" ]]; do
	b=`gsutil ls -l gs://iron-eye-6998/tcga_wgs_results/${TCGA}/varscan_results/TCGA* | awk '{FS="("; if(NR > 1) {print $2;}}' | awk '{FS=" "; gsub(")",""); print $2;}'`
	if [[ "${b}" == "MiB" ]] || [[ "${b}" == "GiB" ]]; then
		echo "${TCGA}" >> finished_tcga_ids.txt
	else
        echo "${TCGA}" >> failed_ids.txt
	fi 
#echo -ne "P: ${passed} / F: ${failed}"\\r
done < "get_ids.txt"

echo ""
echo "Retrieved all IDs, beginning post processing."

while IFS='' read -r TCGA_ID || [[ -n "$TCGA_ID" ]]; do
    echo "Beginning working on ${TCGA_ID}"
    mkdir -p ${TCGA_ID}
    cp generate_bar_graphs.rscript ${TCGA_ID}/
    pushd .
    cd ${TCGA_ID}
    gsutil cp gs://iron-eye-6998/tcga_wgs_results/${TCGA_ID}/varscan_results/*.gz .
    
    tar zxvf *.gz
    rm *.gz
    wc -l $(ls -1 *.snp.vcf) | awk '{gsub("_", " "); print $0;}' | awk 'BEGIN{FS=" "; print"Count,TCGA,Chrom";}{gsub(".snp.vcf", " "); if($2 != "total"){gsub("chr", "", $3); print $1","$2","$3;}}' | sort -k 3,3 -n -t "," > snps_by_chrom.csv
    wc -l $(ls -1 *.indel.vcf) | awk '{gsub("_", " "); print $0;}' | awk 'BEGIN{FS=" "; print"Count,TCGA,Chrom";}{gsub(".indel.vcf", " "); if($2 != "total"){gsub("chr", "", $3); print $1","$2","$3;}}' | sort -k 3,3 -n -t "," > indels_by_chrom.csv
    echo -e "\tGenerating bargraphs ..."
    Rscript generate_bar_graphs.rscript
    rm generate_bar_graphs.rscript
    echo -e "\tGenerating combined VCF files"
    vcf-concat $(ls -1 *.snp.vcf | perl -pe 's/\n/ /g') > ${TCGA_ID}.all.snp.vcf
    vcf-concat $(ls -1 *.indel.vcf | perl -pe 's/\n/ /g') > ${TCGA_ID}.all.indel.vcf
    rm *chr*.vcf ## Leave us just with the all snp and indel vcfs
    echo -e "\tVarScan processSomatic call.. (SNPs)"
    java -jar /varscan/varscan/VarScan.jar processSomatic \
        "${TCGA_ID}".all.snp.vcf \
        --min-tumor-freq 0.10 \
        --max-normal-freq 0.05 \
        --p-value 0.07
    echo -e "\tVarScan processSomatic call.. (Indels)"
    java -jar /varscan/varscan/VarScan.jar processSomatic \
        "${TCGA_ID}".all.indel.vcf \
        --min-tumor-freq 0.10 \
        --max-normal-freq 0.05 \
        --p-value 0.07
    # Get total counts for indels and SNPs - can be used in QA with the above barplots
    echo -e "\tFinal Counts"
    wc -l $(ls -1 *.vcf) | awk 'BEGIN{FS=" "; print"Count,File";}{print $1","$2;}' > ${TCGA_ID}_total_counts.txt
    cd ..

done < "finished_tcga_ids.txt"