import requests
import argparse
import json


class DatabasePoster:
    def __init__(self):
        pass

    def PostData(self, url, wgs_data):
        r = requests.post(url, data=json.dumps(wgs_data))
        print("POSTed data, return value: {}".format(r.status_code))



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

    # parser.add_argument('--sitl', '-s', dest='sitl', action='store_true', help='Turns on the software in a loop')
    #
    # parser.add_argument('--latitude', '-lat', dest='latitude', default="38.7509000",
    #                     help='This is the latitude the drone should be created at, if using a SITL simulation.  By default this will be in Manassas Va')
    # parser.add_argument('--longitude', '-lon', dest='longitude', default="-77.4753000",
    #                     help='This is the longitude the drone should be created at, if using a SITL simulation.  By default this will be in Manassas Va')

    args = parser.parse_args()

    url = 'http://127.0.0.1/' + args.url + '/'

    if args.url == 'samtoolssort':
        if args.verbose:
            print("Posting to the SamtoolsSort Databse.")
    elif args.url == 'mpileup':
        if args.verbose:
            print("Posting to the MpileUp database.")
    elif args.url == 'varscansomatic':
        if args.verbose:
            print("Posting to the VarscanSomatic database.")
    elif args.url == 'varscanprocesssomaticsnps':
        if args.verbose:
            print("Posting to the VarscanProcessSomaticSnps database.")
    elif args.url == 'varscanprocesssomaticindels':
        if args.verbose:
            print("Posting to the VarscanProcesssomaticIndels database.")
    else:
        if args.verbose:
            print("Posting to the test database.")
        url = 'http://127.0.0.1/test/'

    test_data = {
        'CommandLineArguments': 'value1',
        'AvgSizeUnsharedDataArea_KBs': 'value2',
        'ElapsedTime_s': 'value',
        'NumPagesFaults': 'value',
        'NumFileSystemInputs': 'value',
        'AvgMemUse_KBs': 'value',
        'MaxResidentSetSize_KBs': 'value',
        'NumFileSystemOutputs': 'value',
        'CPU_Percent': 'value',
        'NumRecoverablePageFaults': 'value',
        'CPUUsedInKernelMode_s': 'value',
        'CPUUsedInUserMode_s': 'value',
        'TimesProcessSwappedOutOfMainMemory': 'value',
        'AverageAmountSharedText': 'value',
        'SystemPageSize_KBs': 'value',
        'TimesProcessContextSwitched': 'value',
        'ElapsedRealTimeUsed_s': 'value',
        'NumSignalsDelivered': 'value',
        'AverageUnsharedStackSize_KBs': 'value',
        'NumSocketMessagesReceived': 'value',
        'NumSocketMessagesSent': 'value',
        'ResidentSetSize_KBs': 'value',
        'NumTimesContextSwitchedVoluntarily': 'value',
        'ExitStatus': 'value'
    }

    dp = DatabasePoster()
    dp.PostData(url, test_data)
