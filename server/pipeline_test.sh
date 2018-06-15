#!/usr/bin/env bash

OUTPUT_FORMAT="{\"CommandLineArguments\":\"%C\",\"AvgSizeUnsharedDataArea_KBs\": \"%D\",\"ElapsedTime_s\": \"%E\",\"NumPageFaults\": \"%F\",\"NumFileSystemInputs\": \"%I\",\"AvgMemUse_KBs\": \"%K\",\"MaxResidentSetSize_KBs\": \"%M\",\"NumFileSystemOutputs\": \"%O\",\"CPU_Percent\": \"%P\",\"NumRecoverablePageFaults\": \"%R\",\"CPUUsedInKernelMode_s\": \"%S\",\"CPUUsedInUserMode_s\": \"%U\",\"TimesProcessSwappedOutOfMainMemory\": \"%W\",\"AverageAmountSharedText\": \"%X\",\"SystemPageSize_KBs\": \"%Z\",\"TimesProcessContextSwitched\": \"%c\",\"ElapsedRealTimeUsed_s\": \"%e\",\"NumSignalsDelivered\": \"%k\",\"AverageUnsharedStackSize_KBs\": \"%p\",\"NumSocketMessagesReceived\": \"%r\",\"NumSocketMessagesSent\": \"%s\",\"ResidentSetSize_KBs\": \"%t\",\"NumTimesContextSwitchedVoluntarily\": \"%w\",\"ExitStatus\": \"%x\"}"

{ /usr/bin/time --format "${OUTPUT_FORMAT}" sleep 5 ; } 2> time.txt

python test_post_json.py -u samtoolssort -f time.txt -v
