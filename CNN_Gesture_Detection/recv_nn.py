# FOR APPLYING TRAINED ML WIEGHTS TO LIVE DATA

import socketio
import asyncio
import numpy as np
from numpy import savez_compressed
import cv2
import math
""" 
For Applying Trained Weights to Real-Time Data
"""

sio = socketio.AsyncClient()

XPOINTS = []
ZPOINTS = []
FRAMESBUFF = []
grid = np.ones((200,420,1), dtype=np.uint8)
j = 1

WEIGHTS = np.load('MLWeights.npz')

k = 0
def ml_process(img):
    global k
    img = img.astype("float32") / 255
    img = np.reshape(img, (1, 84000))
    img.shape += (1,)
    # Forward propagation input -> hidden
    h_pre = WEIGHTS['B_I_H'] + WEIGHTS['W_I_H'] @ img
    h = 1 / (1 + np.exp(-h_pre))
    # Forward propagation hidden -> output
    o_pre = WEIGHTS['B_H_O'] + WEIGHTS['W_H_O'] @ h
    o = 1 / (1 + np.exp(-o_pre))

    print(o.argmax(), k)
    k += 1

@sio.on('updateSensorData') 
def response(data):
    global j, FRAMESBUFF, grid
    grid[:,:] = [0]
    XPOINTS = []
    ZPOINTS = []
    DOPPLER = []
    XPOINTS = data["x_pts"]
    ZPOINTS = data["z_pts"]
    DOPPLER = data["dopp"]

    i = 0
    while i < len(XPOINTS):
        if (ZPOINTS[i] > 0) and (abs(XPOINTS[i]) < 2):
            grid[199-math.floor(100*ZPOINTS[i]),math.floor(100*XPOINTS[i])+219] = [255]
        i += 1

    FRAMESBUFF.insert(0, grid)
    if (len(FRAMESBUFF) == 6):
        FRAMESBUFF.pop()
        grid = np.array(FRAMESBUFF[0]) + np.array(FRAMESBUFF[1]) + np.array(FRAMESBUFF[2]) + np.array(FRAMESBUFF[3]) + np.array(FRAMESBUFF[4])

    ml_process(grid)

    resizedgrid = cv2.resize(grid, (840, 400), 0, 0, interpolation = cv2.INTER_NEAREST)

    cv2.imshow('image', resizedgrid)
    cv2.waitKey(1)

@sio.event
async def connect():
    print()
    print('Connected to Server')

@sio.event
async def disconnect():
    print()
    print('Disconnected from Server')
    cv2.destroyAllWindows() 

async def start_server():
    await sio.connect('http://141.233.xx.xxx:3000')
    await sio.wait()

if __name__ == '__main__':
    asyncio.run(start_server())