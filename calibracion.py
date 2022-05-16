import numpy as np
import glob
import cv2
from extras import write_log
from procesos import Procesamiento
#from calc3D import GetTriangulatedPts,Get3D
import calc3D
# import json
# import threading
# from extras import write_log

tam_video_x=640
tam_video_y=480
# tam_video_x=1920
# tam_video_y=1080


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
        fotos=glob.glob('calibracion\\calibracion{}x{}\\*.png'.format(tam_video_x,tam_video_y))
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
                txto=('calibracion\\calibracion{}x{}_2//{}.jpg').format(tam_video_x,tam_video_y,cont)
                print(txto,end="\r")
                cont+=1
                cv2.imwrite(txto,img)
        print("\n")
        ret,cameraMatrix,dist,rvecs,tvecs=cv2.calibrateCamera(self.puntos_3d,self.puntos_img,self.tam_frames,None,None)
        return cameraMatrix,dist
    def calibracion_default(self):
        matrix=np.array([[tam_video_x,0.,tam_video_x/2.],[0., tam_video_x, tam_video_y/2.],[0., 0., 1.]])
        print("Matriz CheesBoard Default Inicializada...")
        
        return matrix, 0
    
def  Calibracion_inicial_(process_name,DataProcess,flag_VideoProcessCaptureDone_01):   
    
    DataProcess["index_write_{}".format(process_name)]=-1
    DataProcess["index_read_{}".format(process_name)]=-1
    write_log(DataProcess,process_name,"Proceso (Calibracion_inicial_) activado...")
    cont_calibracion=0
    cont=0
    Procesa0=Procesamiento(hand='right',confidence=0.2,dinamyc_static=False)
    Procesa1=Procesamiento(hand='right',confidence=0.2,dinamyc_static=False)
    while DataProcess['run']:  
        if flag_VideoProcessCaptureDone_01.value:

            frame0=DataProcess['frame0_read'].copy()
            frame1=DataProcess['frame1_read'].copy()
            DataProcess['frame0_procesado'],pts0,_=Procesa0.Procesa_Frames_Calibracion_(0,frame0,DataProcess)    
            DataProcess['frame1_procesado'],_,pts1=Procesa1.Procesa_Frames_Calibracion_(1,frame1,DataProcess)   
            #if DataProcess['Calibracion_inicial_']==False:
            if len(pts0)>0 and len(pts1)>0:
                if cont==0:
                    cont=1
                    pts00=np.array(pts0)
                    pts11=np.array(pts1)
                else:
                    pts00=np.concatenate((pts00, pts0), axis=0)
                    pts11=np.concatenate((pts11, pts1), axis=0)
                cont_calibracion+=1
                texto="Calibración Inicial={}".format(cont_calibracion)
                write_log(DataProcess,process_name,texto)
                #print(texto)
                if cont_calibracion>=100:
                    write_log(DataProcess,process_name,"100 muestras guardadas en calibracion\\CalibracionInicial_3D.npy")
                    #print("50")
                    
                    t=[{'pts0':pts00,'pts1':pts11}]
                    np.save('calibracion\\CalibracionInicial_3D.npy',np.array(t))#,dtype=object))
                    DataProcess['run']=False
                    DataProcess['exit']=True
                    
                    DataProcess['Calibracion_inicial_']=True
            flag_VideoProcessCaptureDone_01.value=False
def  Calibracion_cropping_(process_name,DataProcess,flag_VideoProcessCaptureDone_01):   
    
    DataProcess["index_write_{}".format(process_name)]=-1
    DataProcess["index_read_{}".format(process_name)]=-1
    write_log(DataProcess,process_name,"Proceso (Calibracion_inicial_) activado...")
    cont_calibracion=0
    cont=0
    Procesa0=Procesamiento(hand='right',confidence=0.2,dinamyc_static=False)
    Procesa1=Procesamiento(hand='right',confidence=0.2,dinamyc_static=False)
    while DataProcess['run']:  
        if flag_VideoProcessCaptureDone_01.value:

            frame0=DataProcess['frame0_read'].copy()
            frame1=DataProcess['frame1_read'].copy()
            DataProcess['frame0_procesado'],pts0,_=Procesa0.Procesa_Frames_Calibracion_(0,frame0,DataProcess)    
            DataProcess['frame1_procesado'],_,pts1=Procesa1.Procesa_Frames_Calibracion_(1,frame1,DataProcess)   
            

            # if len(pts0)>0 and len(pts1)>0:
            #     if cont==0:
            #         cont=1
            #         pts00=np.array(pts0)
            #         pts11=np.array(pts1)
            #     else:
            #         pts00=np.concatenate((pts00, pts0), axis=0)
            #         pts11=np.concatenate((pts11, pts1), axis=0)
            #     cont_calibracion+=1
            #     texto="Calibración Inicial={}".format(cont_calibracion)
            #     write_log(DataProcess,process_name,texto)
            #     #print(texto)
            #     if cont_calibracion>=100:
            #         write_log(DataProcess,process_name,"100 muestras guardadas en calibracion\\CalibracionInicial_3D.npy")
            #         #print("50")
                    
            #         t=[{'pts0':pts00,'pts1':pts11}]
            #         np.save('calibracion\\CalibracionInicial_3D.npy',np.array(t))#,dtype=object))
            #         DataProcess['run']=False
            #         DataProcess['exit']=True
                    
            #         DataProcess['Calibracion_inicial_']=True
            flag_VideoProcessCaptureDone_01.value=False
def  Calibracion_Vectores_xy_teclado_mouse_(process_name,DataProcess,flag_VideoProcessCaptureDone_01):   
    
    DataProcess["index_write_{}".format(process_name)]=-1
    DataProcess["index_read_{}".format(process_name)]=-1
    write_log(DataProcess,process_name,"Proceso (Calibracion_Vectores_xy_teclado_mouse_) activado...")
    contador=5
    t_start = time.time()
    cont_calibracion=0
    cont=0
    Get3D_=calc3D.Get3D(DataProcess,process_name)
    while DataProcess['run']:  
        if flag_VideoProcessCaptureDone_01.value:
            Procesa0=Procesamiento(hand='right',confidence=0.2,dinamyc_static=False)
            Procesa1=Procesamiento(hand='right',confidence=0.2,dinamyc_static=False)
            frame0=DataProcess['frame0_read'].copy()
            frame1=DataProcess['frame1_read'].copy()
            DataProcess['frame0_procesado'],pts0,_=Procesa0.Procesa_Frames_Calibracion_(0,frame0,DataProcess)    
            DataProcess['frame1_procesado'],_,pts1=Procesa1.Procesa_Frames_Calibracion_(1,frame1,DataProcess)       
            
            try:
                R=DataProcess['calibracion'][0].R
                t=DataProcess['calibracion'][0].t
                matrix=DataProcess['calibracion'][0].matrix
            except:
                print("Matrices no encontradas!!")
            #if DataProcess['Calibracion_Vectores_xy_teclado_mouse_']==False:
            if len(pts0)>0 and len(pts1)>0:
                t_end = time.time()
                totalTime = t_end - t_start
                if totalTime>1:
                    if contador>0:
                        texto="Captura {} en {}seg.".format(cont_calibracion,contador)
                        write_log(DataProcess,process_name,texto)
                        print(texto,end="\r")
                        contador-=1
                        t_start=t_end
                    else:
                        texto="Captura {} en {}seg.".format(cont_calibracion,contador)
                        write_log(DataProcess,process_name,texto)
                        print(texto)
                        contador=5
                        pts3d=calc3D.GetTriangulatedPts(pts0,pts1,matrix,R,t,cv2.triangulatePoints)
                        # x=y=z=0
                        # for _ in pts3d:
                        #     x+=_[0]
                        #     y+=_[1]
                        #     z+=_[2]
                        # pts=[x/21.,y/21.,z/21.]

                        if cont==0:
                            cont=1
                            
                            pts3d_=np.array(pts3d)
                            #pts3d_=np.array([pts])
                            
                        else:
                            pts3d_=np.concatenate((pts3d_, pts3d), axis=0)
                            #pts3d_=np.concatenate((pts3d_, [pts]), axis=0)
                            
                        cont_calibracion+=1
                        # texto="Captura {} ".format(cont_calibracion)
                        # write_log(DataProcess,process_name,texto)
                        # print(texto)

                            
                        if cont_calibracion>=3:
                            DataProcess['Calibracion_Vectores_xy_teclado_mouse_']=True
                            datos3d=np.array([{'pts3d':pts3d_}])
                            np.save('calibracion\\Calibracion_Vectores_xy_teclado_mouse.npy',datos3d)#,dtype=object))
                            print(pts3d_)   

                            Get3D_.Vectores_base=datos3d.copy()
                            print("GET3D=",datos3d)

                            DataProcess['run']=False
                            DataProcess['exit']=True   
            flag_VideoProcessCaptureDone_01.value=False  
