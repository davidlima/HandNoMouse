import cv2
import numpy as np
from math import *
from PyQt5.QtWidgets import QMessageBox
#from calibracion import calibracion_
import calibracion
import config
import ctypes
from extras import write_log

class Calculo_3D_():
    def __init__(self,DataProcess,process_name):
        self.DataProcess=DataProcess
        self.process_name=process_name
        self.calibracion_recuperada=False
    def LoadCalibracion(self,self_):
        if self.Calibracion_Inicial():
            try:
                record_cal=np.load("calibracion\\CalibracionMatriz_Chess_Board_.npy",allow_pickle=True)
                self.calibracion_recuperada=True
                self.matrix=record_cal[0]['matrix']
                self.R=record_cal[0]['R']
                self.t=record_cal[0]['t']
            # print("Recuperación archivo CalibracionMatriz_Chess_Board_.npy correcta!")
                write_log(self.DataProcess,self.process_name,"Recuperación archivo CalibracionMatriz_Chess_Board_.npy correcta!")
                write_log(self.DataProcess,self.process_name,"Matriz=\n{}".format(self.matrix))
                write_log(self.DataProcess,self.process_name,"Rotacion R=\n{}".format(self.R))
                write_log(self.DataProcess,self.process_name,"Traslacion t=\n{}".format(self.t))
            except:
                self.calibracion_recuperada=False
                #QMessageBox.about(self_,"Archivo CalibracionMatriz_Chess_Board_.npy no encontrado!", "Se intentará generar nuevo archivo según los datos guardados")
                print("No ha sido posible recuperar el archivo de calibración previa CalibracionMatriz_Chess_Board_.npy, calculando archivo...")
                cal_=calibracion.calibracion_()
                self.matrix,self.dist=cal_.calibracion_cam_()
                #self.matrix,self.dist=cal_.calibracion_default()
                try:
                    #self.Calibracion_Inicial()
                    ###MATRIZ FUNDAMENTAL
                    #F,mask=cv2.findFundamentalMat(pts1,pts2,cv2.RANSAC)
                    F,mask=cv2.findFundamentalMat(self.pts0,self.pts1,cv2.FM_LMEDS,	confidence =  0.99)

                    K=self.matrix
                    ###MATRIZ ESENCIAL
                    E=K.T.dot(F.dot(K))
                    #R1,R2,t=ExtractCameraPoses(E)
                    #t=t[:,np.newaxis]

                    _,self.R,self.t,mask=cv2.recoverPose(E,self.pts0,self.pts1,K)###utilizado para descartar todas las posiciones de las cámaras erroneos
                    ###R=Rotación
                    ###t=Traslación
                    t=[{'matrix':self.matrix,'R':self.R,'t':self.t}]
                    np.save('calibracion\\CalibracionMatriz_Chess_Board_.npy',np.array(t))#,dtype=object))
                    print("calibracion\\CalibracionMatriz_Chess_Board_.npy Guardada!")
                    return True
                except:
                    print("No ha sido posible recuperar el archivo de calibración de puntos entre cámaras Calibracion_inicial_3D.npy. Error!")
                    return False
        else:
            write_log(self.DataProcess,self.process_name,"No ha sido posible recuperar el archivo calibracion\\CalibracionInicial_3D.npy! se requiere calibrar la opción (Sincronizar cámaras 3D)")

    def LoadCalibracion_xy(self):
        try:
            datos3d=np.load("calibracion\\Calibracion_Vectores_xy_teclado_mouse.npy",allow_pickle=True)
            print("Recuperación Calibracion_Vectores_xy_teclado_mouse.npy correcta!")
            return True
        except:
            #QMessageBox.about(self, "Archivo Calibracion_Vectores_xy_teclado_mouse.npy no encontrado!", "Se requiere ir al apartado de calibración para generar un nuevo archivo")
            print("No ha sido posible abrir el archivo de Calibracion_Vectores_xy_teclado_mouse.npy")
            return False

    def Calibracion_Inicial(self):
        try:
            t=np.load("calibracion\\CalibracionInicial_3D.npy",allow_pickle=True)
            self.pts0=t[0]['pts0']
            self.pts1=t[0]['pts1']
            return True
        except:
            return False
def GetTriangulatedPts(img1pts,img2pts,K,R,t,triangulateFunc):
    img1ptsHom=cv2.convertPointsToHomogeneous(img1pts)[:,0,:]
    img2ptsHom=cv2.convertPointsToHomogeneous(img2pts)[:,0,:]
    img1ptsNorm=(np.linalg.inv(K).dot(img1ptsHom.T)).T
    img2ptsNorm=(np.linalg.inv(K).dot(img2ptsHom.T)).T
    img1ptsNorm=cv2.convertPointsFromHomogeneous(img1ptsNorm)[:,0,:]
    img2ptsNorm=cv2.convertPointsFromHomogeneous(img2ptsNorm)[:,0,:]
    pts4d=triangulateFunc(np.eye(3,4),np.hstack((R,t)),img1ptsNorm.T,img2ptsNorm.T)
    pts3d=cv2.convertPointsFromHomogeneous(pts4d.T)[:,0,:]
    return pts3d
def MatrizRotacion_(angle_x,angle_y,angle_z,matriz):
    if matriz=='x':
        rotacion = [[1, 0, 0],
                    [0, cos(angle_x), -sin(angle_x)],
                    [0, sin(angle_x), cos(angle_x)]]
    elif matriz=='y':
        rotacion = [[cos(angle_y), 0, sin(angle_y)],
                    [0, 1, 0],
                    [-sin(angle_y), 0, cos(angle_y)]]
    else:#=='z'
        rotacion = [[cos(angle_z), -sin(angle_z), 0],
                    [sin(angle_z), cos(angle_z), 0],
                    [0, 0, 1]]
    return rotacion
def multiply_m(a, b):
    a_rows = len(a)
    a_cols = len(a[0])
    b_rows = len(b)
    b_cols = len(b[0])
    # Dot product matrix dimentions = a_rows x b_cols
    product = [[0 for _ in range(b_cols)] for _ in range(a_rows)]
    if a_cols == b_rows:
        for i in range(a_rows):
            for j in range(b_cols):
                for k in range(b_rows):
                    product[i][j] += a[i][k] * b[k][j]
    else:
        print("INCOMPATIBLE MATRIX SIZES")
    return product     
def suma_m(a, xx,yy,zz):
    a[0][0]+=xx
    a[1][0]+=yy
    a[2][0]+=zz
    return a
class Get3D():
    def __init__(self,DataProcess,process_name):
        try:
            self.tmp=0
            self.Vectores_base=np.load("calibracion\\Calibracion_Vectores_xy_teclado_mouse.npy",allow_pickle=True)
#            print(self.Vectores_base)
            self.process_name=process_name
            self.DataProcess=DataProcess
            self.cube_points = []
            self.Rx=self.Ry=self.Rz=0
            self.angle_x = self.angle_y = self.angle_z = 0
            self.xx=self.yy=self.zz=0.0
            self.rotation_x=MatrizRotacion_(self.angle_x,self.angle_y,self.angle_z,'x')
            self.rotation_y=MatrizRotacion_(self.angle_x,self.angle_y,self.angle_z,'y')
            self.rotation_z=MatrizRotacion_(self.angle_x,self.angle_y,self.angle_z,'z')
        except:
            print("Archivo Calibracion_Vectores_xy_teclado_mouse.npy no encontrado!", "Se requiere ir al apartado de calibración para generar un nuevo archivo")
    def Rotate_Translate_3D(self,pts3d):
        dedo_calculo=0
        self.cube_points=[]#self.cube_points[:4]
        aa=[]
        try:
            self.cube_points.append([[self.Vectores_base[0]['pts3d'][0+dedo_calculo][0]],[self.Vectores_base[0]['pts3d'][0+dedo_calculo][1]],[self.Vectores_base[0]['pts3d'][0+dedo_calculo][2]]])#####cube_points[4]
            self.cube_points.append([[self.Vectores_base[0]['pts3d'][21+dedo_calculo][0]],[self.Vectores_base[0]['pts3d'][21+dedo_calculo][1]],[self.Vectores_base[0]['pts3d'][21+dedo_calculo][2]]])
            self.cube_points.append([[self.Vectores_base[0]['pts3d'][42+dedo_calculo][0]],[self.Vectores_base[0]['pts3d'][42+dedo_calculo][1]],[self.Vectores_base[0]['pts3d'][42+dedo_calculo][2]]])
        except:
            if self.tmp==0:
                write_log(self.DataProcess,self.process_name,"Vectores Base no disponibles. Recuerde ejecutar calibración-->Detección plano xy")
                self.tmp=1
                print("Vectores Base no disponibles")
        # aa.append([[self.Vectores_base[0]['pts3d'][0+0][0]],[self.Vectores_base[0]['pts3d'][0+0][1]],[self.Vectores_base[0]['pts3d'][0+0][2]]])#####cube_points[4]


        

        # aa.append([[self.Vectores_base[0]['pts3d'][1+0][0]],[self.Vectores_base[0]['pts3d'][1+0][1]],[self.Vectores_base[0]['pts3d'][1+0][2]]])
        # aa.append([[self.Vectores_base[0]['pts3d'][2+0][0]],[self.Vectores_base[0]['pts3d'][2+0][1]],[self.Vectores_base[0]['pts3d'][2+0][2]]])        
        #self.cube_points.extend(aa)
        for _ in pts3d:
            aa.append([[_[0].copy()],[_[1].copy()],[_[2].copy()]])
        self.cube_points.extend(aa)#####cube_points[9]
        ##xx,yy,zz se utiliza para desplazar todos los vectores respecto a este vector en posicion nueva (0,0,0)
        xx=-self.cube_points[0][0][0]#self.Vectores_base[0]['pts3d'][0+0][0]
        yy=-self.cube_points[0][1][0]#self.Vectores_base[0]['pts3d'][0+0][1]
        zz=-self.cube_points[0][2][0]#self.Vectores_base[0]['pts3d'][0+0][2]
        ####MUEVE Vectores_base 0 AL PUNTO (0,0,0)
        for point in range(len(self.cube_points[:])):
            self.cube_points[point]=suma_m(self.cube_points[point],xx,yy,zz)
        z_=self.cube_points[1][2][0]
        y_=self.cube_points[1][1][0]
        Rx=np.arctan(z_/y_)
        if y_<0:Rx+=np.pi
        #rotation_x=MatrizRotacion_(angle_x-Rx,0,0,'x')
        rotation_x=MatrizRotacion_(-Rx,0,0,'x')
        for point in range(len(self.cube_points[:])):
            self.cube_points[point] = multiply_m(rotation_x, self.cube_points[point])
        x_=self.cube_points[1][0][0]
        y_=self.cube_points[1][1][0]
        Rz=np.arctan(y_/x_)
        if x_<0:Rz+=np.pi
        rotation_z=MatrizRotacion_(0,0,-Rz,'z')
        #rotation_z=MatrizRotacion_(0,0,angle_z-Rz,'z')
        for point in range(len(self.cube_points[:])):
            self.cube_points[point] = multiply_m(rotation_z, self.cube_points[point])
        z_=self.cube_points[2][2][0]
        y_=self.cube_points[2][1][0]
        Rx=np.arctan(z_/y_)
        if y_<0:Rx+=np.pi
        Rx+=np.pi############################# Z INVERTIDA
        rotation_x=MatrizRotacion_(-Rx,0,0,'x')
        #rotation_x=MatrizRotacion_(angle_x-Rx,0,0,'x')
        for point in range(len(self.cube_points[:])):
            self.cube_points[point] = multiply_m(rotation_x, self.cube_points[point])
        return self.cube_points[:]


