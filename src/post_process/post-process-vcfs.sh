#!/bin/bash

TCGA_IDS=`gsutil ls gs://iron-eye-6998/tcga_wgs_results | awk 'BEGIN{FS="/";}{if (NR > 1) {print $5;}}'`

for TCGA_ID in ${TCGA_IDS}; do
    mkdir -p ${TCGA_ID}
    cp generate_bar_graphs.rscript ${TCGA_ID}/
    pushd .
    cd ${TCGA_ID}
    gsutil cp gs://iron-eye-6998/tcga_wgs_results/${TCGA_ID}/varscan_results/*.gz .
    
    tar zxvf *.gz
    rm *.gz
    wc -l $(ls -1 *.snp.vcf) | awk '{gsub("_", " "); print $0;}' | awk 'BEGIN{FS=" "; print"Count,TCGA,Chrom";}{gsub(".snp.vcf", " "); if($2 != "total"){gsub("chr", "", $3); print $1","$2","$3;}}' | sort -k 3,3 -n -t "," > snps_by_chrom.csv
    wc -l $(ls -1 *.indel.vcf) | awk '{gsub("_", " "); print $0;}' | awk 'BEGIN{FS=" "; print"Count,TCGA,Chrom";}{gsub(".indel.vcf", " "); if($2 != "total"){gsub("chr", "", $3); print $1","$2","$3;}}' | sort -k 3,3 -n -t "," > indels_by_chrom.csv
    Rscript generate_bar_graphs.rscript
    rm generate_bar_graphs.rscript
    vcf-concat $(ls -1 *.snp.vcf | perl -pe 's/\n/ /g') > ${TCGA_ID}.all.snp.vcf
    vcf-concat $(ls -1 *.indel.vcf | perl -pe 's/\n/ /g') > ${TCGA_ID}.all.indel.vcf
    rm *chr*.vcf ## Leave us just with the all snp and indel vcfs
    java -jar /varscan/varscan/VarScan.jar processSomatic \
        "${TCGA_ID}".all.snp.vcf \
        --min-tumor-freq 0.10 \
        --max-normal-freq 0.05 \
        --p-value 0.07
    java -jar /varscan/varscan/VarScan.jar processSomatic \
        "${TCGA_ID}".all.indel.vcf \
        --min-tumor-freq 0.10 \
        --max-normal-freq 0.05 \
        --p-value 0.07
    # Get total counts for indels and SNPs - can be used in QA with the above barplots
    wc -l $(ls -1 *.vcf) | awk 'BEGIN{FS=" "; print"Count,File";}{print $1","$2;}' > ${TCGA_ID}_total_counts.txt

done