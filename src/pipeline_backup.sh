#!/bin/bash

# Pipeline for Varscan in GDC

#
# Sanity checking for number of arguments
#
if [[ $# -lt 4 ]] ; then
    echo 'The pipeline script requires four arguments:'
	echo "pipeline.h <gs://.../normal.bam> <gs://.../tumor.bam> <gs://.../reference.fa> <output bucket location (i.e. gs://my-bucket/output)>"
    exit 1
fi
if [[ $# -gt 4 ]] ; then
    echo 'The pipeline script requires four arguments:'
	echo "pipeline.h <gs://.../normal.bam> <gs://.../tumor.bam> <gs://.../reference.fa> <output bucket location (i.e. gs://my-bucket/output)>"
    exit 1
fi

#
# Help script
#
if [[ $1 == "-h" ]]; then
	echo "Help"
	echo "-------------"
	echo "pipeline.h <gs://.../normal.bam> <gs://.../tumor.bam> <gs://.../reference.fa> <output bucket location (i.e. gs://my-bucket/output)>"
	echo ""
	echo "The files should be locations the container can access; this script is set up to accept accessible gs:// locations and copy them in using gsutil."
	echo "For example: gs://my-bucket/normal.bam"
	exit 1
fi

#
# Set variables based on user passed in data
#
NORMAL_BAM=$1
TUMOR_BAM=$2
REFERENCE=$3
OUTPUT_LOCATION=$4

#
# Copy data over from apporpriate gs bucket (as passed in by user)
#
gsutil cp ${NORMAL_BAM} .
gsutil cp ${TUMOR_BAM} .
gsutil cp ${REFERENCE} .

#
# Get new local file names from the paths (gs bucket paths)
#
NORMAL_BAM=$(basename "$NORMAL_BAM")
TUMOR_BAM=$(basename "$TUMOR_BAM")
REFERENCE=$(basename "$REFERENCE")

#
# Run samtools sorting on both of the bam files
#
/samtools/bin/bin/samtools sort ${NORMAL_BAM} sorted_${NORMAL_BAM}
/samtools/bin/bin/samtools sort ${TUMOR_BAM} sorted_${TUMOR_BAM}

#
# Run samtools mpileup
#
/samtools/bin/bin/samtools mpileup \
	-f ${REFERENCE} \
	-q 1 \
	-B \
	sorted_${NORMAL_BAM} \
	sorted_${TUMOR_BAM} \
	> \
	intermediate_mpileup.pileup

#
# Get base somatic mutations
#
java -jar varscan/VarScan.jar somatic \
	intermediate_mpileup.pileup \
	. \
	--mpileup      1 \
	--min-coverage 8 \
	--min-coverage-normal 8 \
	--min-coverage-tumor 6 \
	--min-var-freq 0.10 \
	--min-freq-for-hom 0.75 \
	--normal-purity 1.0 \
	--tumor-purity 1.00 \
	--p-value 0.99 \
	--somatic-p-value 0.05 \
	--strand-filter 0 \
	--output-vcf

#
# Process for somatic SNPs
#
java -jar varscan/VarScan.jar processSomatic \
	..snp.vcf \
	--min-tumor-freq 0.10 \
	--max-normal-freq 0.05 \
	--p-value 0.07
	
#
# Process for somatic indels
#
java -jar varscan/VarScan.jar processSomatic \
	..indel.vcf \
	--min-tumor-freq 0.10 \
	--max-normal-freq 0.05 \
	--p-value 0.07
	
# Need to move the output here from ./output (?) to shared mount
# What is the prefix we should have so far?
# Don't need to use volumes since we're using buckets (???)
# 1. Create output directory based on patient ID / TCGA number
# 2. Copy appropriate files into that directory (rename here?)

#mv ..indel                  ..indel.Germline.vcf  ..indel.LOH.vcf         ..indel.Somatic.vcf  ..snp                  ..snp.Germline.vcf  ..snp.LOH.vcf         ..snp.Somatic.vcf
#..indel.Germline.hc.vcf  ..indel.LOH.hc.vcf    ..indel.Somatic.hc.vcf  ..indel.vcf          ..snp.Germline.hc.vcf  ..snp.LOH.hc.vcf    ..snp.Somatic.hc.vcf  ..snp.vcf

