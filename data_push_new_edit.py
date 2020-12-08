#package import
import pandas as pd
import time
from hashlib import sha256
from urllib.parse import quote_plus, urlencode
from hmac import HMAC
import requests
import hashlib
from base64 import b64encode, b64decode
import json
import os,sys
import serial
import pandas as pd
from datetime import datetime
# Temperature Sensor
'''BASE_DIR = '/sys/bus/w1/devices/'
SENSOR_DEVICE_ID = 'YOUR_DEVICE_ID'
'''
#DEVICE_FILE = 'records.csv'

# Azure IoT Hub
URI = 'nanoput.azure-devices.net'
KEY = 'vVZOy6HxrLG+hC1MKac6a/N5Tma2jUJBPjHVKA9yvWU='
IOT_DEVICE_ID = 'nanoputid'
POLICY = 'iothubowner'
arr = []
#recipient = "+919360990954"


#phone = serial.Serial("/dev/ttyUSB2",  115200, timeout=5)
now = datetime.now()
start = now.strftime('%H:%M:%S')

def generate_sas_token():
    expiry=3600
    ttl = time.time() + expiry
    sign_key = "%s\n%d" % ((quote_plus(URI)), int(ttl))
    signature = b64encode(HMAC(b64decode(KEY), sign_key.encode('utf-8'), sha256).digest())

    rawtoken = {
        'sr' :  URI,
        'sig': signature,
        'se' : str(int(ttl))
    }

    rawtoken['skn'] = POLICY


    return 'SharedAccessSignature ' + urlencode(rawtoken)


def read_temp():
    fine = pd.read_csv('sleep.csv')
    
    v1 = fine.iloc[-1, 0]
    v2 = fine.iloc[-1, 1]
    v3 = fine.iloc[-1, 2]
    v4 = fine.iloc[-1, 3]
    v5 = fine.iloc[-1, 4]
    return v1, v2, v3, v4, v5

def send_message(token, message):
    url = 'https://{0}/devices/{1}/messages/events?api-version=2016-11-14'.format(URI, IOT_DEVICE_ID)
    headers = {
        "Content-Type": "application/json",
        "Authorization": token
    }
    data = json.dumps(message)
    print(data)
    response = requests.post(url, data=data, headers=headers)
    print(response)

if __name__ == '__main__':
    # 1. Enable Temperature Sensor
#    os.system('modprobe w1-gpio')
#    os.system('modprobe w1-therm')

    # 2. Generate SAS Token
    token = generate_sas_token()

    # 3. Send Temperature to IoT Hub
    while True:
      try:
        v1, v2, v3, v4, v5 = read_temp() 
        message = {"drowsiness": str(v1),
                   "status1": str(v2),
                   "status2": str(v3),
                   "time": str(v4),
                   "edittime": str(v5)}                  
#        if v1 in arr:
#          print("already send data")
#          time.sleep(1)
#        if v1 not in arr:
#          arr.append(v1)
        send_message(token, message)
        time.sleep(1)

#        format = '%H:%M:%S'
#        now = datetime.now()
#        stop = now.strftime('%H:%M:%S')
#        print(stop)
#        condition = str('0:00:25')
#        val = str(datetime.strptime(stop, format) - datetime.strptime(start, format))
#        print("val {}".format(val))
#        if val >= condition:
#          sms = ("DRIVER MONITER\nDRIVING STRESS {}".format(v2))
#          print(message)
#          try:
#            phone.close()
#            time.sleep(0.5)
#            phone.open()
#            time.sleep(0.5)
#            phone.write(b'ATZ\r')
#            time.sleep(0.5)
#            phone.write(b'AT+CMGF=1\r')
#            time.sleep(0.5)
#            phone.write(b'AT+CMGS="' + recipient.encode() + b'"\r')
#            time.sleep(0.5)
#            phone.write(sms.encode() + b"\r")
#            time.sleep(0.5)
#            val = phone.write(bytes([26]))
#            print(val)
#            time.sleep(0.5)
#            print("send message..")
#            start = str(stop)
#          except:
#            phone.close()
#            print('stop')
#          finally:
#            phone.close()
#        else:
#          print("waiting..")
#          time.sleep(1)
      except Exception as e:
        print(e)
        sys.exit()
