#!/usr/bin/env python
#import device_patches       # Device specific patches for Jetson Nano (needs to be before importing cv2)

import cv2
import os
import sys, getopt
import signal
import time
from edge_impulse_linux.image import ImageImpulseRunner
import pyrebase
import json
import time

Spill_Count = 0
Smudge_Count = 0
Die_Cut_Count = 0
Inverted_Label_Count = 0
start = 0
flag = 0


start_value = {"Value" : start}
count_data = {"Die Cutting" : Die_Cut_Count,"Ink Spills":Spill_Count,"Ink Smudges":Smudge_Count,"Inverted Labels":Inverted_Label_Count,}


runner = None
# if you don't want to see a camera preview, set this to False
show_camera = True

if (sys.platform == 'linux' and not os.environ.get('DISPLAY')):
    show_camera = False

def now():
    b = round(time.time() * 1000)
    print("NOW", b)
    return b

def get_webcams():
    port_ids = []
    for port in range(5):
        print("Looking for a camera in port %s:" %port)
        camera = cv2.VideoCapture(port)
        if camera.isOpened():
            ret = camera.read()[0]
            if ret:
                backendName =camera.getBackendName()
                w = camera.get(3)
                h = camera.get(4)
                print("Camera %s (%s x %s) found in port %s " %(backendName,h,w, port))
                port_ids.append(port)
            camera.release()
    return port_ids

def sigint_handler(sig, frame):
    print('Interrupted')
    if (runner):
        runner.stop()
    sys.exit(0)

signal.signal(signal.SIGINT, sigint_handler)

def help():
    print('python classify.py <path_to_model.eim> <Camera port ID, only required when more than 1 camera is present>')

def main(argv):
    global Spill_Count,Smudge_Count,Die_Cut_Count,Inverted_Label_Count,start,flag
    if flag == 0:
        config = {
            "apiKey": "AIzaSyAqbi6Cud5CDw7bXJE6nCPNCvMECS08oOE",
            "authDomain": "counter-77c7e.firebaseapp.com",
            "databaseURL": "https://counter-77c7e-default-rtdb.firebaseio.com",
            "projectId": "counter-77c7e",
            "storageBucket": "counter-77c7e.appspot.com",
            "messagingSenderId": "192592357928",
            "appId": "1:192592357928:web:1abe3dbf9425a3f649e31d"
            }
        firebase = pyrebase.initialize_app(config)
        db = firebase.database()
        db.child("Count").set(count_data)
        db.child("Count_Start").set(start_value)
        flag = 1

    try:
        opts, args = getopt.getopt(argv, "h", ["--help"])
    except getopt.GetoptError:
        help()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            help()
            sys.exit()

    if len(args) == 0:
        help()
        sys.exit(2)

    model = args[0]

    dir_path = os.path.dirname(os.path.realpath(__file__))
    modelfile = os.path.join(dir_path, model)

    print('MODEL: ' + modelfile)

    with ImageImpulseRunner(modelfile) as runner:
        try:
            model_info = runner.init()
            print('Loaded runner for "' + model_info['project']['owner'] + ' / ' + model_info['project']['name'] + '"')
            labels = model_info['model_parameters']['labels']
            if len(args)>= 2:
                videoCaptureDeviceId = int(args[1])
            else:
                port_ids = get_webcams()
                if len(port_ids) == 0:
                    raise Exception('Cannot find any webcams')
                if len(args)<= 1 and len(port_ids)> 1:
                    raise Exception("Multiple cameras found. Add the camera port ID as a second argument to use to this script")
                videoCaptureDeviceId = int(port_ids[0])

            camera = cv2.VideoCapture(videoCaptureDeviceId)
            ret = camera.read()[0]
            if ret:
                backendName = camera.getBackendName()
                w = camera.get(3)
                h = camera.get(4)
                print("Camera %s (%s x %s) in port %s selected." %(backendName,h,w, videoCaptureDeviceId))
                camera.release()
            else:
                raise Exception("Couldn't initialize selected camera.")

            next_frame = 0 # limit to ~10 fps here

            for res, img in runner.classifier(videoCaptureDeviceId):

                if "bounding_boxes" in res["result"].keys():
                    print('Found %d bounding boxes (%d ms.)' % (len(res["result"]["bounding_boxes"]), res['timing']['dsp'] + res['timing']['classification']))
                    Count = len(res["result"]["bounding_boxes"])
                    Count_Start = db.child("Count_Start").get()
                    
                    if Count_Start.val()['Value'] == 1:
                      for bb in res["result"]["bounding_boxes"]:
                        img = cv2.rectangle(img, (bb['x'], bb['y']), (bb['x'] + bb['width'], bb['y'] + bb['height']), (255, 0, 0), 1)
                        Label  = bb['label']
                        score  = bb['value']
                        print(Label, score)
                        if score > 0.50 :
                          if Label == "S1":
                             Spill_Count+=1
                          elif Label == "S2":
                             Spill_Count+=1
                          elif Label == "SM":
                             Smudge_Count+=1
                          elif Label == "DC":
                             Die_Cut_Count+=1
                          elif Label == "INV":
                             Inverted_Label_Count+=1
                      db.child("Count").update({"Die Cutting" : Die_Cut_Count,"Ink Spills":Spill_Count,"Ink Smudges":Smudge_Count,"Inverted Labels":Inverted_Label_Count,})
                      
                      #Spill_Count, Smudge_Count, Die_Cut_Count, Inverted_Label_Count = 0,0,0,0
                if (show_camera):
                    cv2.imshow('edgeimpulse', cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
                    if cv2.waitKey(1) == ord('q'):
                        break
                next_frame = now() + 10
        finally:
            if (runner):
                runner.stop()

if __name__ == "__main__":
   main(sys.argv[1:])