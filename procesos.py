from multiprocessing import Process,Manager,Value
import mediapipe as mp
import cv2
import numpy as np
import time
import ctypes
from video import Captura_video_
from calc3D import GetTriangulatedPts,Get3D
from extras import write_log,Determina_Acciones_mano


tam_video_x=1920
tam_video_y=1080 

def MainProcess_(camaras,DataProcess,flag_Show):
    
    # T0_=threading.Thread(target=Procesa_video_, args=(0,[self.arg_])).start()
    # T1_=threading.Thread(target=Procesa_video_, args=(1,[self.arg_])).start()
    
    DataProcess['log_Procesa_frames_']=[]
    # DataProcess['log_Procesa_capture_']=""
    flag_ProcessCaptureDone_0=Value('i',False)
    flag_ProcessCaptureDone_1=Value('i',False)
    flag_ProcessCaptureDone=Value('i',False)
 #   DataProcess['log_1'].setText("HOLA")
 #   print(camaras[0],camaras[1])

    


    P0_=Process(target=Captura_video_, args=(camaras[0],0,DataProcess,flag_ProcessCaptureDone_0)).start()
    P1_=Process(target=Captura_video_, args=(camaras[1],1,DataProcess,flag_ProcessCaptureDone_1)).start()
    
    P2_=Process(target=Procesa_frames_, args=(3,DataProcess,flag_ProcessCaptureDone)).start()
    #P3_=Process(target=Procesa_frames_, args=(4,DataProcess,flag_ProcessCaptureDone)).start()
    

    ################SINCRONIZACION DE LAS CAPTURAS
    while DataProcess['run']:
       # print(FlagProcess['flag_ProcessCaptureDone_0'],FlagProcess['flag_ProcessCaptureDone_1'])
        if flag_ProcessCaptureDone_0.value  and flag_ProcessCaptureDone_1.value:
            DataProcess['frame0_read']=DataProcess['frame0'].copy()
            DataProcess['frame1_read']=DataProcess['frame1'].copy()
            flag_ProcessCaptureDone.value=True###
            while flag_ProcessCaptureDone.value:
                time.sleep(1/300)
            flag_Show.value=True
            flag_ProcessCaptureDone_0.value=False
            flag_ProcessCaptureDone_1.value=False


class Procesamiento():  
    def __init__(self,hand='right',confidence=0.9,dinamyc_static=False):
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils ####PARA DIBUJAR SOLUCIONES
        self.hands=self.mp_hands.Hands(static_image_mode=dinamyc_static,max_num_hands=2,min_detection_confidence=confidence)###min_tracking_confidence=0.5
        self.max_x=self.max_y=0
        self.x_min_=tam_video_x
        self.y_min_=tam_video_y
        self.x_max_=0
        self.y_max_=0
        self.x_min=tam_video_x
        self.y_min=tam_video_y
        self.x_max=0
        self.y_max=0
        

    def Procesa_Frame(self,camara_num,frame,DataProcess):

        frame=cv2.flip(frame,1)
        if DataProcess['croping']:
            if camara_num==0:croping=DataProcess['croping0']
            else:croping=DataProcess['croping1']
            frame = frame[ croping[0]:croping[1],croping[2]:croping[3]]

        #print(camara_num,croping)
        
        frame_rgb=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        results=self.hands.process(frame_rgb)
        if DataProcess['croping']==False:
            croping=[0,0,0,0]
            tam_x=tam_video_x
            tam_y=tam_video_y
            croping[0]=croping[2]=0
        else:
            tam_x=croping[3]-croping[2]
            tam_y=croping[1]-croping[0]
       # frame=cv2.circle(frame,(int(tam_x//2),int(tam_y//2)),10,(255,0,255),2)
        pts0=[]
        pts1=[]
        if results.multi_hand_landmarks is not None:
                for hand_landmarks in results.multi_hand_landmarks:
                    self.mp_drawing.draw_landmarks(frame,hand_landmarks,self.mp_hands.HAND_CONNECTIONS)####################################cambiar dibujos de manos!!
        if results.multi_hand_landmarks is not None:# and not run[0]:
            if results.multi_handedness[0].classification[0].label=='Right':
                tmp=0
            elif len(results.multi_hand_landmarks)>1 and results.multi_handedness[1].classification[0].label=='Right':
                tmp=1
            else:
                tmp=-1
            if tmp!=-1:
                if camara_num==0:
                    for _ in results.multi_hand_landmarks[tmp].landmark:
                        pts0.append([croping[2]+(_.x*tam_x),croping[0]+(_.y*tam_y)])##escala y añade parámetros del croping extraido para adaptarlo a las dimensiones de captura 1920x1080
                    pts0=np.array(pts0)
                    self.x_min=int(pts0[:,0].min())
                    self.x_max=int(pts0[:,0].max())
                    self.y_min=int(pts0[:,1].min())
                    self.y_max=int(pts0[:,1].max())
                        #frame=cv2.circle(frame,(int(_[0]),int(_[1])),2,(255,255,255),2)
                else:
                    for _ in results.multi_hand_landmarks[tmp].landmark:
                        pts1.append([croping[2]+(_.x*tam_x),croping[0]+(_.y*tam_y)])##escala y añade parámetros del croping extraido para adaptarlo a las dimensiones de captura 1920x1080
                        ######################################################################################################################################################
                        #pts1.append([_.x*tam_video_x,_.y*tam_video_y])######################################################################################################
                        ######################################################################################################################################################
                    pts1=np.array(pts1)
                    self.x_min=int(pts1[:,0].min())
                    self.x_max=int(pts1[:,0].max())
                    self.y_min=int(pts1[:,1].min())
                    self.y_max=int(pts1[:,1].max())
        if self.x_min<self.x_min_:self.x_min_=self.x_min
        if self.y_min<self.y_min_:self.y_min_=self.y_min
        if self.x_max>self.x_max_:self.x_max_=self.x_max
        if self.y_max>self.y_max_:self.y_max_=self.y_max
        if self.x_min_<self.x_max_ and self.y_min_<self.y_max_:
            if (self.x_max_-self.x_min_)>self.max_x:self.max_x=self.x_max_-self.x_min_
            if (self.y_max_-self.y_min_)>self.max_y:self.max_y=self.y_max_-self.y_min_

            x_med_=int((self.x_max_-self.x_min_)/2.)
            y_med_=int((self.y_max_-self.y_min_)/2.)
            x_centro_=int((self.x_max_+self.x_min_)/2.)
            y_centro_=int((self.y_max_+self.y_min_)/2.)
            

            #frame= cv2.rectangle(frame, (self.x_min_,self.y_min_), (self.x_max_,self.y_max_), color, 3)
            if DataProcess['croping']==False:
                frame = frame[ y_centro_-y_med_:y_centro_+y_med_,x_centro_-x_med_:x_centro_+x_med_]######cropped
                DataProcess[camara_num]=[ y_centro_-y_med_,y_centro_+y_med_,x_centro_-x_med_,x_centro_+x_med_]
                #print(camara_num,DataProcess[camara_num])
        return frame,pts0,pts1


def Procesa_frames_(process_name,DataProcess,flag_ProcessCaptureDone):
    dedo_calculo=0##dedo indice
    DataProcess["index_write_{}".format(process_name)]=-1
    DataProcess["index_read_{}".format(process_name)]=-1
    write_log(DataProcess,process_name,"Proceso (Procesa_frames_) activado...")

    Procesa0=Procesamiento(hand='right',confidence=0.2,dinamyc_static=False)
    Procesa1=Procesamiento(hand='right',confidence=0.2,dinamyc_static=False)
    cont_calibracion=0
    cont=0
    #######R=Rotacion
    #######t=traslación
    try:
        R=DataProcess['calibracion'][0].R
        t=DataProcess['calibracion'][0].t
        matrix=DataProcess['calibracion'][0].matrix
    except:
        print("Matrices no encontradas!!")
        
    Get3D_=Get3D(DataProcess,process_name)
    cube_points=None
    DataProcess['cube_points']=[cube_points]

    user32 = ctypes.windll.user32
    screensize = user32.GetSystemMetrics(78), user32.GetSystemMetrics(79)
    window_weight_size=screensize[0]
    window_height_size=screensize[1]
    print(window_weight_size,window_height_size)
    write_log(DataProcess,process_name,"Tamaño de las ventanas detectado=({},{})".format(window_weight_size,window_height_size))
    while DataProcess['run']:
        if flag_ProcessCaptureDone.value:
           # read_log(DataProcess)
            frame0=DataProcess['frame0_read'].copy()
            frame1=DataProcess['frame1_read'].copy()


            DataProcess['frame0_procesado'],pts0,_=Procesa0.Procesa_Frame(0,frame0,DataProcess)    
            DataProcess['frame1_procesado'],_,pts1=Procesa1.Procesa_Frame(1,frame1,DataProcess)    
            if len(pts0)>0 and len(pts1)>0:
                
                
                


                ##EN CASO DE QUE NO EXISTA ARCHIVO INICIAL PREVIO DE CALIBRACIÓN DE POSICION DE LAS CAMARAS Calibracion_Inicial.npy  SE GENERARIA AQUÍ
                if DataProcess['Calibracion_inicial']==False:
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
                        
                        #DataProcess['Calibracion_inicial']=True
                elif DataProcess['Calibracion_Vectores_xy_teclado_mouse']==False:
                    pts3d=GetTriangulatedPts(pts0,pts1,matrix,R,t,cv2.triangulatePoints)
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
                    for _ in range(3,-1,-1):
                        texto="Captura {} en {}seg.".format(cont_calibracion,_)
                        write_log(DataProcess,process_name,texto)
                        print(texto,end="\r")
                        time.sleep(1)
                        
                    if cont_calibracion>=3:
                        DataProcess['Calibracion_Vectores_xy_teclado_mouse']=True
                        datos3d=np.array([{'pts3d':pts3d_}])
                        np.save('calibracion\\Calibracion_Vectores_xy_teclado_mouse.npy',datos3d)#,dtype=object))
                        print(pts3d_)   

                        #Get3D_.Vectores_base=pts3d_.copy()

                        DataProcess['run']=False
                        DataProcess['exit']=True     
                else:
                    pts3d=GetTriangulatedPts(pts0,pts1,matrix,R,t,cv2.triangulatePoints)
                    cube_points=Get3D_.Rotate_Translate_3D(pts3d)#"2 Manos detectadas"
    #                DataProcess['log_pos_cube_xyz_']=(cube_points[0][0][0],cube_points[0][1][0],cube_points[0][2][0])
                    DataProcess['cube_points']=[cube_points]
                    Determina_Acciones_mano(DataProcess)
                    
                    # x_size=abs(cube_points[0][0][0]-cube_points[1][0][0])##componente x
                    # y_size=abs(cube_points[2][1][0]-cube_points[0][1][0])##componente x
                    x_tmp=cube_points[3+dedo_calculo][0][0]#-cube_points[0][0][0]
                    y_tmp=cube_points[3+dedo_calculo][1][0]#-cube_points[0][1][0]
                    z_tmp=cube_points[3+dedo_calculo][2][0]



                    # x_tmp=cube_points[2][0][0]#-cube_points[0][0][0]
                    # y_tmp=cube_points[2][1][0]#-cube_points[0][1][0]
                    # z_tmp=cube_points[2][2][0]


                    #print(x_tmp,y_tmp,z_tmp)


                    # print("(",cube_points[0][0][0],cube_points[0][1][0],cube_points[0][2][0],")",
                    #       "(",cube_points[1][0][0],cube_points[1][1][0],cube_points[1][2][0],")",
                    #       "(",cube_points[2][0][0],cube_points[2][1][0],cube_points[2][2][0],")",
                    #       "(",cube_points[3+dedo_calculo][0][0],cube_points[3+dedo_calculo][1][0],cube_points[3+dedo_calculo][2][0],")")

                    #print(cube_points[0][0][0],cube_points[1][0][0],cube_points[0][1][0],cube_points[2][1][0])

                    # x=x_tmp*window_weight_size/x_size
                    # y=y_tmp*window_height_size/y_size
                    x=x_tmp*100
                    y=y_tmp*100
                    z=z_tmp*100


                    # if x<0:x=0
                    # if x>=window_weight_size:x=window_weight_size-1
                    # if y<0:y=0
                    # if y>=window_height_size:y=window_height_size-1



                    #DataProcess['log_Procesa_frames_']="x={:.3f} y={:.3f} z={:.3f}".format(x,y,posxyz[2])#max_x=36,max_y=-8,z=0
                    DataProcess['log_Procesa_frames_']=[x,y,z]
                    DataProcess['cube_points']=cube_points
                    #print(posxyz)         

            else:
                pass
                # if len(pts0)>0 or len(pts1)>0:
                #     DataProcess['log_Procesa_frames_']="1 Mano detectadas"
                # else:
                #     DataProcess['log_Procesa_frames_']="..."
            
            ##LIBERA frame_read PARA NUEVA CAPTURA mediante flag_ProcessCaptureDone
            flag_ProcessCaptureDone.value=False



      



