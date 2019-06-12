#!/bin/bash

# ARGUMENTS
# 1. Normal Bam File Location (i.e. gs://my-bucket/my-bam.bam)
#   NOTE: In order to avoid sorting if bam is already sorted, the .bam.bai file should also be included there, with the same basename
# 2. Tumor Bam File Location (i.e. gs://my-bucket/my-bam.bam)
#   NOTE: In order to avoid sorting if bam is already sorted, the .bam.bai file should also be included there, with the same basename
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
    echo 'The pipeline script requires five arguments with an optional sixth:'
	echo "pipeline.h <gs://.../normal.bam> <gs://.../tumor.bam> <output bucket location (i.e. gs://my-bucket/output)> <output base name> <reference> <ip address of database>"
    exit 1
fi
if [[ $# -gt 6 ]] ; then
    echo 'The pipeline script requires five arguments with an optional sixth:'
	echo "pipeline.h <gs://.../normal.bam> <gs://.../tumor.bam> <output bucket location (i.e. gs://my-bucket/output)> <output base name> <reference> <ip address of database>"
    exit 1
fi

NORMAL_BAM=$(basename "$1")
TUMOR_BAM=$(basename "$2")
OUTPUT_LOCATION=$3
BASE_OUTPUT_NAME=$4
REFERENCE=$5
REFERENCE_NAME=$(basename "$5")
IP=$6


# Need to move the output here from ./output (?) to shared mount
# What is the prefix we should have so far?
# Don't need to use volumes since we're using buckets (???)
# 1. Create output directory based on patient ID / TCGA number
# 2. Copy appropriate files into that directory 

echo "Compressing VCF files...."
tar -zcf ${BASE_OUTPUT_NAME}.vcf.tar.gz *.vcf

# How to move into GS bucket?
# Where to move into bucket?

echo ""
echo "Copying files into the appropriate output location..."
gsutil cp ${BASE_OUTPUT_NAME}.vcf.tar.gz ${OUTPUT_LOCATION}varscan_results/
gsutil -m cp OUTPUT/* ${OUTPUT_LOCATION}varscan_results/OUTPUT/
gsutil cp ../*.std* ${OUTPUT_LOCATION}varscan_results/OUTPUT/


ERROR_FILES="${OUTPUT_LOCATION}varscan_results/OUTPUT/"
JSON_FINISHED="{\"Normal\":\"${NORMAL_BAM}\",\"Tumor\":\"${TUMOR_BAM}\",\"errorfiles\":\"${ERROR_FILES}\"}"
echo "============================================="
echo ${JSON_FINISHED} > OUTPUT/finished.txt
echo "FINISHED File:"
cat OUTPUT/finished.txt
echo ""
echo ""
if [[ ! -z "$6" ]]
then
    echo "POSTing job information ..."
    python post_json.py -u recordfinished -i ${IP} -f OUTPUT/finished.txt
fi
# Update Running Entry to finished
echo "{\"Normal\":\"${NORMAL_BAM}\",\"Tumor\":\"${TUMOR_BAM}\",\"Stage\":9,\"Reference\":\"${REFERENCE_NAME}\"}" > OUTPUT/running_entry.txt
if [[ ! -z "$6" ]]
then
    python post_json.py -u updaterunningsample -v -i ${IP} -f OUTPUT/running_entry.txt
fi
echo ""
echo "FINISHED!"

return 0