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

tam_video_x=1920
tam_video_y=1080



def Captura_video_(frame_num,camara_num,DataProcess,flag_ProcessCaptureDone):
    #DataProcess["log_write_{}".format(camara_num)]=['']*100
    DataProcess["index_write_{}".format(camara_num)]=-1
    DataProcess["index_read_{}".format(camara_num)]=-1
    cap=cv2.VideoCapture(camara_num)#,cv2.CAP_ANY)#CAP_ANY )#CAP_DSHOW)
    #cap=cv2.VideoCapture(camara_num,cv2.CAP_DSHOW)
    width=tam_video_x#640#1920
    height=tam_video_y#480#1080
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    cap.set(cv2.CAP_PROP_FPS, 30)###no necesario
    texto="Inicialización capturadora de video...{} realizada".format(camara_num)
 #   DataProcess['log_Procesa_capture_']+="\n"+texto

    write_log(DataProcess,camara_num,texto)
 
    while DataProcess['run']:#run:
        if flag_ProcessCaptureDone.value==False:
            
            resultado,frame=cap.read()
            if resultado==False:
                #print("break1 ",camara_num)
                write_log(DataProcess,camara_num,"break")
                #arg[1][0]['run']=False
                #DataProcess['run']=False
                break
            else:
                DataProcess['frame{}'.format(frame_num)]=frame
                
                flag_ProcessCaptureDone.value=True
                
                time.sleep(1/300)

    cap.release()
    

  
     
class ZoomClass:
    def __init__(self):
        self.mag = Magnification()
        self.mag.MagUninitialize()#############para reset...memoria

    def zoom(self, factor,x, y):
        x=int(x)
        y=int(y)
        print("({},{})".format(x,y),end="\r")
            #while True:
        # #print(x,y)
        # if self.mag.MagInitialize():
        #     #print("ok")
        #     self.mag.MagSetFullscreenTransform(factor, x, y)
            
        #     # print("resultado=",result)
        #     # aa=result
        #     # if result:    
        #     #     fInputTransformEnabled = self.mag.PBOOL()
        #     #     rcInputTransformSource = self.mag.LPRECT()
        #     #     rcInputTransformDest = self.mag.LPRECT()

        #         # if self.mag.MagGetInputTransform(fInputTransformEnabled, rcInputTransformSource, rcInputTransformDest):
        #         # #if self.mag.MagGetInputTransform(ctypes.byref(fInputTransformEnabled), ctypes.byref(rcInputTransformSource), ctypes.byref(rcInputTransformDest)):
        #         # # fails here
        #         #     print("Success")
        #         # else:
        #         #     print("Failed")
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



            
        
