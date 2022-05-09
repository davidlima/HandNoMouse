import numpy as np
import glob
import cv2
import json
import threading

tam_video_x=1980
tam_video_y=1080

import time
class calibracion_():
    def __init__(self):
        self.tablero=(9,6)
        self.tam_frames=(tam_video_x,tam_video_y)
        self.criterio=(cv2.TermCriteria_EPS+cv2.TERM_CRITERIA_MAX_ITER,100,0.1)
        self.puntos_obj=np.zeros((self.tablero[0]*self.tablero[1],3),np.float32)
        self.puntos_obj[:,:2]=np.mgrid[0:self.tablero[0],0:self.tablero[1]].T.reshape(-1,2)
        self.puntos_3d=[]
        self.puntos_img=[]

    def calibracion_cam_(self):
        fotos=glob.glob('calibracion\\calibracion1980x1080\\*.png')
        cont=0
        for foto in fotos:
            #print(foto)
            img=cv2.imread(foto)
            gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

            #buscar esquinas
            ret,esquinas=cv2.findChessboardCorners(gray,self.tablero,None)

            if ret==True:
                self.puntos_3d.append(self.puntos_obj)
                esquinas2=cv2.cornerSubPix(gray,esquinas,(11,11),(-1,-1),self.criterio)
                self.puntos_img.append(esquinas)

                img=cv2.drawChessboardCorners(img,self.tablero,esquinas2,ret)
                txto=('calibracion\\calibracion1980x1080_2//{}.jpg').format(cont)
                print(txto,end="\r")
                cont+=1
                cv2.imwrite(txto,img)
        print("\n")
        ret,cameraMatrix,dist,rvecs,tvecs=cv2.calibrateCamera(self.puntos_3d,self.puntos_img,self.tam_frames,None,None)
        return cameraMatrix,dist
