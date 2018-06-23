import requests
import argparse
import json


def PostData(wgs_url, wgs_data):
    r = requests.post(wgs_url, data=json.dumps(wgs_data))
    print("POSTed data, return value: {}".format(r.status_code))
    print("POSTed data, return : {}".format(r.text))


def ReadDataFromFile(file_handle):
    print("Json file to open: {}".format(file_handle))
    with open(file_handle) as json_file:
        data = json.load(json_file)
        return data

# url = 'http://127.0.0.1/samtoolssort/'
# payload = {
#     'CommandLineArguments': 'value1',
#     'AvgSizeUnsharedDataArea_KBs': 'value2',
#     'ElapsedTime_s': 'value',
#     'NumPagesFaults': 'value',
#     'NumFileSystemInputs': 'value',
#     'AvgMemUse_KBs': 'value',
#     'MaxResidentSetSize_KBs': 'value',
#     'NumFileSystemOutputs': 'value',
#     'CPU_Percent': 'value',
#     'NumRecoverablePageFaults': 'value',
#     'CPUUsedInKernelMode_s': 'value',
#     'CPUUsedInUserMode_s': 'value',
#     'TimesProcessSwappedOutOfMainMemory': 'value',
#     'AverageAmountSharedText': 'value',
#     'SystemPageSize_KBs': 'value',
#     'TimesProcessContextSwitched': 'value',
#     'ElapsedRealTimeUsed_s': 'value',
#     'NumSignalsDelivered': 'value',
#     'AverageUnsharedStackSize_KBs': 'value',
#     'NumSocketMessagesReceived': 'value',
#     'NumSocketMessagesSent': 'value',
#     'ResidentSetSize_KBs': 'value',
#     'NumTimesContextSwitchedVoluntarily': 'value',
#     'ExitStatus': 'value'
# }
#
# print("Beginning requests")
# # GET
# r = requests.get(url)
# print("GET, no params: {}".format(r))
#
# # GET with params in URL
# r = requests.get(url, params=payload)
# print("GET, with params: {}".format(r.text))
#
# # POST with form-encoded data
# # r = requests.post(url, data=payload)
# # print("POST, form-encoded data: {}".format(r.text))
#
# # POST with JSON
# import json
# r = requests.post(url, data=json.dumps(payload))
# print("POST, with JSON: {}".format(r.text))
#
# # Response, status etc
# r.text
# r.status_code


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Commands for the POSTer.')
    parser.add_argument('--verbose', '-v', dest='verbose', action='store_true', help="Turns on verbosity.")
    parser.add_argument('--url', '-u', dest='url', default="samtoolssort", help='Determines the URL to post to.')
    parser.add_argument('--file', '-f', dest='file', help='File to read data from.')
    parser.add_argument('--ip', '-i', dest='ip', help='The IP address of the database.')

    args = parser.parse_args()

    if args.ip:
        url = 'http://' + args.ip + '/' + args.url + '/'
    else:
        url = 'http://127.0.0.1/' + args.url + '/'
    args.verbose = True
    if args.url == 'samtoolssort':
        if args.verbose:
            print("Posting to the SamtoolsSort table.")
    elif args.url == 'mpileup':
        if args.verbose:
            print("Posting to the MpileUp table.")
    elif args.url == 'varscansomatic':
        if args.verbose:
            print("Posting to the VarscanSomatic table.")
    elif args.url == 'varscanprocesssomaticsnps':
        if args.verbose:
            print("Posting to the VarscanProcessSomaticSnps table.")
    elif args.url == 'varscanprocesssomaticindels':
        if args.verbose:
            print("Posting to the VarscanProcesssomaticIndels table.")
    elif args.url == 'recordfinished':
        if args.verbose:
            print("Posting to the FinishedSamples table.")
    elif args.url == 'createrunningsample':
        if args.verbose:
            print("Adding to the RunningSample table.")
    elif args.url == 'updaterunningsample':
        if args.verbose:
            print("Updating the RunningSample table.")
    elif args.url == 'removerunningsample':
        if args.verbose:
            print("Removing from the RunningSample table.")
    elif args.url == 'rawdata':
        if args.verbose:
            print("Getting raw data.")
    else:
        if args.verbose:
            print("Posting to the test database.")
        url = 'http://127.0.0.1/test/'

    post_data = ReadDataFromFile(args.file)
    print(post_data)
    # print(args)

    # test_data = {
    #     'CommandLineArguments': '\"samtools sort -b test.sam > test.bam\"',
    #     'AvgSizeUnsharedDataArea_KBs': 56854,
    #     'ElapsedTime_s': "\"365898\"",
    #     'NumPageFaults': 7,
    #     'NumFileSystemInputs': 12,
    #     'AvgMemUse_KBs': 1526,
    #     'MaxResidentSetSize_KBs': 1625,
    #     'NumFileSystemOutputs': 10,
    #     'CPU_Percent': '\"3%\"',
    #     'NumRecoverablePageFaults': 1425,
    #     'CPUUsedInKernelMode_s': 9283.2345,
    #     'CPUUsedInUserMode_s': 7483.332,
    #     'TimesProcessSwappedOutOfMainMemory': 92,
    #     'AverageAmountSharedText': 2416,
    #     'SystemPageSize_KBs': 4026,
    #     'TimesProcessContextSwitched': 42,
    #     'ElapsedRealTimeUsed_s': 293.25,
    #     'NumSignalsDelivered': 62,
    #     'AverageUnsharedStackSize_KBs': 72,
    #     'NumSocketMessagesReceived': 73,
    #     'NumSocketMessagesSent': 92,
    #     'ResidentSetSize_KBs': 15,
    #     'NumTimesContextSwitchedVoluntarily': 51,
    #     'ExitStatus': 0
    # }

    # GET with params in URL
    # r = requests.get(url, params=test_data)
    # print("GET, with params: {}".format(r.text))

    print("Data to be posted: {}".format(post_data))
    PostData(url, post_data)
