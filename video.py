import time
import cv2
import mediapipe as mp
import numpy as np
import time
import threading
#import pygame
from math import *
import ctypes
import sys
from PyQt5.QtGui import QImage
from PyQt5.QtGui import QPixmap
from multiprocessing import Process,Manager,Value
import multiprocessing
from ctypes import c_bool
from extras import write_log

import config
from PyQt5.QtWidgets import QMessageBox

import concurrent.futures

tam_video_x=640
tam_video_y=480
# tam_video_x=1920
# tam_video_y=1080


def Captura_video_(frame_num,camara_num,DataProcess,flag_VideoProcessCaptureDone):
    #DataProcess["log_write_{}".format(camara_num)]=['']*100
    DataProcess["index_write_{}".format(camara_num)]=-1
    DataProcess["index_read_{}".format(camara_num)]=-1
    cap=cv2.VideoCapture(camara_num,cv2.CAP_DSHOW)#CAP_ANY )#cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 2)
    
    
    width=tam_video_x#640#1920
    height=tam_video_y#480#1080
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    cap.set(cv2.CAP_PROP_FPS, 60)###no necesario
    
    
    texto="Inicialización capturadora de video...{} realizada".format(camara_num)
 #   DataProcess['log_Procesa_capture_']+="\n"+texto

    write_log(DataProcess,camara_num,texto)
    

    FPS = 1/60
    TimeWorking=0
    TimeSleeping=0
    t_start = time.time()
    t_start2= time.time()
    contador=totalTime=last_contador=0
    while DataProcess['run']:#run:
        if flag_VideoProcessCaptureDone.value==False:
            
            resultado,frame=cap.read()

            if resultado==False:
                #print("break1 ",camara_num)
                write_log(DataProcess,camara_num,"break")
                #arg[1][0]['run']=False
                #DataProcess['run']=False
                break
            else:
                DataProcess['frame{}'.format(frame_num)]=frame
                ###############calculo de fps####################
                t_end2= time.time()
                contador+=1
                totalTime += t_end2 - t_start2
                t_start2=t_end2
                if totalTime>1:
                    last_contador=contador
                    contador=totalTime=0

                
                flag_VideoProcessCaptureDone.value=True
                t_end = time.time()
                TimeWorking += t_end - t_start
                t_start = t_end
                time.sleep(FPS)
                t_end = time.time()
                TimeSleeping += t_end - t_start
                t_start = t_end
                if (TimeSleeping+TimeWorking)>1:
                    DataProcess['core{}'.format(camara_num)]=TimeWorking*100/(TimeSleeping+TimeWorking)
                    DataProcess['core{}estado'.format(camara_num)]="Core {}: ON --> {:3.1f}% {}FPS  Proceso:Captura_video_({})".format(camara_num+1,DataProcess['core{}'.format(camara_num)],last_contador,camara_num)
                    TimeSleeping=0
                    TimeWorking=0
                    

    cap.release()
    
    

  
     
class ZoomClass:
    def __init__(self):
        self.mag = Magnification()
        self.mag.MagUninitialize()#############para reset...memoria

    def zoom(self, factor,x, y):
        x=int(x)
        y=int(y)
        # print("({},{})".format(x,y),end="\r")
            #while True:
        # #print(x,y)
        if self.mag.MagInitialize():
            #print("ok")
            self.mag.MagSetFullscreenTransform(factor, x, y)
            
            # print("resultado=",result)
            # aa=result
            # if result:    
            #     fInputTransformEnabled = self.mag.PBOOL()
            #     rcInputTransformSource = self.mag.LPRECT()
            #     rcInputTransformDest = self.mag.LPRECT()

                # if self.mag.MagGetInputTransform(fInputTransformEnabled, rcInputTransformSource, rcInputTransformDest):
                # #if self.mag.MagGetInputTransform(ctypes.byref(fInputTransformEnabled), ctypes.byref(rcInputTransformSource), ctypes.byref(rcInputTransformDest)):
                # # fails here
                #     print("Success")
                # else:
                #     print("Failed")
    def exit(self):
         # usado para finalizar...no necesario
        self.mag.MagUninitialize()


#############zoom mediante magnification.dll
class RECT(ctypes.Structure):
    _fields_ = [("left", ctypes.c_long),
                ("top", ctypes.c_long),
                ("right", ctypes.c_long),
                ("bottom", ctypes.c_long)]

class Magnification:
    def __init__(self):
        self.dll = ctypes.CDLL("magnification.dll")

        BOOL = ctypes.c_bool
        FLOAT = ctypes.c_float
        INT = ctypes.c_int
        self.LPRECT = LPRECT = ctypes.POINTER(RECT)
        self.PBOOL = PBOOL = ctypes.POINTER(ctypes.c_bool)

        # MagInitialize
        self.dll.MagInitialize.restype = BOOL

        # MagUninitialize 
        self.dll.MagUninitialize.restype = BOOL

        # MagSetFullscreenTransform 
        self.dll.MagSetFullscreenTransform.restype = BOOL
        self.dll.MagSetFullscreenTransform.argtypes = (FLOAT, INT, INT)

        # MagGetInputTransform 
        self.dll.MagGetInputTransform.restype = BOOL
        self.dll.MagGetInputTransform.argtypes = (PBOOL, LPRECT, LPRECT)

    def MagInitialize(self):
        return self.dll.MagInitialize()

    def MagUninitialize(self):
        return self.dll.MagUninitialize()

    def MagSetFullscreenTransform(self, magLevel, xOffset, yOffset):
        return self.dll.MagSetFullscreenTransform(magLevel, xOffset, yOffset)

    def MagGetInputTransform(self, pfEnabled, prcSource, prcDest):
        return self.dll.MagGetInputTransform(pfEnabled, prcSource, prcDest)



            
        
