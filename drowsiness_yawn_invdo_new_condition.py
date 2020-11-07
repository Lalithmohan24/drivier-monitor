#python drowniness_yawn.py --webcam webcam_index

from scipy.spatial import distance as dist
from imutils.video import VideoStream
from imutils import face_utils
from threading import Thread
import numpy as np
import argparse
import imutils
import time
import dlib
import cv2
import os, sys
import csv
from os import path 
from datetime import datetime, timedelta
from datetime import date


#global nonvisible_eye
#global nonvisible_yawn

#global first
status1 = ''
status2 = ''

condition = str('0:00:25')

#global sleep_count
#global yawning_count
#global yawn_break

#global yawning

#yawn_break = 30
nonvisible_eye = 0
nonvisible_yawn = 0

first = True
starting = True

eye_dummy = True
sleep_count = 0
yawning_count = 0

#####################################################
#time creation
def csv_write():
    now = datetime.now()
    dtString = now.strftime('%H:%M:%S')
    today = date.today()
    dtdate = today.strftime("%Y-%m-%d")

    ptime = str(dtdate) + 'T' + str(dtString)

    d = datetime.today() - timedelta(hours=5, minutes=29)

    new = d.strftime('%Y-%m-%dT%H:%M:%S')
   
    new_time = str(new)

#    old_ptime = str(dtString)
#    print(time)
    return ptime, new_time, dtString
#####################################################
#file creation 

ptime, new_time, dtString = csv_write()

if path.exists('sleep.csv') == True:
  print("already sleep.csv")
else:
  
  with open('sleep.csv', mode='w+') as graph_file:
     heading_writer = csv.writer(graph_file, delimiter=',')
     heading_writer.writerow(['count','status1','status2','time','newtime'])
#     heading_writer.writerow([sleep_count,yawn_count,time])
  print("sleep csv created..")
#####################################################


def alarm(msg):
    global alarm_status
    global alarm_status2
    global saying

    while alarm_status:
        print('call')
        s = 'espeak "'+msg+'"'
        os.system(s)

    if alarm_status2:
        print('call')
        saying = True
        s = 'espeak "' + msg + '"'
        os.system(s)
        saying = False

def eye_aspect_ratio(eye):
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])

    C = dist.euclidean(eye[0], eye[3])

    ear = (A + B) / (2.0 * C)

    return ear

def final_ear(shape):
    (lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
    (rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

    leftEye = shape[lStart:lEnd]
    rightEye = shape[rStart:rEnd]

    leftEAR = eye_aspect_ratio(leftEye)
    rightEAR = eye_aspect_ratio(rightEye)

    ear = (leftEAR + rightEAR) / 2.0
    return (ear, leftEye, rightEye)

def lip_distance(shape):
    top_lip = shape[50:53]
    top_lip = np.concatenate((top_lip, shape[61:64]))

    low_lip = shape[56:59]
    low_lip = np.concatenate((low_lip, shape[65:68]))

    top_mean = np.mean(top_lip, axis=0)
    low_mean = np.mean(low_lip, axis=0)

    distance = abs(top_mean[1] - low_mean[1])
    return distance


#def yawn_breaking():
#   if yawn_break == 5:
#      yawning = True
ap = argparse.ArgumentParser()
ap.add_argument("-w", "--webcam", type=int, default=0,
                help="index of webcam on system")
args = vars(ap.parse_args())
##############################################
#threshhold values for ziegan webcam
#EYE_AR_THRESH = 0.25
#EYE_AR_CONSEC_FRAMES = 3
#YAWN_THRESH = 6
#alarm_status = False
#alarm_status2 = False
#saying = False
#COUNTER = 0
##############################################
#threshhold values for mohan webcam
EYE_AR_THRESH = 0.20
EYE_AR_CONSEC_FRAMES = 3
YAWN_THRESH = 18
alarm_status = False
alarm_status2 = False
saying = False
COUNTER = 0
##############################################
ptime, new_time, dtString = csv_write()
old_ptime = str(dtString)
print("old_ptime {}".format(old_ptime))
with open('sleep.csv', 'a') as file:
  file.writelines('{0},{1},{2},{3},{4}\n'.format(sleep_count,status1,status2,ptime,new_time))
  print("Initial value updated..")

print("-> Loading the predictor and detector...")
#detector = dlib.get_frontal_face_detector()
detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")    #Faster but less accurate
predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')


print("-> Starting Video Stream")
#vs = VideoStream("karthik_sir1.mp4").start()
vs = VideoStream(src=args["webcam"]).start()
#vs= VideoStream(usePiCamera=True).start()       //For Raspberry Pi
time.sleep(1.0)


while True:
  try:
    frame = vs.read()
    frame = imutils.resize(frame, width=450)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    #rects = detector(gray, 0)
    rects = detector.detectMultiScale(gray, scaleFactor=1.1, 
		minNeighbors=5, minSize=(30, 30),
		flags=cv2.CASCADE_SCALE_IMAGE)

    #for rect in rects:
    for (x, y, w, h) in rects:
        rect = dlib.rectangle(int(x), int(y), int(x + w),int(y + h))
        
        shape = predictor(gray, rect)
        shape = face_utils.shape_to_np(shape)

        eye = final_ear(shape)
        ear = eye[0]
#        print("ear value {}".format(ear))
        leftEye = eye [1]
        rightEye = eye[2]

        distance = lip_distance(shape)

        leftEyeHull = cv2.convexHull(leftEye)
        rightEyeHull = cv2.convexHull(rightEye)
        cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
        cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)

        lip = shape[48:60]
        cv2.drawContours(frame, [lip], -1, (0, 255, 0), 1)

        if ear < EYE_AR_THRESH:
            COUNTER += 1

            if COUNTER >= EYE_AR_CONSEC_FRAMES:
                if alarm_status == False:
                    alarm_status = True
 
#                    t = Thread(target=alarm, args=('wake up sir',))
#                    t.deamon = True
#                    t.start()
                    
                cv2.putText(frame, "DROWSINESS ALERT!", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                nonvisible_eye += 1                
                if nonvisible_eye == 3:
                   sleep_count += 1
#                if eye_dummy == True:
        else:
            COUNTER = 0
            alarm_status = False
            nonvisible_eye = 0

        if (distance > YAWN_THRESH):
                cv2.putText(frame, "Yawn Alert", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                if alarm_status2 == False and saying == False:
                    alarm_status2 = True
#                    t = Thread(target=alarm, args=('take some fresh air sir',))
#                    t.deamon = True
#                    t.start()
                nonvisible_yawn += 1
#mohan                
                if nonvisible_yawn == 5:
#                if nonvisible_yawn == 3:#ziegan cam
                  sleep_count += 1
        else:
            alarm_status2 = False
            nonvisible_yawn = 0

        ptime, new_time, dtString = csv_write()
        new_ptime = str(dtString)
#                  print("eye new time {}".format(new_ptime))
        format = '%H:%M:%S'
        value = datetime.strptime(new_ptime,format) - datetime.strptime(old_ptime,format)
        val = str(value)
#                  print("eye cal time {}".format(val))
        if val > condition:
#           if (sleep_count <= 1):
#              status = 'LOW'
#              with open('sleep.csv', 'a') as file:
#                file.writelines('{0},{1},{2},{3}\n'.format(sleep_count,status,ptime,new_time))
#                print("DRIVING STRESS LOW") 
           if (sleep_count >= 0 and sleep_count <= 3):
              status1 = 'LOW'
              status2 = ''
              with open('sleep.csv', 'a') as file:
                file.writelines('{0},{1},{2},{3},{4}\n'.format(sleep_count,status1,status2,ptime,new_time))
                print("DRIVING STRESS MEDIUM") 
           elif (sleep_count >= 4):
              status2 = 'HIGH'  
              status1 = ''           
              with open('sleep.csv', 'a') as file:
                file.writelines('{0},{1},{2},{3},{4}\n'.format(sleep_count,status1,status2,ptime,new_time))
                print("DRIVING STRESS HIGH")
           else:
              print('nothing') 
           old_ptime = str(dtString)
           starting = False     
           sleep_count = 0
           status = 'LOW'   

        cv2.putText(frame, "EAR: {:.2f}".format(ear), (300, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(frame, "YAWN: {:.2f}".format(distance), (300, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)


    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break
  except:
    print("close")
    cv2.destroyAllWindows()
    vs.stop()
    sys.exit()
