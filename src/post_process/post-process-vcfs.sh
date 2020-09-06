#!/bin/bash

SNP_VALID_CHR_COUNT=22
INDEL_VALID_CHR_COUNT=20

echo "This script will perform some quality assurance and final post-processing steps for the variant call pipeline."
echo "This shoudl be run from the post-processing/ directory within the project."
echo ""
echo "This script currently assumes ${SNP_VALID_CHR_COUNT} valid (greater than 100000 bytes) SNP files for a chromosome are valid."
echo "This script currently assumes ${INDEL_VALID_CHR_COUNT} valid (greater than 100000 bytes) Indel file for a chromosome are valid."
echo "These settings can be set at the top of the script if they should be changed."
echo ""
echo "Creating Quality Assurance Directory"
rm -rf ./QA
mkdir -p QA
echo "Moving into QA Directory!"
cd QA
echo "Currently: "`pwd`

gsutil ls gs://iron-eye-6998/tcga_wgs_results | awk 'BEGIN{FS="/";}{if (NR > 1) {print $5;}}' > get_ids.txt

passed=0
failed=0

while IFS='' read -r TCGA || [[ -n "$TCGA" ]]; do
	b=`gsutil ls -l gs://iron-eye-6998/tcga_wgs_results/${TCGA}/varscan_results/TCGA* | awk '{FS="("; if(NR > 1) {print $2;}}' | awk '{FS=" "; gsub(")",""); print $2;}'`
	if [[ "${b}" == "MiB" ]] || [[ "${b}" == "GiB" ]]; then
		echo "${TCGA}" >> finished_tcga_ids.txt
        $((passed+1))
	else
        echo "${TCGA}" >> failed_ids.txt
        $((failed+1))
	fi 
    echo -ne "P: ${passed} / F: ${failed}"\\r
done < "get_ids.txt"

echo ""
echo "Retrieved all IDs, beginning post processing."

# Check to see if all chromosomes are represented
snp_chr_passed=0
indel_chr_passed=0


while IFS='' read -r TCGA_ID || [[ -n "$TCGA_ID" ]]; do
    echo -ne "Working on ${TCGA_ID}: Beginning\r"
    mkdir -p ${TCGA_ID}
    cp ../generate_bar_graphs.rscript ${TCGA_ID}/
    pushd .
    cd ${TCGA_ID}
    gsutil cp gs://iron-eye-6998/tcga_wgs_results/${TCGA_ID}/varscan_results/*.gz .
    tar zxvf *.gz
    rm *.gz
    # Get chr passed counts
    snp_chr_passed_=`ls -l *snp.vcf | awk 'BEGIN{a=0}{if($5>100000){a++;}}END{print a}'`
    indel_chr_passed_=`ls -l *indel.vcf | awk 'BEGIN{a=0}{if($5>100000){a++;}}END{print a}'`
    if [[ ${snp_chr_passed_} -gt ${SNP_VALID_CHR_COUNT} ]]; then
        snp_chr_passed_=$((snp_chr_passed+1))
    fi
    if [[ ${indel_chr_passed_} -gt ${INDEL_VALID_CHR_COUNT} ]]; then
        indel_chr_passed_=$((indel_chr_passed+1))
    fi
    # Generate rough SNP counts
    wc -l $(ls -1 *.snp.vcf) | awk '{gsub("_", " "); print $0;}' | awk 'BEGIN{FS=" "; print"Count,TCGA,Chrom";}{gsub(".snp.vcf", " "); if($2 != "total"){gsub("chr", "", $3); print $1","$2","$3;}}' | sort -k 3,3 -n -t "," > snps_by_chrom.csv
    wc -l $(ls -1 *.indel.vcf) | awk '{gsub("_", " "); print $0;}' | awk 'BEGIN{FS=" "; print"Count,TCGA,Chrom";}{gsub(".indel.vcf", " "); if($2 != "total"){gsub("chr", "", $3); print $1","$2","$3;}}' | sort -k 3,3 -n -t "," > indels_by_chrom.csv
    echo -ne "Working on ${TCGA_ID}: Generating Bargraphs\r"
    Rscript generate_bar_graphs.rscript
    rm generate_bar_graphs.rscript
    echo -ne "Working on ${TCGA_ID}: Generating VCFs\r"
    vcf-concat $(ls -1 *.snp.vcf | perl -pe 's/\n/ /g') > ${TCGA_ID}.all.snp.vcf
    vcf-concat $(ls -1 *.indel.vcf | perl -pe 's/\n/ /g') > ${TCGA_ID}.all.indel.vcf
    rm *chr*.vcf ## Leave us just with the all snp and indel vcfs
    echo -ne "Working on ${TCGA_ID}: VarScan processSomatic (SNPs)\r"
    java -jar /varscan/varscan/VarScan.jar processSomatic \
        "${TCGA_ID}".all.snp.vcf \
        --min-tumor-freq 0.10 \
        --max-normal-freq 0.05 \
        --p-value 0.07
    echo -ne "Working on ${TCGA_ID}: VarScan processSomatic (Indels)\r"
    java -jar /varscan/varscan/VarScan.jar processSomatic \
        "${TCGA_ID}".all.indel.vcf \
        --min-tumor-freq 0.10 \
        --max-normal-freq 0.05 \
        --p-value 0.07
    # Get total counts for indels and SNPs - can be used in QA with the above barplots
    echo -ne "Working on ${TCGA_ID}: Finished\r"
    wc -l $(ls -1 *.vcf) | awk 'BEGIN{FS=" "; print"Count,File";}{print $1","$2;}' > ${TCGA_ID}_total_counts.txt
    cd ..

done < "finished_tcga_ids.txt"

echo "Finished post-processing."
echo "-- Passing SNP Samples:   ${snp_chr_passed}"
echo "-- Passing Indel Samples: ${indel_chr_passed}"