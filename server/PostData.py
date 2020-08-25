# Poster helper methods
import requests
import json


def PostData(wgs_url, wgs_data):
    try:
        r = requests.post(wgs_url, data=json.dumps(wgs_data))
        print("POSTed data, return value: {}".format(r.status_code))
        print("POSTed data, return : {}".format(r.text))
    except requests.exceptions.ConnectionError as e:
        print("ERROR: %e", e)
        print("Note: This is most likely due to a CTRL+C call on the server, or the server otherwise has been shut "
              "down.")
