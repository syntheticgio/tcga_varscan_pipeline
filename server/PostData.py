# Poster helper methods
import requests
import json


def PostData(wgs_url, wgs_data):
    r = requests.post(wgs_url, data=json.dumps(wgs_data))
    print("POSTed data, return value: {}".format(r.status_code))
    print("POSTed data, return : {}".format(r.text))
