#!/usr/bin/env bash

# ARGUMENTS
# 1. Normal Bam File Location
# 2. Tumor Bam File Location
# 3. IP address if the server for keeping logs

#
# Sanity checking for number of arguments
#
if [[ $# -lt 2 ]]; then
  echo 'The pipeline script requires two arguments with an optional third one:'
  echo "pipeline.h <normal.bam> <tumor.bam> <ip address of database>"
  exit 1
fi
if [[ $# -gt 3 ]]; then
  echo 'The pipeline script requires two arguments with an optional third one:'
  echo "pipeline.h <normal.bam> <tumor.bam> <ip address of database>"
  exit 1
fi

#
# Help output
#
if [[ $1 == "-h" ]]; then
  echo "Help"
  echo "-------------"
  echo "split_by_ref.h <normal.bam> <tumor.bam> <ip address of database>"
  echo ""
  exit 1
fi

# Check to make sure files are copied and exist
NORMAL_BAM=$(basename "$1")
TUMOR_BAM=$(basename "$2")

if [[ -e "${NORMAL_BAM}.bai" ]]; then
  NORMAL_SORTED=0
else
  NORMAL_SORTED=1
  echo "NORMAL BAM INDEX DOESN'T EXIST"
fi

# Check to see if tumor bam index exists to skip sorting
if [[ -e "${TUMOR_BAM}.bai" ]]; then
  TUMOR_SORTED=0
else
  TUMOR_SORTED=1
  echo "TUMOR BAM INDEX DOESN'T EXIST"
fi

if [[ -z "$3" ]]; then
  echo "No argument supplied for server."
fi

mkdir -p OUTPUT
if [[ $? -gt 0 ]]; then
  directory=$(pwd)
  echo "Error creating the output directory.  Make sure you have permissions to create ${directory}/OUTPUT"
  exit 5
fi

#NORMAL_ID="${NORMAL_BAM%.*}"
#TUMOR_ID="${TUMOR_BAM%.*}"

SAMTOOLS="/samtools/bin/samtools"

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
# Only run if the bai index is not included
# Stage 1
#
echo "{\"Normal\":\"${NORMAL_BAM}\",\"Tumor\":\"${TUMOR_BAM}\",\"Stage\":1,\"Reference\":\"Human\"}" >OUTPUT/running_entry.txt

python post_json.py -u createrunningsample -v -i "${3}" -f OUTPUT/running_entry.txt

##
## TODO: Change to faster algorithm
##
echo "=========================================================="
echo "1. SORTING:  /usr/bin/time -o OUTPUT/samtools_sort_normal_time.txt --format ${SORT_FORMAT} ${SAMTOOLS} sort -@ 8 ${NORMAL_BAM} -o sorted_${NORMAL_BAM} 1> OUTPUT/samtools_sort_normal.stdout 2> OUTPUT/samtools_sort_normal.stderr"
if [[ ${NORMAL_SORTED} -gt 0 ]]; then
  echo "Normal Not yet sorted, sorting now..."
  /usr/bin/time -o OUTPUT/samtools_sort_normal_time.txt --format "${SORT_FORMAT}" ${SAMTOOLS} sort -@ 8 "${NORMAL_BAM}" -o sorted_"${NORMAL_BAM}" 1>OUTPUT/samtools_sort_normal.stdout 2>OUTPUT/samtools_sort_normal.stderr
  rm "${NORMAL_BAM}"
  SORT_NORMAL_ERROR_CODE=$?
  echo -e "\tERROR CODE: ${SORT_NORMAL_ERROR_CODE}"
else
  echo "Already sorted.  Simulating stdout and stderr for logging."
  ln -s "${NORMAL_BAM}" sorted_"${NORMAL_BAM}"
  ln -s "${NORMAL_BAM}".bai sorted_"${NORMAL_BAM}".bai

  # Make simulated time output file for submission
  /usr/bin/time -o OUTPUT/samtools_sort_normal_time.txt --format "${SORT_FORMAT}" ls 1>OUTPUT/samtools_sort_normal.stdout 2>OUTPUT/samtools_sort_normal.stderr
  SORT_NORMAL_ERROR_CODE=$?
  echo -e "\tERROR CODE: ${SORT_NORMAL_ERROR_CODE}"
fi

echo ""
echo "2. POSTing time data to database: python post_json.py -u samtoolssort -f OUTPUT/samtools_sort_normal_time.txt -v -i ${3}"

python post_json.py -u samtoolssort -f OUTPUT/samtools_sort_normal_time.txt -v -i "${3}"

POST_NORMAL_ERROR_CODE=$?
echo -e "\tERROR CODE: ${POST_NORMAL_ERROR_CODE}"
echo ""
echo "STDERR"
echo "------"
cat OUTPUT/samtools_sort_normal.stderr
echo "=========================================================="

# Make sure chromosome names are the same...
/samtools/bin/samtools view -H sorted_"${NORMAL_BAM}" >header.sam
awk -f re_chrom_name.awk header.sam >new_header.sam
# TODO: Conditional seems to not quite have worked, but this should be fast anyway
#if [[ $? -gt 0 ]]; then
${SAMTOOLS} reheader -iP new_header.sam sorted_"${NORMAL_BAM}" >_tmp
mv _tmp sorted_"${NORMAL_BAM}"
#fi

# Get BAMSTATS
${SAMTOOLS} flagstat -@ 8 sorted_"${NORMAL_BAM}" >OUTPUT/_"${NORMAL_BAM}"_flagstat.txt &
NORMAL_SAMTOOLS_PID=$!
java -jar -Xmx8g /BAMStats-1.25/BAMStats-1.25.jar -i sorted_"${NORMAL_BAM}" >OUTPUT/_"${NORMAL_BAM}"_bamstats.txt &
NORMAL_BAMSTATS_PID=$!

#
# Split based on reference
# Not threaded :(
bamtools split -in sorted_"${NORMAL_BAM}" -reference &
NORMAL_SPLIT_PID=$!

#
# Run the SORT command for TUMOR and submit to the database
# Stage 2
#
echo "{\"Normal\":\"${NORMAL_BAM}\",\"Tumor\":\"${TUMOR_BAM}\",\"Stage\":2,\"Reference\":\"Human\"}" >OUTPUT/running_entry.txt

python post_json.py -u updaterunningsample -v -i "${3}" -f OUTPUT/running_entry.txt

echo ""
echo "3. SORTING: /usr/bin/time -o OUTPUT/samtools_sort_tumor_time.txt --format ${SORT_FORMAT} ${SAMTOOLS} sort -@ 8 ${TUMOR_BAM} -o sorted_${TUMOR_BAM} 1> OUTPUT/samtools_sort_tumor.stdout 2> OUTPUT/samtools_sort_tumor.stderr"
if [[ ${TUMOR_SORTED} -gt 0 ]]; then
  echo "Tumor not yet sorted, sorting now..."
  /usr/bin/time -o OUTPUT/samtools_sort_tumor_time.txt --format "${SORT_FORMAT}" ${SAMTOOLS} sort -@ 8 "${TUMOR_BAM}" -o sorted_"${TUMOR_BAM}" 1>OUTPUT/samtools_sort_tumor.stdout 2>OUTPUT/samtools_sort_tumor.stderr
  rm "${TUMOR_BAM}"
  SORT_TUMOR_ERROR_CODE=$?
  echo -e "\tERROR CODE: ${SORT_TUMOR_ERROR_CODE}"
else
  echo "Already sorted.  Simulating stdout and stderr for logging."
  ln -s "${TUMOR_BAM}" sorted_"${TUMOR_BAM}"
  ln -s "${TUMOR_BAM}".bai sorted_"${TUMOR_BAM}".bai

  /usr/bin/time -o OUTPUT/samtools_sort_tumor_time.txt --format "${SORT_FORMAT}" ls 1>OUTPUT/samtools_sort_tumor.stdout 2>OUTPUT/samtools_sort_tumor.stderr
  SORT_TUMOR_ERROR_CODE=$?
  echo -e "\tERROR CODE: ${SORT_TUMOR_ERROR_CODE}"
fi

echo ""
echo "4. POSTing time data to database: python post_json.py -u samtoolssort -f OUTPUT/samtools_sort_tumor_time.txt -v -i ${3}"

python post_json.py -u samtoolssort -f OUTPUT/samtools_sort_tumor_time.txt -v -i "${3}"

POST_TUMOR_ERROR_CODE=$?
echo -e "\tERROR CODE: ${POST_TUMOR_ERROR_CODE}"
echo ""
echo "STDERR"
echo "------"
cat OUTPUT/samtools_sort_tumor.stderr
echo "=========================================================="

# Make sure chromosome names are the same...
/samtools/bin/samtools view -H sorted_"${TUMOR_BAM}" >header.sam
awk -f re_chrom_name.awk header.sam >new_header.sam
${SAMTOOLS} reheader -iP new_header.sam sorted_"${TUMOR_BAM}" > _tmp
mv _tmp sorted_"${TUMOR_BAM}"

# BAMSTAT
${SAMTOOLS} flagstat -@ 8 sorted_"${TUMOR_BAM}" >OUTPUT/_"${TUMOR_BAM}"_flagstat.txt &
TUMOR_SAMTOOLS_PID=$!
java -jar -Xmx8g /BAMStats-1.25/BAMStats-1.25.jar -i sorted_"${TUMOR_BAM}" >OUTPUT/_"${TUMOR_BAM}"_bamstats.txt &
TUMOR_BAMSTATS_PID=$!

#
# Split based on reference
# Not threaded
bamtools split -in sorted_"${TUMOR_BAM}" -reference &
TUMOR_SPLIT_PID=$!

##
## TODO: This could be done much nicer - move to python script
##
echo "Waiting on NORMAL SAMTOOLS"
wait ${NORMAL_SAMTOOLS_PID}
echo "Waiting on NORMAL BAMSTAT"
wait ${NORMAL_BAMSTATS_PID}
echo "Waiting on NORMAL SPLIT"
wait ${NORMAL_SPLIT_PID}
echo "Waiting on TUMOR SAMTOOLS"
wait ${TUMOR_SAMTOOLS_PID}
echo "Waiting on TUMOR BAMSTAT"
wait ${TUMOR_BAMSTATS_PID}
echo "Waiting on TUMOR SPLIT"
wait ${TUMOR_SPLIT_PID}

echo "{\"Normal\":\"${NORMAL_BAM}\",\"Tumor\":\"${TUMOR_BAM}\",\"Stage\":9,\"Reference\":\"Human\"}" >OUTPUT/running_entry.txt

python post_json.py -u updaterunningsample -v -i "${3}" -f OUTPUT/running_entry.txt
