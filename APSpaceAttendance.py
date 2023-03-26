import logging
import configparser
import os
import platform
import time
import numpy as np
import pyautogui
import pygetwindow
from cv2 import cv2
import requests
from bs4 import BeautifulSoup
import json

# DO NOT EDIT #
Config = configparser.ConfigParser()
Config.read("config.ini")
attendix_url = Config.get('ENDPOINTS', 'APSpaceURL')
apkey = Config.get('APKEY', 'APKey')
apkey_password = Config.get('APKEY', 'APKeyPassword')
oncompletion_config = Config.get('OPTIONS', 'ON_COMPLETION')
onfail_config = Config.get('OPTIONS', 'ON_FAIL')

max_attempts = Config.get('OPTIONS', 'MAX_ATTEMPT')
retry_interval = Config.get('OPTIONS', 'RETRY_INTERVAL')


attendix_attempt = 0


def capture_window(window_name='Microsoft Teams'):
    # print(platform.system())
    if platform.system() == "Darwin":
        window = pyautogui.screenshot(os.getcwd() + "/img.png")

        # cv2.imshow(window)
        arrayy = np.array(window)

        return arrayy

    elif platform.system() == "Windows":
        window = pyautogui.screenshot(os.getcwd() + "/img.png")
        arrayy = np.array(window)

        return arrayy


def check_qr(image):
    image = cv2.imread(os.getcwd() + "/img.png")
    qrCodeDetector = cv2.QRCodeDetector()
    invertedImage = cv2.bitwise_not(image)
    decodedText, points, _ = qrCodeDetector.detectAndDecode(invertedImage)
    if points is not None:
        if len(decodedText) == 3:
            try:
                int(decodedText)
                update_attendance(decodedText)
            except ValueError:
                print("Invalid QR!")
                print(f"Retrying in {retry_interval} seconds...")
                time.sleep(int(retry_interval))
                check_qr(capture_window())
        else:
            print("Invalid QR!")
            print(f"Retrying in {retry_interval} seconds...")
            time.sleep(int(retry_interval))
            check_qr(capture_window())
    else:
        time.sleep(int(retry_interval))
        check_qr(capture_window())


def update_attendance(code):
    global attendix_attempt
    service = "https://api.apiit.edu.my/attendix"
    print(f"QR Detected!")
    print(f"Attendance Code: {code}")

    casUrl = f'https://cas.apiit.edu.my/cas/v1/tickets?username={apkey}&password={apkey_password}'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    x = requests.post(casUrl, headers=headers)

    if x.status_code == 401:
        for _ in range(3):
            print("Log in to APSpace failed! Check config.ini or network connection!")
        exit()

    soup = BeautifulSoup(x.text, 'html.parser')

    tgt = soup.find('form').get('action')

    # CAS TGT #

    tgtUrl = tgt + f"?service={service}"
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    serviceTicket = requests.post(tgtUrl, headers=headers)

    # UPDATE ATTENDANCE #

    attendixUrl = 'https://attendix.apu.edu.my/graphql'
    headers = {
        'X-Api-Key': 'da2-dv5bqitepbd2pmbmwt7keykfg4',
        'x-amz-user-agent': 'aws-amplify/2.0.7',
        'ticket': serviceTicket.text,
        'Content-Type': 'application/json',
        'Content-Length': '266',
        'Host': 'attendix.apu.edu.my',
        'Origin': 'https://apspace.apu.edu.my',
        'Connection': 'keep-alive',
        'Referer': 'https://apspace.apu.edu.my/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'TE': 'trailer'
    }

    body = {"operationName": "updateAttendance", "variables": {"otp": code},
            "query": "mutation updateAttendance($otp: String!) {\n  updateAttendance(otp: $otp) {\n    id\n    "
                     "attendance\n    classcode\n    date\n    startTime\n    endTime\n    classType\n    "
                     "__typename\n  }\n}\n"}

    print("Sending attendance code to Attendix...")
    try:
        attendanceUpdate = requests.post(attendixUrl, headers=headers, json=body, timeout=15)
        response = json.loads(attendanceUpdate.text)

        # with open('response.json', 'r') as f:
        #     response = json.load(f)

        try:
            if response['errors'][0]['message'] == "Class not found":
                if attendix_attempt != 3:
                    attendix_attempt = attendix_attempt + 1
                    print("Attendix: " + response['errors'][0]['message'])
                    print("Retrying... (Max attempt is 3)")
                    print(f"[Attempt {attendix_attempt}]")
                    check_qr(capture_window())
                else:
                    print("Attendix: " + response['errors'][0]['message'])
                    print("Max attempt reached! Retrying in 20 seconds interval...")
                    time.sleep(20)
                    print("Scanning for QR...")
                    check_qr(capture_window())
        except KeyError:
            pass

        try:
            if response['data']['updateAttendance']['attendance'] == "Y":
                print("Class Code: " + response['data']['updateAttendance']['classcode'])
                print("Class Type: " + response['data']['updateAttendance']['classType'])
                print("Start: " + response['data']['updateAttendance']['startTime'])
                print("End: " + response['data']['updateAttendance']['endTime'])
                print("Attendance Updated!")
                exit()
        except KeyError:
            pass

        # print("Server returned an unidentified response.")
        # check_qr(capture_window())
    except requests.exceptions.Timeout as err:
        print("Attendix Exception: ")
        print(err)


class APSpaceAttendance(object):
    def __init__(self):
        self.log = logging.getLogger(__name__)
        self.log.addHandler(logging.NullHandler())

        print(f"Scanning for QR every {retry_interval} seconds...")
        try:
            check_qr(capture_window())
        except KeyboardInterrupt:
            print("You have forcefully stopped the program.")
