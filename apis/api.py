# from websocket import create_connection
import requests
import time
import json
import asyncio
import websockets
import certifi
from model.Machine import Machine
from model.Ad import Ad
from model.Product import Product
from DbFuncs import db
import base64
import ssl
import certifi
import os
import threading
from dotenv import load_dotenv
from Observers.Subject import subject
from config.utils import setThreadStatus, getThreadStatus, THREAD_INIT, THREAD_RUNNING, THREAD_STOPPING, THREAD_FINISHED

load_dotenv()


hostName = os.environ.get('server')
port = os.environ.get('port')

def send_get_ads_info():
    url = "/api/machine/get_ads_info"
    # Send an HTTP GET request to a URL of your choice
    print(f"https://{hostName}:{port}{url}")

    response = requests.post(f"https://{hostName}:{port}{url}", verify=False)
    try:
        # Check the response status code
        if response.status_code == 200:
            responseData = response.json()   # {status : , message : , details : [{},]}
            adData = responseData['details']
            # params = Ad(0, adData['type'], bytes(adData['content'], 'utf-8'))
            db.delete_ads()
            params = Ad(0, adData['type'], base64.b64decode(adData['content']))
            db.insert_ads(params)
        else:
            print(f"Request failed with status code: {response.status_code}")
    except Exception as e:
        print("error"+ str(e))


def send_get_machine_info():

    # Send an HTTP GET request to a URL of your choice
    url = "/api/machine/get_machine_info"
    response = requests.post(f"https://{hostName}:{port}{url}", verify=False)
    
    # Check the response status code
    if response.status_code == 200:
        responseData = response.json()   # {status : , message : , details : [{},]}
        machineData = responseData['details']
        # delete machine table
        db.delete_machines()
        for item in machineData:
            params = Machine(0, item['name'], item['unit'], item['value'], base64.b64decode(item['thumbnail']))
    
            db.insert_machine(params)
    else:
        print(f"Request failed with status code: {response.status_code}")

def send_get_products_info():
    url = "/api/machine/get_product_info"

    # Send an HTTP GET request to a URL of your choice
    response = requests.post(f"https://{hostName}:{port}{url}", verify=False)

    # Check the response status code
    if response.status_code == 200:
        productData = response.json()   # {status : , message : , details : [{},]}
        # delete products table
        db.delete_products()
        for item in productData:
            params = Product(0, item['itemno'], item['name'], base64.b64decode(item['thumbnail']), item['nicotine'], item['batterypack'],
                             item['tankvolumn'], item['price'], item['currency'], item['caution'], item['stock'])
            db.insert_product(params)
    else:
        print(f"Request failed with status code: {response.status_code}")

def send_sell_product():
    url = "api/machine/sell_product"

websocket=None

async def connect_to_server():
    reconnecttime = int(os.environ.get('reconnecttime'))

    setThreadStatus(THREAD_RUNNING)

    while True:
        # ssl_context = ssl.create_default_context()
        # ssl_context.load_verify_locations(certifi.where())

        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        print("wss thread id", threading.get_native_id())

        try:
            if getThreadStatus() == THREAD_STOPPING:
                break


        except:
            print('getThreadstatus_______error')
            pass
        
        try:
            async with websockets.connect(f'wss://{hostName}:{port}', ssl = ssl_context) as websocket:
                print('connected')
                sendData = {'action': 'MachineConnect'}
                await websocket.send(json.dumps(sendData))

                # Receive data
                response = await websocket.recv()
                responseData = json.loads(response)

                print(f"Received data: {responseData}")

                machineConnectStatus = responseData['status']
                token = responseData['token']

                if machineConnectStatus == 'success':
                    while True: 
                        
                        if getThreadStatus() == THREAD_STOPPING:
                            break

                        print(f'send_websockrt_every10s')
                        time.sleep(reconnecttime)

                        statusData = {
                            'action': "MachineSendStatus",
                            'payload': {
                                'serialno': "123-456-678",
                                'temparature': "XXX",
                                'token': token, 
                            }
                        }
                        if getThreadStatus() == THREAD_STOPPING:
                            break

                        await websocket.send(json.dumps(statusData))

                        statusResponse = await websocket.recv()
                        
                        print(str(statusResponse))

                        statusResponseData = json.loads(statusResponse)
                        machineGetStatus = statusResponseData['status']
                        machineGetType = statusResponseData['type']

                        if machineGetStatus == 1:
                        
                            if getThreadStatus() == THREAD_STOPPING:
                                break

                            if 'ads' in machineGetType:
                                send_get_ads_info()
                            if 'machine' in machineGetType:
                                send_get_machine_info()
                            if 'product' in machineGetType:
                                send_get_products_info()
                            
                            try:
                                subject.notify_observers()
                            except Exception as e:
                                print("---error---")
                                print(str(e))

                else:
                    pass

        except websockets.exceptions.ConnectionClosedError:
            if getThreadStatus() == THREAD_STOPPING:
                break
            print("Reconnecting... in 10s")
            time.sleep(reconnecttime)
            pass
        except:
            if getThreadStatus() == THREAD_STOPPING:
                break
            print("Reconnecting... in 10s")
            time.sleep(reconnecttime)
            pass

        if getThreadStatus() == THREAD_STOPPING:
            break
    
    setThreadStatus(THREAD_FINISHED)


        
def close_connect():
    pass
# asyncio.get_event_loop().run_until_complete(connect_to_server())