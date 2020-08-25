#!/usr/bin/env bash

# ARGUMENTS
# 1. Normal Bam File Location (BAI index should also be in same location)
# 2. Tumor Bam File Location (BAI index should also be in same location)
# 3. Output Location
#   This is where the output from the pipeline should be copied to (i.e. gs://my-bucket/output/)
# 4. Base Output Name
#	The basename for the output files (i.e. my-output)
# 5. Reference
#	The location of the reference file
# 6. IP address if the server for keeping logs

#
# Sanity checking for number of arguments
#
if [[ $# -lt 5 ]] ; then
    echo 'The pipeline script requires five arguments with an optional sixth one:'
	echo "pipeline.h </path/to/normal.bam> </path/to/tumor.bam> <output bucket location (i.e. gs://my-bucket/output)> <output base name> <reference> <[optional] ip address of database>"
    exit 1
fi
if [[ $# -gt 6 ]] ; then
    echo 'The pipeline script requires five arguments with an optional sixth:'
	echo "pipeline.h </path/to/normal.bam> </path/to/tumor.bam> <output bucket location (i.e. gs://my-bucket/output)> <output base name> <reference> <[optional] ip address of database>"
    exit 1
fi

#
# Help script
#
if [[ $1 == "-h" ]]; then
	echo "Help"
	echo "-------------"
	echo "pipeline.h </path/to/normal.bam> </path/to/tumor.bam> <output bucket location (i.e. gs://my-bucket/output)> <output base name> <reference> <[optional] ip address of database>"
	echo ""
	echo "Output location should have the complete gs:// path up to (but excluding) the file name"
	exit 1
fi

# SET VARIABLES

# The normal and tumor bam and bai files should have been downloaded
# by the split_by_ref.sh script
NORMAL_BAM=$(basename "$1")
TUMOR_BAM=$(basename "$2")
OUTPUT_LOCATION=$3
BASE_OUTPUT_NAME=$4
REFERENCE=$5
REFERENCE_NAME=$(basename "$5")
# Check to see if reference file exists
if [[ ! -e "${5}" ]]; then
	echo "Error, Reference file not found..."
	exit 7
fi
IP=$6
NORMAL_ID="${NORMAL_BAM%.*}"
TUMOR_ID="${TUMOR_BAM%.*}"

MODIFIED_NORMAL="sorted_${NORMAL_ID}.REF_${REFERENCE_NAME%.*}.bam"
MODIFIED_TUMOR="sorted_${TUMOR_ID}.REF_${REFERENCE_NAME%.*}.bam"

echo ""
echo -e "\tNORMAL_BAM: ${MODIFIED_NORMAL}"
echo -e "\tTUMOR_BAM: ${MODIFIED_TUMOR}"
echo -e "\tOUTPUT_LOCATION: ${OUTPUT_LOCATION}"
echo -e "\tBASE_OUTPUT_NAME: ${BASE_OUTPUT_NAME}"
echo -e "\tREFERENCE: ${REFERENCE}"
echo -e "\tREFERENCE NAME: ${REFERENCE_NAME}"
echo -e "\tIP: ${IP}"
echo ""
echo -e "\tNORMAL_ID: ${NORMAL_ID}"
echo -e "\tTUMOR_ID: ${TUMOR_ID}"
echo ""
/samtools/bin/samtools --version
echo ""

SAMTOOLS="/samtools/bin/samtools"

#
# Create OUTPUT directory, where everything should live for testing purposes
#
mkdir -p OUTPUT


#
# This is the base formatting option that all tables take in the database.  This assumes the beginning hasn't been defined yet
#
TIME_FORMAT="\"CommandLineArguments\":\"%C\",\"AvgSizeUnsharedDataArea_KBs\":\"%D\",\"ElapsedTime_s\":\"%E\",\"NumPageFaults\":\"%F\",\"NumFileSystemInputs\":\"%I\",\"AvgMemUse_KBs\":\"%K\",\"MaxResidentSetSize_KBs\":\"%M\",\"NumFileSystemOutputs\":\"%O\",\"CPU_Percent\":\"%P\",\"NumRecoverablePageFaults\":\"%R\",\"CPUUsedInKernelMode_s\":\"%S\",\"CPUUsedInUserMode_s\":\"%U\",\"TimesProcessSwappedOutOfMainMemory\":\"%W\",\"AverageAmountSharedText\":\"%X\",\"SystemPageSize_KBs\":\"%Z\",\"TimesProcessContextSwitched\":\"%c\",\"ElapsedRealTimeUsed_s\":\"%e\",\"NumSignalsDelivered\":\"%k\",\"AverageUnsharedStackSize_KBs\":\"%p\",\"NumSocketMessagesReceived\":\"%r\",\"NumSocketMessagesSent\":\"%s\",\"ResidentSetSize_KBs\":\"%t\",\"NumTimesContextSwitchedVoluntarily\":\"%w\",\"ExitStatus\":\"%x\"}"

# TODO : check to make sure that the stderr redirect doesn't capture time output also.

######################################################
# Stages 1 and 2 were completed in the split_by_ref.sh
######################################################

######################################################
# Determine MPILEUP time output format
######################################################
MPILEUP_FORMAT="{\"NormalID\":\"${NORMAL_BAM}\",\"TumorID\":\"${TUMOR_BAM}\",\"Reference\":\"${REFERENCE}\",${TIME_FORMAT}"

######################################################
# Run samtools mpileup
# Stage 3
######################################################
# TODO: Need to update here to have the sorted_*BAM files with the proper _REF_xxx appended
echo "{\"Normal\":\"${NORMAL_BAM}\",\"Tumor\":\"${TUMOR_BAM}\",\"Stage\":3,\"Reference\":\"${REFERENCE_NAME}\"}" > OUTPUT/running_entry.txt

python post_json.py -u createrunningsample -v -i "${IP}" -f OUTPUT/running_entry.txt 2> "__createsample_${REFERENCE_NAME}_post.stderr"

echo ""
MPILEUP_OUTPUT_NAME="intermediate_mpileup.${REFERENCE_NAME}.pileup"
MPILEUP_OUTPUT_STDERR="intermediate_mpileup.${REFERENCE_NAME}.stderr"
MPILEUP_OUTPUT_TIME="mpileup_time.${REFERENCE_NAME}.txt"
echo "5. MPILEUP: /usr/bin/time -o OUTPUT/${MPILEUP_OUTPUT_TIME} --format ${MPILEUP_FORMAT} ${SAMTOOLS} mpileup -f ${REFERENCE} -q 1 -B sorted_${NORMAL_BAM} sorted_${TUMOR_BAM} 1> ${MPILEUP_OUTPUT_NAME} 2> OUTPUT/${MPILEUP_OUTPUT_STDERR}"
/usr/bin/time -o OUTPUT/"${MPILEUP_OUTPUT_TIME}" --format "${MPILEUP_FORMAT}" \
    ${SAMTOOLS} mpileup \
	-f "${REFERENCE}" \
	-q 1 \
	-B \
	sorted_"${NORMAL_BAM}" \
	sorted_"${TUMOR_BAM}" \
	1> \
	"${MPILEUP_OUTPUT_NAME}" \
	2> OUTPUT/"${MPILEUP_OUTPUT_STDERR}"
MPILEUP_ERROR_CODE=$?
echo -e "\tERROR CODE: ${MPILEUP_ERROR_CODE}"
echo ""

echo "6. POSTing mpileup: python post_json.py -u mpileup -f OUTPUT/${MPILEUP_OUTPUT_TIME} -v -i ${IP}"
python post_json.py -u mpileup -f OUTPUT/"${MPILEUP_OUTPUT_TIME}" -v -i "${IP}" 2> "__mpileup_${REFERENCE_NAME}_post.stderr"
POST_MPILEUP_ERROR_CODE=$?
echo -e "\tERROR CODE: ${POST_MPILEUP_ERROR_CODE}"
echo ""

echo "STDERR"
echo "------"
cat OUTPUT/"${MPILEUP_OUTPUT_STDERR}"
echo "=========================================================="

######################################################
# Get base somatic mutations
# Stage 4
######################################################
BASE_OUTPUT_NAME="${BASE_OUTPUT_NAME}_${REFERENCE_NAME%.*}"
VARSCAN_SOMATIC_STDERR="varscan_somatic_${REFERENCE_NAME%.*}.stderr"
VARSCAN_SOMATIC_TIME="somatic_varscan_time_${REFERENCE_NAME%.*}.txt"
echo "{\"Normal\":\"${NORMAL_BAM}\",\"Tumor\":\"${TUMOR_BAM}\",\"Stage\":4,\"Reference\":\"${REFERENCE_NAME}\"}" > OUTPUT/running_entry.txt
python post_json.py -u updaterunningsample -v -i "${IP}" -f OUTPUT/running_entry.txt 2> "__update1_${REFERENCE_NAME}_post.stderr"
SOMATIC_FORMAT="{\"NormalID\":\"${NORMAL_BAM}\",\"TumorID\":\"${TUMOR_BAM}\",\"Reference\":\"${REFERENCE}\",${TIME_FORMAT}"
echo ""
echo "7. VARSCAN SOMATIC: /usr/bin/time -o OUTPUT/${VARSCAN_SOMATIC_TIME} --format ${SOMATIC_FORMAT} java -jar /varscan/varscan/VarScan.jar somatic ${MPILEUP_OUTPUT_NAME} ${BASE_OUTPUT_NAME} --mpileup 1 --min-coverage 8 --min-coverage-normal 8 --min-coverage-tumor 6 --min-var-freq 0.10 --min-freq-for-hom 0.75 --normal-purity 1.0 --tumor-purity 1.00 --p-value 0.99 --somatic-p-value 0.05 --strand-filter 0 --output-vcf 2> OUTPUT/${VARSCAN_SOMATIC_STDERR}"
/usr/bin/time -o OUTPUT/"${VARSCAN_SOMATIC_TIME}" --format "${SOMATIC_FORMAT}" \
    java -jar /varscan/varscan/VarScan.jar somatic \
	"${MPILEUP_OUTPUT_NAME}" \
	"${BASE_OUTPUT_NAME}" \
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
	--output-vcf \
	2> OUTPUT/"${VARSCAN_SOMATIC_STDERR}"
VARSCAN_ERROR_CODE=$?
echo -e "\tERROR CODE: ${VARSCAN_ERROR_CODE}"
echo ""

echo "8. POSTing varscan: python post_json.py -u varscansomatic -f OUTPUT/${VARSCAN_SOMATIC_TIME} -v -i ${IP}"
python post_json.py -u varscansomatic -f OUTPUT/"${VARSCAN_SOMATIC_TIME}" -v -i "${IP}" 2> "__varscansomatic_${REFERENCE_NAME}_post.stderr"
POST_VARSCAN_ERROR_CODE=$?
echo -e "\tERROR CODE: ${POST_VARSCAN_ERROR_CODE}"
echo ""

echo "STDERR"
echo "------"
cat OUTPUT/"${VARSCAN_SOMATIC_STDERR}"
echo "=========================================================="

######################################################
# Process for somatic SNPs
# Stage 5
######################################################
VARSCAN_SOMATIC_SNP_TIME="process_somatic_snp_time_${REFERENCE_NAME%.*}.txt"
VARSCAN_SOMATIC_SNP_STDERR="process_somatic_snp_${REFERENCE_NAME%.*}.stderr"
echo "{\"Normal\":\"${NORMAL_BAM}\",\"Tumor\":\"${TUMOR_BAM}\",\"Stage\":5,\"Reference\":\"${REFERENCE_NAME}\"}" > OUTPUT/running_entry.txt
python post_json.py -u updaterunningsample -v -i "${IP}" -f OUTPUT/running_entry.txt 2> "__update2_${REFERENCE_NAME}_post.stderr"
echo ""
echo "9. VARSCAN SOMATIC SNP CALLS: /usr/bin/time -o OUTPUT/${VARSCAN_SOMATIC_SNP_TIME} --format ${SOMATIC_FORMAT}java -jar /varscan/varscan/VarScan.jar processSomatic ${BASE_OUTPUT_NAME}.snp.vcf --min-tumor-freq 0.10 --max-normal-freq 0.05 --p-value 0.07 2> ${VARSCAN_SOMATIC_SNP_STDERR}"
/usr/bin/time -o OUTPUT/"${VARSCAN_SOMATIC_SNP_TIME}" --format "${SOMATIC_FORMAT}" \
    java -jar /varscan/varscan/VarScan.jar processSomatic \
	"${BASE_OUTPUT_NAME}".snp.vcf \
	--min-tumor-freq 0.10 \
	--max-normal-freq 0.05 \
	--p-value 0.07 \
	2> OUTPUT/"${VARSCAN_SOMATIC_SNP_STDERR}"
VARSCAN_SNP_ERROR_CODE=$?
echo -e "\tERROR CODE: ${VARSCAN_SNP_ERROR_CODE}"
echo ""

echo "10. POSTing VARSCAN SNP: python post_json.py -u varscanprocesssomaticsnps -f OUTPUT/${VARSCAN_SOMATIC_SNP_TIME} -v -i ${IP}"
python post_json.py -u varscanprocesssomaticsnps -f OUTPUT/"${VARSCAN_SOMATIC_SNP_TIME}" -v -i "${IP}" 2> "__varscanprocesssomaticsnps_${REFERENCE_NAME}_post.stderr"
POST_VARSCAN_SNP_ERROR_CODE=$?
echo -e "\tERROR CODE: ${POST_VARSCAN_SNP_ERROR_CODE}"
echo ""

echo "STDERR"
echo "------"
cat OUTPUT/"${VARSCAN_SOMATIC_SNP_STDERR}"
echo "=========================================================="

######################################################
# Process for somatic indels
# Stage 6
######################################################
VARSCAN_SOMATIC_INDEL_TIME="process_somatic_indel_time_${REFERENCE_NAME%.*}.txt"
VARSCAN_SOMATIC_INDEL_STDERR="process_somatic_indel_${REFERENCE_NAME%.*}.stderr"
echo "{\"Normal\":\"${NORMAL_BAM}\",\"Tumor\":\"${TUMOR_BAM}\",\"Stage\":6,\"Reference\":\"${REFERENCE_NAME}\"}" > OUTPUT/running_entry.txt
python post_json.py -u updaterunningsample -v -i "${IP}" -f OUTPUT/running_entry.txt 2> "__update3_${REFERENCE_NAME}_post.stderr"
echo ""
echo "11. VARSCAN SOMATIC INDEL CALLS: /usr/bin/time -o OUTPUT/${VARSCAN_SOMATIC_INDEL_TIME} --format ${SOMATIC_FORMAT} java -jar /varscan/varscan/VarScan.jar processSomatic ${BASE_OUTPUT_NAME}.indel.vcf --min-tumor-freq 0.10 --max-normal-freq 0.05 --p-value 0.07 2> OUTPUT/${VARSCAN_SOMATIC_INDEL_STDERR}"
/usr/bin/time -o OUTPUT/"${VARSCAN_SOMATIC_INDEL_TIME}" --format "${SOMATIC_FORMAT}" \
    java -jar /varscan/varscan/VarScan.jar processSomatic \
	"${BASE_OUTPUT_NAME}".indel.vcf \
	--min-tumor-freq 0.10 \
	--max-normal-freq 0.05 \
	--p-value 0.07 \
	2> OUTPUT/"${VARSCAN_SOMATIC_INDEL_STDERR}"
VARSCAN_INDEL_ERROR_CODE=$?
echo -e "\tERROR CODE: ${VARSCAN_INDEL_ERROR_CODE}"
echo ""

echo "12. POSTing VARSCAN INDEL: python post_json.py -u varscanprocesssomaticindels -f OUTPUT/${VARSCAN_SOMATIC_INDEL_TIME} -v -i ${IP}"
python post_json.py -u varscanprocesssomaticindels -f OUTPUT/"${VARSCAN_SOMATIC_INDEL_TIME}" -v -i "${IP}" 2> "__varscanprocesssomaticindels_${REFERENCE_NAME}_post.stderr"
POST_VARSCAN_INDEL_ERROR_CODE=$?
echo -e "\tERROR CODE: ${POST_VARSCAN_INDEL_ERROR_CODE}"
echo ""

echo "STDERR"
echo "------"
cat OUTPUT/"${VARSCAN_SOMATIC_INDEL_STDERR}"
echo "=========================================================="

#############################################
# Finished with this leg
#############################################

echo "{\"Normal\":\"${NORMAL_BAM}\",\"Tumor\":\"${TUMOR_BAM}\",\"Stage\":7,\"Reference\":\"${REFERENCE_NAME}\"}" > OUTPUT/running_entry.txt

python post_json.py -u updaterunningsample -v -i "${IP}" -f OUTPUT/running_entry.txt 2> "__update4_${REFERENCE_NAME}_post.stderr"

return 0