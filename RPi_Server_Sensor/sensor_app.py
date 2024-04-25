from flask import Flask, render_template, request
from flask_socketio import SocketIO
from flask_mqtt import Mqtt
from requests_futures.sessions import FuturesSession
from random import random
from threading import Lock, Event
from datetime import datetime

from sensor4rpi import Sensor

import serial
import numpy as np
import time
import math
import struct

"""
Background Thread
"""
thread1 = None
thread2 = None
thread_lock = Lock()
thread_event = Event()
status = False

sensor = Sensor()

xptcloud = []
yptcloud = []
zptcloud = []
dopcloud = []
ids = []
onZones = []
offZones = []
xpos = []
ypos = []
zpos = []
xvel = []
yvel = []
zvel = []

app = Flask(__name__)
app.config['SECRET_KEY'] = '****'
app.config['MQTT_BROKER_URL'] = '***.***.**.***'

socketio = SocketIO(app, cors_allowed_origins='*')
mqtt = Mqtt(app)

numClients = 0


"""
Function for Starting Sensor: Parsing Cfg and Sending Data
"""
def sensor_thread(event):
    print("Starting mmWave Sensing")
    sensor.connectCom()
    sensor.parseCfg()
    sensor.sendCfg()
    while event.is_set():
        xptcloud.clear()
        yptcloud.clear()
        zptcloud.clear()
        dopcloud.clear()
        numINz = [0,0,0,0]
        onZones.clear()
        offZones.clear()
        ids.clear()
        xpos.clear()
        ypos.clear()
        zpos.clear()
        xvel.clear()
        yvel.clear()
        zvel.clear()
        data = sensor.readData()
        if len(data) > 8: # change to 8 for full point clouds, 4 for clustered ID tracking
            if data['numDetectedPoints'] > 0:
                for n in range(int(data['numDetectedPoints'])):
                    xptcloud.append(round(data['pointCloud'][n,0], 3))
                    yptcloud.append(round(data['pointCloud'][n,1], 3))
                    zptcloud.append(round(data['pointCloud'][n,2], 3))
                    dopcloud.append(round(data['pointCloud'][n,3], 3))
            for i in range(int(data['numDetectedTracks'])):
                ids.append(i)
                xpos.append(round(data['trackData'][i,1], 3))
                ypos.append(round(data['trackData'][i,2], 3))
                zpos.append(round(data['heightData'][i,1], 3))
                xvel.append(round(data['trackData'][i,4], 3))
                yvel.append(round(data['trackData'][i,5], 3))
                zvel.append(round(data['trackData'][i,6], 3))

            # Zone Display and Alert Logic
            for i in range(int(len(ids))):
                if (xpos[i] < 0 and ypos[i] < 3):
                    numINz[0] += 1
                elif (xpos[i] < 0 and ypos[i] > 3):
                    numINz[1] += 1
                elif (xpos[i] > 0 and ypos[i] < 3):
                    numINz[2] += 1
                elif (xpos[i] > 0 and ypos[i] > 3):
                    numINz[3] += 1
            for i in range(4):
                if numINz[i] > 0:
                    onZones.append(i+1)
                else:
                    offZones.append(i+1)

            mqtt.publish('esp32/zones', ' '.join([str(elem) for elem in onZones]))
            socketio.emit(
                'updateSensorData',
                {
                    'ID': ids,
                    'x_data': xpos,
                    'y_data': ypos,
                    'z_data': zpos, 
                    'x_vel': xvel,
                    'y_vel': yvel,
                    'z_vel': zvel,
                    'on_zones': onZones,
                    'off_zones': offZones,
                    'x_pts': xptcloud,
                    'y_pts': yptcloud,
                    'z_pts': zptcloud,
                    'dopp': dopcloud,
                }
            )
            

def time_thread(event):
    starttime = time.time()
    session = FuturesSession()
    while event.is_set():
        elapsedtime = math.floor(time.time() - starttime)
        ftime = time.strftime('%H:%M:%S', time.gmtime(elapsedtime))      
        socketio.emit('updateTime', {'up_time': ftime})
        session.get('https://script.google.com/macros/s/**********************************/exec?time=' + str(ftime))
        time.sleep(1)



"""
Serve root index file (Flask)
"""
@app.route('/')
def index():
    return render_template('index.html')


"""
Incoming Start Command FROM Clients
"""
@socketio.on('runmessage')
def handleMessage(msg):
    global status 
    status = msg['status']
    socketio.emit("runstatus", {'status': status})

    if (status == True):
        global thread1
        global thread2
        with thread_lock:
            if thread1 is None:
                thread_event.set()
                thread1 = socketio.start_background_task(sensor_thread, thread_event)
                thread2 = socketio.start_background_task(time_thread, thread_event)
    if (status == False):
        thread_event.clear()
        with thread_lock:
            if thread1 is not None:
                thread1.join()
                thread2.join()
                thread1 = None
                thread2 = None
                sensor.sendStopCfg()

"""
Outgoing TO Clients
"""
"""
Decorator for connect
"""
@socketio.on('connect')
def connect():
    global numClients
    global status
    numClients += 1
    print('Client connected')
    socketio.emit("users", {"user_count": numClients})
    socketio.emit("runstatus", {'status': status})

"""
Decorator for disconnect
"""
@socketio.on('disconnect')
def disconnect():
    global numClients
    numClients -= 1
    print('Client disconnected',  request.sid)
    socketio.emit("users", {"user_count": numClients})
    
"""
MQTT
"""
@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    mqtt.subscribe('esp32/zones/status/one')
    mqtt.subscribe('esp32/zones/status/two')
    mqtt.subscribe('esp32/zones/status/three')
    mqtt.subscribe('esp32/zones/status/four')

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
	data = dict(
		topic = message.topic,
		payload = message.payload.decode()
		)
	# ZONE CONFIRMATION LOGIC HERE if (topic = 'esp32/zones/status/one') ...
	print(data['payload'])
		
# @mqtt.on_log()
# def handle_logging(client, userdata, level, buf):
# 	print(level, buf)

"""
Run Script: Server process begins 
"""
if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port="3000", use_reloader=False)