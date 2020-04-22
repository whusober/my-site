from __future__ import absolute_import, unicode_literals
import time
from celery import shared_task
from ham.models import Ham

from celery import shared_task
import requests
import json
import hashlib
import random
import time


alphabet = list('abcdefghijklmnopqrstuvwxyz')
table = ''.join(alphabet)[:10]


def MD5(s):
    return hashlib.md5(s.encode()).hexdigest()


def encrypt(s):
    result = ''
    for i in s:
        result += table[ord(i) - ord('0')]
    return result


def run(IMEI, distance):
    # get IMEI
    IMEI = IMEI

    # Generate table Randomly
    alphabet = list('abcdefghijklmnopqrstuvwxyz')
    random.shuffle(alphabet)
    table = ''.join(alphabet)[:10]

    API_ROOT = 'http://client3.aipao.me/api'
    Version = '2.14'

    # Generate Runnig Data Randomly
    RunTime = str(random.randint(720, 1000))  # seconds
    RunDist = str(distance + random.randint(0, 3))  # meters
    RunStep = str(random.randint(1300, 1600))  # steps

    # Login
    TokenRes = requests.get(
        API_ROOT + '/%7Btoken%7D/QM_Users/Login_AndroidSchool?IMEICode=' + IMEI)
    try:
        TokenJson = json.loads(TokenRes.content.decode('utf8', 'ignore'))
    except:
        return False

    # headers
    try:
        token = TokenJson['Data']['Token']
    except:
        return False
    userId = str(TokenJson['Data']['UserId'])
    timespan = str(time.time()).replace('.', '')[:13]
    # auth = 'B' + MD5(MD5(IMEI)) + ':;' + token
    nonce = str(random.randint(100000, 10000000))
    sign = MD5(token + nonce + timespan + userId).upper()  # sign为大写


    header = {'nonce': nonce, 'timespan': timespan,
            'sign': sign, 'version': Version, 'Accept': None, 'User-Agent': None, 'Accept-Encoding': None, 'Connection': 'Keep-Alive'}

    # Start Running
    SRSurl = API_ROOT + '/' + token + '/QM_Runs/SRS?S1=30.534738&S2=114.367788&S3=2000'
    SRSres = requests.get(SRSurl, headers=header, data={})
    SRSjson = json.loads(SRSres.content.decode('utf8', 'ignore'))
    # Running Sleep
    for i in range(int(RunTime)):
        time.sleep(1)
        print(i)


    # print(SRSurl)
    # print(SRSjson)

    RunId = SRSjson['Data']['RunId']

    # End Running
    EndUrl = API_ROOT + '/' + token + '/QM_Runs/ES?S1=' + RunId + '&S4=' + \
        encrypt(RunTime,table) + '&S5=' + encrypt(RunDist,table) + \
        '&S6=&S7=1&S8=' + table + '&S9=' + encrypt(RunStep,table)
    EndRes = requests.get(EndUrl, headers=header)
    json.loads(EndRes.content.decode('utf8', 'ignore'))
    return True


@shared_task
def ham_run(username):
    obj = Ham.objects.get(username=username)
    if obj.sex:
        distance = 2000
    else:
        distance = 1500
    obj.recent_result = run(obj.IMEI, distance)
    obj.is_running = False
    obj.save()

