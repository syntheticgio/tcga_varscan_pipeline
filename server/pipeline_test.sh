#!/usr/bin/env bash

NORMAL_BAM=$1
echo $NORMAL_BAM
# OUTPUT_FORMAT="{\"CommandLineArguments\":\"%C\",\"AvgSizeUnsharedDataArea_KBs\": \"%D\",\"ElapsedTime_s\": \"%E\",\"NumPageFaults\": \"%F\",\"NumFileSystemInputs\": \"%I\",\"AvgMemUse_KBs\": \"%K\",\"MaxResidentSetSize_KBs\": \"%M\",\"NumFileSystemOutputs\": \"%O\",\"CPU_Percent\": \"%P\",\"NumRecoverablePageFaults\": \"%R\",\"CPUUsedInKernelMode_s\": \"%S\",\"CPUUsedInUserMode_s\": \"%U\",\"TimesProcessSwappedOutOfMainMemory\": \"%W\",\"AverageAmountSharedText\": \"%X\",\"SystemPageSize_KBs\": \"%Z\",\"TimesProcessContextSwitched\": \"%c\",\"ElapsedRealTimeUsed_s\": \"%e\",\"NumSignalsDelivered\": \"%k\",\"AverageUnsharedStackSize_KBs\": \"%p\",\"NumSocketMessagesReceived\": \"%r\",\"NumSocketMessagesSent\": \"%s\",\"ResidentSetSize_KBs\": \"%t\",\"NumTimesContextSwitchedVoluntarily\": \"%w\",\"ExitStatus\": \"%x\"}"
TIME_FORMAT="\"CommandLineArguments\":\"%C\",\"AvgSizeUnsharedDataArea_KBs\": \"%D\",\"ElapsedTime_s\": \"%E\",\"NumPageFaults\": \"%F\",\"NumFileSystemInputs\": \"%I\",\"AvgMemUse_KBs\": \"%K\",\"MaxResidentSetSize_KBs\": \"%M\",\"NumFileSystemOutputs\": \"%O\",\"CPU_Percent\": \"%P\",\"NumRecoverablePageFaults\": \"%R\",\"CPUUsedInKernelMode_s\": \"%S\",\"CPUUsedInUserMode_s\": \"%U\",\"TimesProcessSwappedOutOfMainMemory\": \"%W\",\"AverageAmountSharedText\": \"%X\",\"SystemPageSize_KBs\": \"%Z\",\"TimesProcessContextSwitched\": \"%c\",\"ElapsedRealTimeUsed_s\": \"%e\",\"NumSignalsDelivered\": \"%k\",\"AverageUnsharedStackSize_KBs\": \"%p\",\"NumSocketMessagesReceived\": \"%r\",\"NumSocketMessagesSent\": \"%s\",\"ResidentSetSize_KBs\": \"%t\",\"NumTimesContextSwitchedVoluntarily\": \"%w\",\"ExitStatus\": \"%x\"}"

# TODO : check to make sure that the stderr redirect doesn't capture time output also.
SORT_FORMAT="{\"ID\":\"${NORMAL_BAM}\",${TIME_FORMAT}"
mkdir -p OUTPUT
/usr/bin/time -o OUTPUT/samtools_sort_normal_time.txt --format "${SORT_FORMAT}" samtools sort ${NORMAL_BAM} -o OUTPUT/sorted_${NORMAL_BAM} 1> OUTPUT/samtools_sort_normal.stdout 2> OUTPUT/samtools_sort_normal.stderr

python test_post_json.py -u samtoolssort -f OUTPUT/samtools_sort_normal_time.txt -v
