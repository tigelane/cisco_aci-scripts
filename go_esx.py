#!/usr/bin/env python

import _LabEnv
import json
import requests
import sys

SPARK_ROOM_ID = None

def main():
    get_room()
    post_room()

def get_room():
    r = requests.get(_LabEnv.SPARK_API_ROOMS, headers=_LabEnv.SPARK_HEADERS, verify=False) j = json.loads(r.text)
    for tmproom in j['items']:
        if tmproom['title'] == _LabEnv.SPARK_ROOM_NAME:
            SPARK_ROOM_ID = tmproom['id']
            print("Found room ID for '" + _LabEnv.SPARK_ROOM_NAME + "' : " + SPARK_ROOM_ID) 
            break


def post_room():
    m = json.dumps({'roomId':SPARK_ROOM_ID,'text':'Hi '+_LabEnv.LAB_SESSION+' this is '+_LabEnv.LAB_USER})
    r = requests.post(_LabEnv.SPARK_API_MESSAGES, data=m, headers=_LabEnv.SPARK_HEADERS, verify=False) print('Spark Response: ' + r.text)

    print r

if __name__ == '__main__':
    main(sys.argv)