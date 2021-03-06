#    Copyright 2020 Braden Bagby, Robert Stonner, Riley Hughes, David Gray, Zachary Langford

#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at

#        http://www.apache.org/licenses/LICENSE-2.0

#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.


#Creator: Braden Bagby
#FR5 FR6 FR7
#edits: David Gray

import sys
import socket
import select

import tensorflow as tf
from tensorflow.keras import datasets, layers, models
import matplotlib.pyplot as plt
import os
import glob
import pandas as pd
import numpy as np
import pathlib
from io import StringIO
import pathlib
import time

import match





TCP_IP = '127.0.0.1'
TCP_PORT = 6009
BUFFER_SIZE = 1024
param = []

ACCEPTANCE_THRESHOLD = 80 #97.2 #if guess isnt 80% sure, mark as no hand

#class_names = ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"] for landmark_cnn_v2
#class_names = ['B','L','K','R','E','D','O','Y','W','G','N','U','P'] for landmark_cnn_v3_colors
class_names = ['A','B','C','D','E','F','H','I','K','L','O','P','Q','W'] #for landmar_cnn_v4_best_letters


#Input: 21 Landmarks. X0-X21,Y0-Y21,Z0-Z21
#Output: Tensorflow DAtaset
def createDataset(input_string):
    df = input_string.split(",")


  
    lm_final = []
    landmark_hand = [] #entire hand. [finger1,finger2,finger3,etc...]
    landmark_finger_group=[] #each finger [point1,point2,point3,etc...]

    # fingers 0-4 (pinky to index)
    for j in range(0,16):
        landmark = [float(df[j]), float(df[j+21]), float(df[j+42])]
   
        landmark_finger_group.append(landmark)
        if (j+1)%4==0:
            landmark_hand.append(landmark_finger_group)
            landmark_finger_group=[]

    # finger 5 (thumb)
    for j in range(16,21):
        landmark = [float(df[j]), float(df[j+21]), float(df[j+42])]
        landmark_finger_group.append(landmark)

    landmark_hand.append(landmark_finger_group)


    lm_final.append(landmark_hand)
    features = tf.ragged.constant(lm_final)
    sample = features.to_tensor()
    return sample


#PREPARE TENSORFLOW
print("TensorFlow version: {}".format(tf.__version__)) 

model = tf.keras.models.load_model(str(pathlib.Path(__file__).parent.absolute()) + "/../model-training/models/landmark_cnn_v4_best_letters.h5", )

# Check its architecture
model.summary()

print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")



#Input: dataset
#Output: Prints prediction

def classify(s):

    newSet = createDataset(s)
    pred = model.predict(newSet)
   
    res = np.argmax(pred[0])
    threshold = pred[0][res] * 100.0 #percent of greatest guess

    if threshold < ACCEPTANCE_THRESHOLD:
        return "_"

    char = class_names[res]
    return char

  




lastChar = ''
currentWord = ""
skipCount = 0
SKIP_TIMES = 3
#adds a character and keeps track of detected words or commands
def addCharToGuess(char):
    print("--->" +char)
    global lastChar
    global currentWord
    global skipCount

    if skipCount > SKIP_TIMES: #end word
        print("word complete: " + currentWord)

        skipCount = 0
        match.matchWord(currentWord)
        currentWord = ""
     


    if lastChar == char or char == '_':
        lastChar = char
        skipCount = skipCount + 1
        return

    skipCount = 0
    lastChar = char
    currentWord = currentWord + char
    print(currentWord)


#input: 21 Landmarks each point on separate line. CSV Format
#Output: 21 landmarks. all points on same line. X0-X21,Y0-Y21,Z0-Z21
#This is needed because model is trained on data in format of X0-X21,Y0-Y21,Z0-Z21
def reformat(start):
    start = start.replace("\n", "")
    start = start.replace("\r", "")
    ar = start.split(",")


    xs = []
    ys = []
    zs = []

    index = 0
    for val in ar:
        if index % 3 == 0:
            xs.append(val)
        elif (index + 2) % 3 == 0:
            ys.append(val)
        elif (index + 1) % 3 == 0:
            zs.append(val)

        index += 1
    delimeter = ","
    finalS = delimeter.join(xs) + "," + delimeter.join(ys) + "," + delimeter.join(zs)
    return finalS

#Tests: Should be B
# finalString="0.487061,0.798828,0.000081,0.581543,0.702637,-0.053673,0.647461,0.600098,-0.091629,0.648926,0.509766,-0.142059,0.611328,0.491211,-0.193634,0.552246,0.447266,-0.009470,0.534668,0.310791,-0.040627,0.515625,0.232178,-0.079193,0.495605,0.162598,-0.108414,0.480225,0.449951,-0.028095,0.460205,0.300537,-0.066147,0.442139,0.203491,-0.121155,0.422852,0.119141,-0.165558,0.418213,0.476074,-0.059547,0.394043,0.335938,-0.103607,0.375977,0.242920,-0.161438,0.363281,0.157104,-0.203247,0.357666,0.521973,-0.096207,0.341064,0.412354,-0.139008,0.327881,0.339111,-0.175934,0.317383,0.261719,-0.200958"
# reformatString = reformat(finalString) 
# reformatString = reformatString.rstrip('\x00')
# print("------------------------------")
# print(reformatString)
# print("reformat------------------------- ")
# print()
# print("'" + reformatString + "'")
# print()
# classify(reformatString)


print( 'Listening for client...')
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((TCP_IP,TCP_PORT))
server.listen(1)
rxset = [server]
txset = []

times = 0

#recieved hand CSV over tcp from mediapipe. cleans and classifies
while 1:
    rxfds, txfds, exfds = select.select(rxset, txset, rxset)
    for sock in rxfds:
        if sock is server:
            conn, addr = server.accept()
            conn.setblocking(0)
            rxset.append(conn)
           # print( 'Connection from address:' + str(addr))
        else:
            try:
                data = sock.recv(BUFFER_SIZE).decode("utf-8")
                if ";" in data:
                    #print ("Received all the data")
                    param.append(data)
                    finalString = ""
                    for x in param:
                        finalString = finalString + x

                    param = []
                    rxset.remove(sock)

                    times = times + 1
                    if times < 43:
                        continue
                    times = 0


                    finalString = finalString.replace(";","")
                    finalString = finalString.replace("value_","")
                    reformatString = reformat(finalString) 
                    reformatString = reformatString.rstrip('\x00')

                    guessChar = classify(reformatString)

                    addCharToGuess(guessChar)


                    sock.close()
                else:
                    param.append(data)
            except:
                print ("Connection closed by remote end")
                param = []
                rxset.remove(sock)
                sock.close()
