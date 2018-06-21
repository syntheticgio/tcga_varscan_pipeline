#!/usr/bin/env bash

#
# Sanity checking for number of arguments
#
if [[ $# -lt 6 ]] ; then
    echo 'The pipeline script requires five arguments:'
	echo "pipeline.h <gs://.../normal.bam> <gs://.../tumor.bam> <output bucket location (i.e. gs://my-bucket/output)> <output base name> <reference> <ip address of database>"
    exit 1
fi
if [[ $# -gt 6 ]] ; then
    echo 'The pipeline script requires five arguments:'
	echo "pipeline.h <gs://.../normal.bam> <gs://.../tumor.bam> <output bucket location (i.e. gs://my-bucket/output)> <output base name> <reference> <ip address of database>"
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
IP=$6

NORMAL_ID="${NORMAL_BAM%.*}"
TUMOR_ID="${TUMOR_BAM%.*}"

echo "\tNORMAL_BAM: ${NORMAL_BAM}"
echo "\tTUMOR_BAM: ${TUMOR_BAM}"
echo "\tOUTPUT_LOCATION: ${OUTPUT_LOCATION}"
echo "\tBASE_OUTPUT_NAME: ${BASE_OUTPUT_NAME}"
echo "\tREFERENCE: ${REFERENCE}"
echo ""
echo "\tNORMAL_ID: ${NORMAL_ID}"
echo "\tTUMOR_ID: ${TUMOR_ID}"

#
# Create OUTPUT directory, where everything should live for testing purposes
#
mkdir -p OUTPUT


#
# This is the base formating option that all tables take.  This assumes the beginning hasn't been defined yet
#
TIME_FORMAT="\"CommandLineArguments\":\"%C\",\"AvgSizeUnsharedDataArea_KBs\":\"%D\",\"ElapsedTime_s\":\"%E\",\"NumPageFaults\":\"%F\",\"NumFileSystemInputs\":\"%I\",\"AvgMemUse_KBs\":\"%K\",\"MaxResidentSetSize_KBs\":\"%M\",\"NumFileSystemOutputs\":\"%O\",\"CPU_Percent\":\"%P\",\"NumRecoverablePageFaults\":\"%R\",\"CPUUsedInKernelMode_s\":\"%S\",\"CPUUsedInUserMode_s\":\"%U\",\"TimesProcessSwappedOutOfMainMemory\":\"%W\",\"AverageAmountSharedText\":\"%X\",\"SystemPageSize_KBs\":\"%Z\",\"TimesProcessContextSwitched\":\"%c\",\"ElapsedRealTimeUsed_s\":\"%e\",\"NumSignalsDelivered\":\"%k\",\"AverageUnsharedStackSize_KBs\":\"%p\",\"NumSocketMessagesReceived\":\"%r\",\"NumSocketMessagesSent\":\"%s\",\"ResidentSetSize_KBs\":\"%t\",\"NumTimesContextSwitchedVoluntarily\":\"%w\",\"ExitStatus\":\"%x\"}"

# TODO : check to make sure that the stderr redirect doesn't capture time output also.

#
# Create the full format option for the SORT command - prepend sort specific string onto TIME_FORMAT
#
SORT_FORMAT="{\"ID\":\"${NORMAL_BAM}\",${TIME_FORMAT}"

#
# Run the SORT command for NORMAL and then submit the database
#
echo "samtools sort ${NORMAL_BAM} -o sorted_${NORMAL_BAM}"
/usr/bin/time -o OUTPUT/samtools_sort_normal_time.txt --format "${SORT_FORMAT}" samtools sort ${NORMAL_BAM} -o sorted_${NORMAL_BAM} 1> OUTPUT/samtools_sort_normal.stdout 2> OUTPUT/samtools_sort_normal.stderr
python test_post_json.py -u samtoolssort -f OUTPUT/samtools_sort_normal_time.txt -v -i ${IP}

#
# Run the SORT command for TUMOR and submit to the database
#

echo "samtools sort ${TUMOR_BAM} -o sorted_${TUMOR_BAM}"
/usr/bin/time -o OUTPUT/samtools_sort_tumor_time.txt --format "${SORT_FORMAT}" samtools sort ${TUMOR_BAM} -o sorted_${TUMOR_BAM} 1> OUTPUT/samtools_sort_tumor.stdout 2> OUTPUT/samtools_sort_tumor.stderr
python test_post_json.py -u samtoolssort -f OUTPUT/samtools_sort_tumor_time.txt -v -i ${IP}


#
# Determine MPILEUP time output format
#
MPILEUP_FORMAT="{\"NormalID\":\"${NORMAL_BAM}\",\"TumorID\":\"${TUMOR_BAM}\",\"Reference\":\"${REFERENCE}\",${TIME_FORMAT}"

#
# Run samtools mpileup
#
echo "/usr/bin/time -o OUTPUT/mpileup_time.txt --format "${MPILEUP_FORMAT}" samtools mpileup -f ${REFERENCE} -q 1 -B sorted_${NORMAL_BAM} sorted_${TUMOR_BAM} > intermediate_mpileup.pileup 2> OUTPUT/intermediate_mpileup.stderr"
#echo ""
#echo ""
/usr/bin/time -o OUTPUT/mpileup_time.txt --format "${MPILEUP_FORMAT}" \
    samtools mpileup \
	-f ${REFERENCE} \
	-q 1 \
	-B \
	sorted_${NORMAL_BAM} \
	sorted_${TUMOR_BAM} \
	1> \
	intermediate_mpileup.pileup \
	2> OUTPUT/intermediate_mpileup.stderr
python test_post_json.py -u mpileup -f OUTPUT/mpileup_time.txt -v -i ${IP}

#
# Get base somatic mutations
#

SOMATIC_FORMAT="{\"NormalID\":\"${NORMAL_BAM}\",\"TumorID\":\"${TUMOR_BAM}\",\"Reference\":\"${REFERENCE}\",${TIME_FORMAT}"
echo "Running VarScan Somatic..."
echo ""
/usr/bin/time -o OUTPUT/somatic_varscan_time.txt --format "${SOMATIC_FORMAT}" \
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

python test_post_json.py -u varscansomatic -f OUTPUT/somatic_varscan_time.txt -v -i ${IP}

#
# Process for somatic SNPs
#
/usr/bin/time -o OUTPUT/process_somatic_snp_time.txt --format "${SOMATIC_FORMAT}" \
    java -jar varscan/VarScan.jar processSomatic \
	${BASE_OUTPUT_NAME}.snp.vcf \
	--min-tumor-freq 0.10 \
	--max-normal-freq 0.05 \
	--p-value 0.07

python test_post_json.py -u varscanprocesssomaticsnps -f OUTPUT/process_somatic_snp_time.txt -v -i ${IP}

#
# Process for somatic indels
#
/usr/bin/time -o OUTPUT/process_somatic_indel_time.txt --format "${SOMATIC_FORMAT}" \
    java -jar varscan/VarScan.jar processSomatic \
	${BASE_OUTPUT_NAME}.indel.vcf \
	--min-tumor-freq 0.10 \
	--max-normal-freq 0.05 \
	--p-value 0.07

python test_post_json.py -u varscanprocesssomaticindels -f OUTPUT/process_somatic_indel_time.txt -v -i ${IP}
