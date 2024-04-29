import socketio
import asyncio
import numpy as np
from numpy import savez_compressed
import cv2
import math
import csv
import logging

import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
"""
For Recording and Saving Frames from mmWave and Creating and Saving Labels for Each Frame as a result of Google Media Pipe Pose Logic 
"""
logging.basicConfig(filename='rl_output.log', level=logging.INFO)

def draw_landmarks_on_image(rgb_image, detection_result):
    pose_landmarks_list = detection_result.pose_landmarks
    annotated_image = np.copy(rgb_image)

    # Loop through the detected poses to visualize.
    for idx in range(len(pose_landmarks_list)):
        pose_landmarks = pose_landmarks_list[idx]
        # RIGHT AND LEFT SEPERATE
        if (
            (pose_landmarks[16].y > 0)
            and (pose_landmarks[16].y < 0.7)
        ):
            print("1")
            logging.info("1")
        elif (
            (pose_landmarks[15].y > 0)
            and (pose_landmarks[15].y < 0.7)
        ):
            print("2")
            logging.info("2")
        else:
            print("0")
            logging.info("0")

        # BOTH ARMS TOGETHER
        # if (
        #     (pose_landmarks[15].y > 0)
        #     and (pose_landmarks[15].y < 0.6)
        #     and (pose_landmarks[16].y > 0)
        #     and (pose_landmarks[16].y < 0.6)
        # ):
        #     print("1")
        #     logging.info("1")
        # else:
        #     print("0")
        #     logging.info("0")

        # Draw the pose landmarks.
        pose_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
        pose_landmarks_proto.landmark.extend(
            [
                landmark_pb2.NormalizedLandmark(
                    x=landmark.x, y=landmark.y, z=landmark.z
                )
                for landmark in pose_landmarks
            ]
        )
        solutions.drawing_utils.draw_landmarks(
            annotated_image,
            pose_landmarks_proto,
            solutions.pose.POSE_CONNECTIONS,
            solutions.drawing_styles.get_default_pose_landmarks_style(),
        )
    return annotated_image

# STEP 2: Create an PoseLandmarker object.
base_options = python.BaseOptions(model_asset_path="pose_landmarker_full.task")
options = vision.PoseLandmarkerOptions(
    base_options=base_options,
    output_segmentation_masks=True,
)
detector = vision.PoseLandmarker.create_from_options(options)

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open camera")
    exit()

sio = socketio.AsyncClient()

XPOINTS = []
ZPOINTS = []
FRAMESBUFF = []
grid = np.ones((200,420,1), dtype=np.uint8)
j = 1

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

    np.save('MLFrames/frame'+str(j)+'.npy', grid)
    j += 1

    # resizedgrid = cv2.resize(grid, (840, 400), 0, 0, interpolation = cv2.INTER_NEAREST)
        
    # Capture frame
    ret, frame = cap.read()

    # if frame is read correctly ret is True
    if not ret:
        print("Can't receive frame (stream end?). Exiting...")
    # Operations on the frame come here
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)

    detection_result = detector.detect(mp_image)
    annotated_image = draw_landmarks_on_image(mp_image.numpy_view(), detection_result)

    cv2.imshow("live", annotated_image)

    cv2.imshow('image', grid)
    cv2.waitKey(1)

@sio.event
async def connect():
    print()
    print('Connected to Server')

@sio.event
async def disconnect():
    print()
    print('Disconnected from Server')
    # When everything is done, release the capture
    cap.release()
    cv2.destroyAllWindows() 

async def start_server():
    await sio.connect('http://141.233.xx.xxx:3000')
    await sio.wait()

if __name__ == '__main__':
    asyncio.run(start_server())