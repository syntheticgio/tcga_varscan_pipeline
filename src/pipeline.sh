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

echo ""
echo -e "\tNORMAL_BAM: ${NORMAL_BAM}"
echo -e "\tTUMOR_BAM: ${TUMOR_BAM}"
echo -e "\tOUTPUT_LOCATION: ${OUTPUT_LOCATION}"
echo -e "\tBASE_OUTPUT_NAME: ${BASE_OUTPUT_NAME}"
echo -e "\tREFERENCE: ${REFERENCE}"
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
# Stage 1
#
echo "{\"Normal\":\"${NORMAL_BAM}\",\"Tumor\":\"${TUMOR_BAM}\",\"Stage\":1}" > OUTPUT/running_entry.txt
python post_json.py -u createrunningsample -v -i ${IP} -f OUTPUT/running_entry.txt
echo "=========================================================="
echo "1. SORTING:  /usr/bin/time -o OUTPUT/samtools_sort_normal_time.txt --format "${SORT_FORMAT}" ${SAMTOOLS} sort ${NORMAL_BAM} -o sorted_${NORMAL_BAM} 1> OUTPUT/samtools_sort_normal.stdout 2> OUTPUT/samtools_sort_normal.stderr"
/usr/bin/time -o OUTPUT/samtools_sort_normal_time.txt --format "${SORT_FORMAT}" ${SAMTOOLS} sort ${NORMAL_BAM} -o sorted_${NORMAL_BAM} 1> OUTPUT/samtools_sort_normal.stdout 2> OUTPUT/samtools_sort_normal.stderr
SORT_NORMAL_ERROR_CODE=$?
echo -e "\tERROR CODE: ${SORT_NORMAL_ERROR_CODE}"
echo ""
echo "2. POSTing time data to database: python post_json.py -u samtoolssort -f OUTPUT/samtools_sort_normal_time.txt -v -i ${IP}"
python post_json.py -u samtoolssort -f OUTPUT/samtools_sort_normal_time.txt -v -i ${IP}
POST_NORMAL_ERROR_CODE=$?
echo -e "\tERROR CODE: ${POST_NORMAL_ERROR_CODE}"
echo ""
echo "STDERR"
echo "------"
cat OUTPUT/samtools_sort_normal.stderr
echo "=========================================================="

#
# Run the SORT command for TUMOR and submit to the database
# Stage 2
#
echo "{\"Normal\":\"${NORMAL_BAM}\",\"Tumor\":\"${TUMOR_BAM}\",\"Stage\":2}" > OUTPUT/running_entry.txt
python post_json.py -u updaterunningsample -v -i ${IP} -f OUTPUT/running_entry.txt

echo ""
echo "3. SORTING: /usr/bin/time -o OUTPUT/samtools_sort_tumor_time.txt --format "${SORT_FORMAT}" ${SAMTOOLS} sort ${TUMOR_BAM} -o sorted_${TUMOR_BAM} 1> OUTPUT/samtools_sort_tumor.stdout 2> OUTPUT/samtools_sort_tumor.stderr"
/usr/bin/time -o OUTPUT/samtools_sort_tumor_time.txt --format "${SORT_FORMAT}" ${SAMTOOLS} sort ${TUMOR_BAM} -o sorted_${TUMOR_BAM} 1> OUTPUT/samtools_sort_tumor.stdout 2> OUTPUT/samtools_sort_tumor.stderr
SORT_TUMOR_ERROR_CODE=$?
echo -e "\tERROR CODE: ${SORT_TUMOR_ERROR_CODE}"
echo ""
echo "4. POSTing time data to database: python post_json.py -u samtoolssort -f OUTPUT/samtools_sort_tumor_time.txt -v -i ${IP}"
python post_json.py -u samtoolssort -f OUTPUT/samtools_sort_tumor_time.txt -v -i ${IP}
POST_TUMOR_ERROR_CODE=$?
echo -e "\tERROR CODE: ${POST_TUMOR_ERROR_CODE}"
echo ""
echo "STDERR"
echo "------"
cat OUTPUT/samtools_sort_tumor.stderr
echo "=========================================================="

#
# Determine MPILEUP time output format
#
MPILEUP_FORMAT="{\"NormalID\":\"${NORMAL_BAM}\",\"TumorID\":\"${TUMOR_BAM}\",\"Reference\":\"${REFERENCE}\",${TIME_FORMAT}"

#
# Run samtools mpileup
# Stage 3
#
echo "{\"Normal\":\"${NORMAL_BAM}\",\"Tumor\":\"${TUMOR_BAM}\",\"Stage\":3}" > OUTPUT/running_entry.txt
python post_json.py -u updaterunningsample -v -i ${IP} -f OUTPUT/running_entry.txt
echo ""
echo "5. MPILEUP: /usr/bin/time -o OUTPUT/mpileup_time.txt --format ${MPILEUP_FORMAT} ${SAMTOOLS} mpileup -f ${REFERENCE} -q 1 -B sorted_${NORMAL_BAM} sorted_${TUMOR_BAM} 1> intermediate_mpileup.pileup 2> OUTPUT/intermediate_mpileup.stderr"
/usr/bin/time -o OUTPUT/mpileup_time.txt --format "${MPILEUP_FORMAT}" \
    ${SAMTOOLS} mpileup \
	-f ${REFERENCE} \
	-q 1 \
	-B \
	sorted_${NORMAL_BAM} \
	sorted_${TUMOR_BAM} \
	1> \
	intermediate_mpileup.pileup \
	2> OUTPUT/intermediate_mpileup.stderr
MPILEUP_ERROR_CODE=$?
echo -e "\tERROR CODE: ${MPILEUP_ERROR_CODE}"
echo ""
echo "6. POSTing mpileup: python post_json.py -u mpileup -f OUTPUT/mpileup_time.txt -v -i ${IP}"
python post_json.py -u mpileup -f OUTPUT/mpileup_time.txt -v -i ${IP}
POST_MPILEUP_ERROR_CODE=$?
echo -e "\tERROR CODE: ${POST_MPILEUP_ERROR_CODE}"
echo ""
echo "STDERR"
echo "------"
cat OUTPUT/intermediate_mpileup.stderr
echo "=========================================================="

#
# Get base somatic mutations
# Stage 4
#
echo "{\"Normal\":\"${NORMAL_BAM}\",\"Tumor\":\"${TUMOR_BAM}\",\"Stage\":4}" > OUTPUT/running_entry.txt
python post_json.py -u updaterunningsample -v -i ${IP} -f OUTPUT/running_entry.txt
SOMATIC_FORMAT="{\"NormalID\":\"${NORMAL_BAM}\",\"TumorID\":\"${TUMOR_BAM}\",\"Reference\":\"${REFERENCE}\",${TIME_FORMAT}"
echo ""
echo "7. VARSCAN SOMATIC: /usr/bin/time -o OUTPUT/somatic_varscan_time.txt --format ${SOMATIC_FORMAT} java -jar varscan/VarScan.jar somatic intermediate_mpileup.pileup ${BASE_OUTPUT_NAME} --mpileup 1 --min-coverage 8 --min-coverage-normal 8 --min-coverage-tumor 6 --min-var-freq 0.10 --min-freq-for-hom 0.75 --normal-purity 1.0 --tumor-purity 1.00 --p-value 0.99 --somatic-p-value 0.05 --strand-filter 0 --output-vcf 2> OUTPUT/varscan_somatic.stderr"
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
	--output-vcf \
	2> OUTPUT/varscan_somatic.stderr
VARSCAN_ERROR_CODE=$?
echo -e "\tERROR CODE: ${VARSCAN_ERROR_CODE}"
echo ""
echo "8. POSTing varscan: python post_json.py -u varscansomatic -f OUTPUT/somatic_varscan_time.txt -v -i ${IP}"
python post_json.py -u varscansomatic -f OUTPUT/somatic_varscan_time.txt -v -i ${IP}
POST_VARSCAN_ERROR_CODE=$?
echo -e "\tERROR CODE: ${POST_VARSCAN_ERROR_CODE}"
echo ""
echo "STDERR"
echo "------"
cat OUTPUT/varscan_somatic.stderr
echo "=========================================================="

#
# Process for somatic SNPs
# Stage 5
#
echo "{\"Normal\":\"${NORMAL_BAM}\",\"Tumor\":\"${TUMOR_BAM}\",\"Stage\":5}" > OUTPUT/running_entry.txt
python post_json.py -u updaterunningsample -v -i ${IP} -f OUTPUT/running_entry.txt
echo ""
echo "9. VARSCAN SOMATIC SNP CALLS: /usr/bin/time -o OUTPUT/process_somatic_snp_time.txt --format ${SOMATIC_FORMAT}java -jar varscan/VarScan.jar processSomatic ${BASE_OUTPUT_NAME}.snp.vcf --min-tumor-freq 0.10 --max-normal-freq 0.05 --p-value 0.07 2> varscan_somatic_snp.stderr"
/usr/bin/time -o OUTPUT/process_somatic_snp_time.txt --format "${SOMATIC_FORMAT}" \
    java -jar varscan/VarScan.jar processSomatic \
	${BASE_OUTPUT_NAME}.snp.vcf \
	--min-tumor-freq 0.10 \
	--max-normal-freq 0.05 \
	--p-value 0.07 \
	2> varscan_somatic_snp.stderr
VARSCAN_SNP_ERROR_CODE=$?
echo -e "\tERROR CODE: ${VARSCAN_SNP_ERROR_CODE}"
echo ""
echo "10. POSTing VARSCAN SNP: python post_json.py -u varscanprocesssomaticsnps -f OUTPUT/process_somatic_snp_time.txt -v -i ${IP}"
python post_json.py -u varscanprocesssomaticsnps -f OUTPUT/process_somatic_snp_time.txt -v -i ${IP}
POST_VARSCAN_SNP_ERROR_CODE=$?
echo -e "\tERROR CODE: ${POST_VARSCAN_SNP_ERROR_CODE}"
echo ""
echo "STDERR"
echo "------"
cat OUTPUT/varscan_somatic_snp.stderr
echo "=========================================================="

#
# Process for somatic indels
# Stage 6
#
echo "{\"Normal\":\"${NORMAL_BAM}\",\"Tumor\":\"${TUMOR_BAM}\",\"Stage\":6}" > OUTPUT/running_entry.txt
python post_json.py -u updaterunningsample -v -i ${IP} -f OUTPUT/running_entry.txt
echo ""
echo "11. VARSCAN SOMATIC INDEL CALLS: /usr/bin/time -o OUTPUT/process_somatic_indel_time.txt --format ${SOMATIC_FORMAT} java -jar varscan/VarScan.jar processSomatic ${BASE_OUTPUT_NAME}.indel.vcf --min-tumor-freq 0.10 --max-normal-freq 0.05 --p-value 0.07 2> OUTPUT/varscan_somatic_indel.stderr"
/usr/bin/time -o OUTPUT/process_somatic_indel_time.txt --format "${SOMATIC_FORMAT}" \
    java -jar varscan/VarScan.jar processSomatic \
	${BASE_OUTPUT_NAME}.indel.vcf \
	--min-tumor-freq 0.10 \
	--max-normal-freq 0.05 \
	--p-value 0.07 \
	2> OUTPUT/varscan_somatic_indel.stderr
VARSCAN_INDEL_ERROR_CODE=$?
echo -e "\tERROR CODE: ${VARSCAN_INDEL_ERROR_CODE}"
echo ""
echo "12. POSTing VARSCAN INDEL: python post_json.py -u varscanprocesssomaticindels -f OUTPUT/process_somatic_indel_time.txt -v -i ${IP}"
python post_json.py -u varscanprocesssomaticindels -f OUTPUT/process_somatic_indel_time.txt -v -i ${IP}
POST_VARSCAN_INDEL_ERROR_CODE=$?
echo -e "\tERROR CODE: ${POST_VARSCAN_INDEL_ERROR_CODE}"
echo ""
echo "STDERR"
echo "------"
cat OUTPUT/varscan_somatic_indel.stderr
echo "=========================================================="


# Need to move the output here from ./output (?) to shared mount
# What is the prefix we should have so far?
# Don't need to use volumes since we're using buckets (???)
# 1. Create output directory based on patient ID / TCGA number
# 2. Copy appropriate files into that directory 

#mv ..indel                  ..indel.Germline.vcf  ..indel.LOH.vcf         ..indel.Somatic.vcf  ..snp                  ..snp.Germline.vcf  ..snp.LOH.vcf         ..snp.Somatic.vcf
#..indel.Germline.hc.vcf  ..indel.LOH.hc.vcf    ..indel.Somatic.hc.vcf  ..indel.vcf          ..snp.Germline.hc.vcf  ..snp.LOH.hc.vcf    ..snp.Somatic.hc.vcf  ..snp.vcf

# Stage 7
echo "{\"Normal\":\"${NORMAL_BAM}\",\"Tumor\":\"${TUMOR_BAM}\",\"Stage\":7}" > OUTPUT/running_entry.txt
python post_json.py -u updaterunningsample -v -i ${IP} -f OUTPUT/running_entry.txt

echo ""
echo "Compressing VCF files...."
tar -zcf ${BASE_OUTPUT_NAME}.vcf.tar.gz *.vcf

# How to move into GS bucket?
# Where to move into bucket?

echo ""
echo "Copying files into the appropriate output location..."
gsutil cp ${BASE_OUTPUT_NAME}*.vcf.gz ${OUTPUT_LOCATION}/varscan_results/
gsutil cp OUTPUT/* ${OUTPUT_LOCATION}/varscan_results/${BASE_OUTPUT_NAME}/


ERROR_FILES="${OUTPUT_LOCATION}/varscan_results/${BASE_OUTPUT_NAME}/"
JSON_FINISHED="{\"Normal\":${NORMAL_BAM},\"Tumor\":${TUMOR_BAM},\"errorfiles\":${ERROR_FILES},\"SortNormalError\":${SORT_NORMAL_ERROR_CODE},\"PostSortNormalError\":${POST_NORMAL_ERROR_CODE},\"SortTumorError\":${SORT_TUMOR_ERROR_CODE},\"PostSortTumorError\":${POST_TUMOR_ERROR_CODE},\"MpileupError\":${MPILEUP_ERROR_CODE},\"PostMpileupError\":${POST_MPILEUP_ERROR_CODE},\"VarscanError\":${VARSCAN_ERROR_CODE},\"PostVarscanError\":${POST_VARSCAN_ERROR_CODE},\"VarscanSnpError\":${VARSCAN_SNP_ERROR_CODE},\"PostVarscanSnpError\":${POST_VARSCAN_SNP_ERROR_CODE},\"VarscanIndelError\":${VARSCAN_INDEL_ERROR_CODE},\"PostVarscanIndelError\":${POST_VARSCAN_INDEL_ERROR_CODE}}"
echo "============================================="
echo ${JSON_FINISHED} > OUTPUT/finished.txt
echo "FINISHED File:"
cat OUTPUT/finished.txt
echo ""
echo ""
echo "POSTing job information ..."
python post_json.py -u recordfinished -i ${IP} -f OUTPUT/finished.txt
# Update Running Entry to finished
echo "{\"Normal\":\"${NORMAL_BAM}\",\"Tumor\":\"${TUMOR_BAM}\",\"Stage\":9}" > OUTPUT/running_entry.txt
python post_json.py -u updaterunningsample -v -i ${IP} -f OUTPUT/running_entry.txt
echo ""
echo "FINISHED!"
