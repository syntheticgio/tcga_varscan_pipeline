#!/bin/bash

# Pipeline for Varscan in GDC

#
# Sanity checking for number of arguments
#
if [[ $# -lt 5 ]] ; then
    echo 'The pipeline script requires five arguments:'
	echo "pipeline.h <gs://.../normal.bam> <gs://.../tumor.bam> <output bucket location (i.e. gs://my-bucket/output)> <output base name> <reference>"
    exit 1
fi
if [[ $# -gt 5 ]] ; then
    echo 'The pipeline script requires five arguments:'
	echo "pipeline.h <gs://.../normal.bam> <gs://.../tumor.bam> <output bucket location (i.e. gs://my-bucket/output)> <output base name> <reference>"
    exit 1
fi

#
# Help script
#
if [[ $1 == "-h" ]]; then
	echo "Help"
	echo "-------------"
	echo "pipeline.h <gs://.../normal.bam> <gs://.../tumor.bam> <output bucket location (i.e. gs://my-bucket/output)> <output base name> <reference>"
	echo ""
	echo "The files should be locations the container can access; this script is set up to accept accessible gs:// locations and copy them in using gsutil."
	echo "For example: gs://my-bucket/normal.bam"
	echo "Output location should have the complete gs:// path up to (but excluding) the file name"
	echo "The reference will be autodetected for sequence IDs (chr1 vs 1); Hg19 build"
	exit 1
fi

#
# Set variables based on user passed in data
#
NORMAL_BAM=$1
TUMOR_BAM=$2
OUTPUT_LOCATION=$3
BASE_OUTPUT_NAME=$4
REFERENCE=$5

#
# Get new local file names from the paths (gs bucket paths)
#
#NORMAL_BAM=$(basename "$NORMAL_BAM")
#TUMOR_BAM=$(basename "$TUMOR_BAM")
#REFERENCE=""

#
# Determine reference, using either chr1 or 1
#
#_REF=`/samtools/bin/bin/samtools view ${TUMOR_BAM} | head -n1 | awk '{print $3;}'`
#if [[ ${_REF} == "chr1" ]]; then
#	REFERENCE="gs://iron-eye-6998/references/reference_chr.fa"
#else
#	REFERENCE="gs://iron-eye-6998/references/reference.fa"
#fi

#
# Get reference file name
#
#REFERENCE=$(basename "$REFERENCE")

#
# Run samtools sorting on both of the bam files
#
# IN VERSION ON XPS this requires -o for output file
# Get time: { time <command> 2> cmmd.stderr ; } 2> time.txt

OUTPUT_FORMAT="{\"CommandLineArguments\":\"%C\",\"AvgSizeUnsharedDataArea_KBs\": \"%D\",\"ElapsedTime_s\": \"%E\",\"NumPageFaults\": \"%F\",\"NumFileSystemInputs\": \"%I\",\"AvgMemUse_KBs\": \"%K\",\"MaxResidentSetSize_KBs\": \"%M\",\"NumFileSystemOutputs\": \"%O\",\"CPU_Percent\": \"%P\",\"NumRecoverablePageFaults\": \"%R\",\"CPUUsedInKernelMode_s\": \"%S\",\"CPUUsedInUserMode_s\": \"%U\",\"TimesProcessSwappedOutOfMainMemory\": \"%W\",\"AverageAmountSharedText\": \"%X\",\"SystemPageSize_KBs\": \"%Z\",\"TimesProcessContextSwitched\": \"%c\",\"ElapsedRealTimeUsed_s\": \"%e\",\"NumSignalsDelivered\": \"%k\",\"AverageUnsharedStackSize_KBs\": \"%p\",\"NumSocketMessagesReceived\": \"%r\",\"NumSocketMessagesSent\": \"%s\",\"ResidentSetSize_KBs\": \"%t\",\"NumTimesContextSwitchedVoluntarily\": \"%w\",\"ExitStatus\": \"%x\"}"

# TODO : check to make sure that the stderr redirect doesn't capture time output also.

{ /usr/bin/time --format "${OUTPUT_FORMAT}" /samtools/bin/bin/samtools sort ${NORMAL_BAM} -o sorted_${NORMAL_BAM} 1> samtools_sort_normal.stdout 2> samtools_sort_normal.stderr ; } 2> samtools_sort_normal_time.txt

{ /usr/bin/time --format "${OUTPUT_FORMAT}" /samtools/bin/bin/samtools sort ${TUMOR_BAM} -o sorted_${TUMOR_BAM} 1> samtools_sort_tumor.stdout 2> samtools_sort_tumor.stderr ; } 2> samtools_sort_tumor_time.txt

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
	${BASE_OUTPUT_NAME} \
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
	${BASE_OUTPUT_NAME}.snp.vcf \
	--min-tumor-freq 0.10 \
	--max-normal-freq 0.05 \
	--p-value 0.07 
	
#
# Process for somatic indels
#
java -jar varscan/VarScan.jar processSomatic \
	${BASE_OUTPUT_NAME}.indel.vcf \
	--min-tumor-freq 0.10 \
	--max-normal-freq 0.05 \
	--p-value 0.07
	
# Need to move the output here from ./output (?) to shared mount
# What is the prefix we should have so far?
# Don't need to use volumes since we're using buckets (???)
# 1. Create output directory based on patient ID / TCGA number
# 2. Copy appropriate files into that directory 

#mv ..indel                  ..indel.Germline.vcf  ..indel.LOH.vcf         ..indel.Somatic.vcf  ..snp                  ..snp.Germline.vcf  ..snp.LOH.vcf         ..snp.Somatic.vcf
#..indel.Germline.hc.vcf  ..indel.LOH.hc.vcf    ..indel.Somatic.hc.vcf  ..indel.vcf          ..snp.Germline.hc.vcf  ..snp.LOH.hc.vcf    ..snp.Somatic.hc.vcf  ..snp.vcf

mv ${BASE_OUTPUT_NAME}*.vcf ${OUTPUT_LOCATION}/
