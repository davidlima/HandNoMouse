import cmath
from multiprocessing import Process,Manager,Value,Array
import mediapipe as mp
import cv2
import numpy as np
import time
import ctypes
from math import sqrt
from video import Captura_video_
#from calc3D import GetTriangulatedPts,Get3D
import calc3D
from extras import write_log,Determina_Acciones_mano
#from calibracion import Calibracion_inicial_,Calibracion_Vectores_xy_teclado_mouse_
import calibracion as calib_


tam_video_x=640
tam_video_y=480
# tam_video_x=1920
# tam_video_y=1080


def MainProcess_(camaras,DataProcess,flag_Show,calibracion):
    
    # T0_=threading.Thread(target=Procesa_video_, args=(0,[self.arg_])).start()
    # T1_=threading.Thread(target=Procesa_video_, args=(1,[self.arg_])).start()
    
    DataProcess['log_Procesa_3D_']=[]
    # DataProcess['log_Procesa_capture_']=""
    flag_VideoProcessCaptureDone_0=Value('i',False)
    flag_VideoProcessCaptureDone_1=Value('i',False)
    
    ############Cuando se sincronizan las capturas se activa flag_VideoProcessCaptureDone_01 para comenzar a trabajar en el analisis de Procesa_3D_################
    flag_VideoProcessCaptureDone_01=Value('i',False)
    ########################################################################################################################################################
    
    ############Durante el proceso de almacenar los datos para analizarlos en Procesa_3D_ se activa el flag_ProcessAnalisisReading para no machacar los datos por nuevos capturados######
    flag_ProcessAnalisisReading=Value('i',False)
    ########################################################################################################################################################
    
    ############Cuando finaliza el analisis de ambas camaras se activa flag_Frames_Procesados_Done para adquirir nuevos datos en Procesa_3D_##############
    flag_Frames_Procesados_Done=Value('i',False)
    ########################################################################################################################################################
 

    


    P0_=Process(target=Captura_video_, args=(camaras[0],0,DataProcess,flag_VideoProcessCaptureDone_0)).start()
    P1_=Process(target=Captura_video_, args=(camaras[1],1,DataProcess,flag_VideoProcessCaptureDone_1)).start()
    #P2_=main.py
    P3_=Process(target=Sincroniza_frames_, args=(3,DataProcess,flag_VideoProcessCaptureDone_0,flag_VideoProcessCaptureDone_1,flag_VideoProcessCaptureDone_01,flag_Show,flag_ProcessAnalisisReading)).start()
    if calibracion==None:
        P4_=Process(target=Procesa_3D_, args=(4,DataProcess,flag_VideoProcessCaptureDone_01,flag_Frames_Procesados_Done)).start()
        P5_=Process(target=Procesa_Analisis_Frames_, args=(5,DataProcess,flag_VideoProcessCaptureDone_01,flag_ProcessAnalisisReading)).start()
    elif calibracion=='Calibracion_inicial_':
        P4_=Process(target=calib_.Calibracion_inicial_, args=(4,DataProcess,flag_VideoProcessCaptureDone_01)).start()
    elif  calibracion=='Calibracion_Vectores_xy_teclado_mouse_':
        P4_=Process(target=calib_.Calibracion_Vectores_xy_teclado_mouse_, args=(4,DataProcess,flag_VideoProcessCaptureDone_01)).start()
    elif calibracion=='Calibracion_cropping_':
        P4_=Process(target=calib_.Calibracion_cropping_, args=(4,DataProcess,flag_VideoProcessCaptureDone_01)).start()

    
    DataProcess['core2estado']="Core 3: ON -->50% Proceso:Main(...)"##core3=core2
    # t_start = time.time()
    ################SINCRONIZACION DE LAS CAPTURAS
    while DataProcess['run']:
        pass
        # if flag_ProcessAnalisisWork.value:
        #     flag_ProcessAnalisisWork.value=False
        #     DataProcess['frame0_read']=DataProcess['frame0'].copy()
        #     DataProcess['frame1_read']=DataProcess['frame1'].copy()
        
       
        #if flag_VideoProcessCaptureDone_0.value  and flag_VideoProcessCaptureDone_1.value:
        #     DataProcess['frame0_read']=DataProcess['frame0'].copy()
        #     DataProcess['frame1_read']=DataProcess['frame1'].copy()
        #     # t_end = time.time()
        #     # totalTime = t_end - t_start
        #     # t_start=t_end

            # flag_ProcessAnalisisWork.value=True###
            # while flag_ProcessAnalisisWork.value:
            #     time.sleep(1/300)

        #     flag_Show.value=True
        #     flag_VideoProcessCaptureDone_0.value=False
        #     flag_VideoProcessCaptureDone_1.value=False

def Sincroniza_frames_(process_name,DataProcess,flag_VideoProcessCaptureDone_0,flag_VideoProcessCaptureDone_1,flag_VideoProcessCaptureDone_01,flag_Show,flag_ProcessAnalisisWorkReading):

    DataProcess["index_write_{}".format(process_name)]=-1
    DataProcess["index_read_{}".format(process_name)]=-1
    write_log(DataProcess,process_name,"Proceso (Sincroniza_frames_) activado...")
    t_start = t_start2=time.time()
    totalTime=0
    contador=0
    TimeWorking=0
    TimeSleeping=0
    while DataProcess['run']:
        if flag_VideoProcessCaptureDone_0.value and flag_VideoProcessCaptureDone_1.value and flag_ProcessAnalisisWorkReading.value==False:
            DataProcess['frame0_read']=DataProcess['frame0'].copy()
            DataProcess['frame1_read']=DataProcess['frame1'].copy()

            ###############calculo de fps####################
            t_end2= time.time()
            contador+=1
            totalTime += t_end2 - t_start2
            t_start2=t_end2
            if totalTime>1:
              #  print("{} {}FPS ".format(totalTime,contador))
                DataProcess['FPS']=contador
                
                contador=totalTime=0
            flag_VideoProcessCaptureDone_01.value=True###
           
            flag_Show.value=True
            flag_VideoProcessCaptureDone_0.value=False
            flag_VideoProcessCaptureDone_1.value=False
        t_end = time.time()
        TimeWorking += t_end - t_start
        t_start = t_end
        time.sleep(1/300)
        t_end = time.time()
        TimeSleeping += t_end - t_start
        t_start = t_end
        if (TimeSleeping+TimeWorking)>1:
            DataProcess['core{}'.format(process_name)]=TimeWorking*100/(TimeSleeping+TimeWorking)
            try:
                DataProcess['core{}estado'.format(process_name)]="Core {}: ON -->{:3.1f}% {}FPS Proceso:Sincroniza_frames_(...)".format(process_name+1,DataProcess['core{}'.format(process_name)],DataProcess['FPS'])
            except:
                pass
            TimeSleeping=0
            TimeWorking=0

class Procesamiento():  
    def __init__(self,hand='right',confidence=0.9,dinamyc_static=False):
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils ####PARA DIBUJAR SOLUCIONES
        self.hands=self.mp_hands.Hands(static_image_mode=dinamyc_static,max_num_hands=2,min_detection_confidence=confidence)###min_tracking_confidence=0.5
        self.max_x=self.max_y=0
        self.x_min_0=self.x_min_1=tam_video_x
        self.y_min_0=self.y_min_1=tam_video_y
        self.x_max_0=self.x_max_1=0
        self.y_max_0=self.y_max_1=0

 
    def Procesa_Frames_Calibracion_(self,camara_num,frame,DataProcess):

        frame=cv2.flip(frame,1)
        if DataProcess['croping']:
            if camara_num==0:croping=DataProcess['croping0']
            else:croping=DataProcess['croping1']
            frame = frame[ croping[0]:croping[1],croping[2]:croping[3]]
        
        if camara_num==0:
            self.x_min_=self.x_min_0
            self.y_min_=self.y_min_0
            self.x_max_=self.x_max_0
            self.y_max_=self.y_max_0
        else:
            self.x_min_=self.x_min_1
            self.y_min_=self.y_min_1
            self.x_max_=self.x_max_1
            self.y_max_=self.y_max_1

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
        #if results.multi_hand_landmarks is not None:# and not run[0]:
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
                        frame=cv2.circle(frame,(int((_.x*tam_x)),int((_.y*tam_y))),2,(255,0,255),2)                        
                        
                    pts0=np.array(pts0)
                    self.x_min=int(pts0[:,0].min())
                    self.x_max=int(pts0[:,0].max())
                    self.y_min=int(pts0[:,1].min())
                    self.y_max=int(pts0[:,1].max())
                        #frame=cv2.circle(frame,(int(_[0]),int(_[1])),2,(255,255,255),2)
                else:
                    for _ in results.multi_hand_landmarks[tmp].landmark:
                        pts1.append([croping[2]+(_.x*tam_x),croping[0]+(_.y*tam_y)])##escala y añade parámetros del croping extraido para adaptarlo a las dimensiones de captura 1920x1080
                        frame=cv2.circle(frame,(int((_.x*tam_x)),int((_.y*tam_y))),2,(255,0,255),2) 
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
                

                #frame= cv2.rectangle(frame, (self.x_min_,self.y_min_), (self.x_max_,self.y_max_), (255,255,255), 2)
            # frame= cv2.rectangle(frame, (x_centro_-x_med_, y_centro_-y_med_), (x_centro_+x_med_,y_centro_+y_med_), (255,255,255), 2)
                if DataProcess['croping']==False:
                    
                    frame = frame[ y_centro_-y_med_:y_centro_+y_med_,x_centro_-x_med_:x_centro_+x_med_]######cropped
                    DataProcess[camara_num]=[ y_centro_-y_med_,y_centro_+y_med_,x_centro_-x_med_,x_centro_+x_med_]
                    #print(camara_num,DataProcess[camara_num])
            if camara_num==0:
                self.x_min_0=self.x_min_
                self.y_min_0=self.y_min_
                self.x_max_0=self.x_max_
                self.y_max_0=self.y_max_
            else:
                self.x_min_1=self.x_min_
                self.y_min_1=self.y_min_
                self.x_max_1=self.x_max_
                self.y_max_1=self.y_max_
        return frame,pts0,pts1

    def Procesa_Frame_(self,process_name,camara_num,DataProcess,flag_Procesa_Frame_,pts_,frame_procesado_):
        TimeWorking=0
        TimeSleeping=0
        t_start = time.time()
        #print("a->",process_name,camara_num)
        DataProcess["index_write_{}".format(process_name)]=-1
        DataProcess["index_read_{}".format(process_name)]=-1
        write_log(DataProcess,process_name,"Proceso (Procesa_Frame_) activado...")
        while DataProcess['run']:
            if flag_Procesa_Frame_.value==False:
                t_end = time.time()
                TimeSleeping += t_end - t_start
                t_start = t_end
                try:
                    if camara_num==0:frame=DataProcess['frame0'].copy()
                    else:frame=DataProcess['frame1'].copy()

                    frame=cv2.flip(frame,1)
                    if DataProcess['croping']:
                        if camara_num==0:croping=DataProcess['croping0']
                        else:croping=DataProcess['croping1']
                        frame = frame[ croping[0]:croping[1],croping[2]:croping[3]]
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
                    pts=[]
                    # if results.multi_hand_landmarks is not None:
                    #         for hand_landmarks in results.multi_hand_landmarks:
                    #             self.mp_drawing.draw_landmarks(frame,hand_landmarks,self.mp_hands.HAND_CONNECTIONS)####################################cambiar dibujos de manos!!
                    if results.multi_hand_landmarks is not None:# and not run[0]:
                        if results.multi_handedness[0].classification[0].label=='Right':
                            tmp=0
                        elif len(results.multi_hand_landmarks)>1 and results.multi_handedness[1].classification[0].label=='Right':
                            tmp=1
                        else:
                            tmp=-1
                        if tmp!=-1:
                            for _ in results.multi_hand_landmarks[tmp].landmark:
                                x=croping[2]+(_.x*tam_x)
                                y=croping[0]+(_.y*tam_y)
                                pts.append([x,y])##escala y añade parámetros del croping extraido para adaptarlo a las dimensiones de captura 1920x1080 o 640x480
                                
                            
                            d=dist(pts[0],pts[9])
                            x=(pts[0][0]-croping[2]+pts[9][0]-croping[2])/2
                            y=(pts[0][1]-croping[0]+pts[9][1]-croping[0])/2
                            color=(255,255,255)
                            frame=cv2.circle(frame,(int(x),int(y)),int(d/2),color,1)
                            # pts[0][0]=x+croping[2]#############centro de la mano
                            # pts[0][1]=x+croping[0]
                            x=pts[4][0]-croping[2]
                            y=pts[4][1]-croping[0]
                            frame=cv2.circle(frame,(int(x),int(y)),2,color,2)
                            x=pts[8][0]-croping[2]
                            y=pts[8][1]-croping[0]
                            frame=cv2.circle(frame,(int(x),int(y)),2,color,2)
                            x=pts[12][0]-croping[2]
                            y=pts[12][1]-croping[0]
                            frame=cv2.circle(frame,(int(x),int(y)),2,color,2)
                            x=pts[16][0]-croping[2]
                            y=pts[16][1]-croping[0]
                            frame=cv2.circle(frame,(int(x),int(y)),2,color,2)
                            x=pts[20][0]-croping[2]
                            y=pts[20][1]-croping[0]
                            frame=cv2.circle(frame,(int(x),int(y)),2,color,2)
                            pts=np.array(pts)
                    #print("pts_",pts_.value)
                    DataProcess[pts_]=pts.copy()
                    #print("frame_procesado_",frame_procesado_.value)
                    DataProcess[frame_procesado_]=frame.copy()

                except:
                    DataProcess[pts_]=[]
                    DataProcess[frame_procesado_]=[]

                flag_Procesa_Frame_.value=True
                t_end = time.time()
                TimeWorking += t_end - t_start
                t_start = t_end
                if (TimeSleeping+TimeWorking)>1:
                    DataProcess['core{}'.format(process_name)]=TimeWorking*100/(TimeSleeping+TimeWorking)
                    DataProcess['core{}estado'.format(process_name)]="Core {}: ON -->{:3.1f}% Proceso:Procesa_Frame_({})".format(process_name+1,DataProcess['core{}'.format(process_name)],camara_num)
                    TimeSleeping=0
                    TimeWorking=0
                    
# def Get_Better_pts(pts1,pts2):
#     if len(pts1)>0 and len(pts2)>0:
#         for _ in range(len(pts1)):
def dist(a,b):
    tmp1=a[0]-b[0]          
    tmp1*=tmp1
    tmp2=a[1]-b[1]          
    tmp2*=tmp2
    return sqrt(tmp1+tmp2)
        
                
def ProcesaFrame_Process(process_name,camara_num,DataProcess,flag_Procesa_Frame_,pts_,frame_procesado_,confidence=0.2,dynamic_state=False):
    Procesa=Procesamiento(hand='right',confidence=confidence,dinamyc_static=dynamic_state)
    Procesa.Procesa_Frame_(process_name,camara_num,DataProcess,flag_Procesa_Frame_,pts_,frame_procesado_)
            

def Procesa_Analisis_Frames_(process_name,DataProcess,flag_VideoProcessCaptureDone_01,flag_ProcessAnalisisReading):
    TimeWorking=0
    TimeSleeping=0
    t_start = time.time()
    DataProcess["index_write_{}".format(process_name)]=-1
    DataProcess["index_read_{}".format(process_name)]=-1
    write_log(DataProcess,process_name,"Proceso (Procesa_Analisis_Frames_) activado...")
    
#    Procesa1=Procesamiento(hand='right',confidence=0.2,dinamyc_static=False)
    
    
    # flag_Frames_Procesados=Value('i',False)
    flag_Procesa_Frame_0_0=Value('i',False)
    flag_Procesa_Frame_1_0=Value('i',False)
    flag_Procesa_Frame_0_1=Value('i',False)
    flag_Procesa_Frame_1_1=Value('i',False)

    
    confidence=0.2
    dynamic_state=False
 
    P6_=Process(target=ProcesaFrame_Process, args=(6,0,DataProcess,flag_Procesa_Frame_0_0,"pts0_0","frame0_0procesado_",confidence,dynamic_state)).start()
    pts_='pts1'
    frame_procesado_='frame1_procesado'
    P7_=Process(target=ProcesaFrame_Process, args=(7,1,DataProcess,flag_Procesa_Frame_1_0,"pts1_0","frame1_0procesado_",confidence,dynamic_state)).start()
    confidence=0.9
    dynamic_state=True
    P8_=Process(target=ProcesaFrame_Process, args=(8,1,DataProcess,flag_Procesa_Frame_0_1,"pts0_1","frame0_1procesado_",confidence,dynamic_state)).start()
    P9_=Process(target=ProcesaFrame_Process, args=(9,1,DataProcess,flag_Procesa_Frame_1_1,"pts1_1","frame1_1procesado_",confidence,dynamic_state)).start()
    flag_Frames_Procesados=False
    contador=totalTime=last_contador=0
    t_start2= time.time()
    while DataProcess['run']:
        # if flag_Procesa_Frame_0.value==True:
        #     pts0=DataProcess['pts0'].copy()
        #     frame0_procesado=DataProcess['frame0_procesado']
        #     flag_Procesa_Frame_0.value=False
        
        # if flag_Procesa_Frame_1.value==True:
        #     pts1=DataProcess['pts1'].copy()
        #     frame1_procesado=DataProcess['frame1_procesado']
        #     flag_Procesa_Frame_1.value=False
        
         
        
        if flag_VideoProcessCaptureDone_01.value: 
            if flag_Frames_Procesados==False:#################################################
                t_end = time.time()
                TimeSleeping += t_end - t_start
                t_start = t_end
                flag_ProcessAnalisisReading.value==True
                DataProcess['frame0']=DataProcess['frame0_read'].copy()
                DataProcess['frame1']=DataProcess['frame1_read'].copy()
                flag_ProcessAnalisisReading.value==False
                while DataProcess['run'] and flag_Frames_Procesados==False:
                    if flag_Procesa_Frame_0_0.value and flag_Procesa_Frame_1_0.value:
                        if flag_Procesa_Frame_0_1.value and flag_Procesa_Frame_1_1.value:
                            pts0_0=DataProcess['pts0_0'].copy()
                            frame0_0procesado=DataProcess['frame0_0procesado_']
                            DataProcess['pts0_0']=pts0_0.copy()
                            DataProcess['frame0_0procesado']=frame0_0procesado.copy()
                            pts1_0=DataProcess['pts1_0'].copy()
                            frame1_0procesado=DataProcess['frame1_0procesado_']
                            DataProcess['pts1_0']=pts1_0.copy()
                            DataProcess['frame1_0procesado']=frame1_0procesado.copy()

                            pts0_1=DataProcess['pts0_1'].copy()
                            frame0_1procesado=DataProcess['frame0_1procesado_']
                            DataProcess['pts0_1']=pts0_1.copy()
                            DataProcess['frame0_1procesado']=frame0_1procesado.copy()
                            pts1_1=DataProcess['pts1_1'].copy()
                            frame1_1procesado=DataProcess['frame1_1procesado_']
                            DataProcess['pts1_1']=pts1_1.copy()
                            DataProcess['frame1_1procesado']=frame1_1procesado.copy()
                            
                            
                            DataProcess['pts0']=pts0_0.copy()
                            DataProcess['frame0_procesado']=frame0_0procesado.copy()
                            DataProcess['pts1']=pts1_0.copy()
                            DataProcess['frame1_procesado']=frame1_0procesado.copy()
                            
                            
                            # d=dist(pts[0],pts[9])
                            # x=(pts[0][0]-croping[2]+pts[9][0]-croping[2])/2
                            # y=(pts[0][1]-croping[0]+pts[9][1]-croping[0])/2
                            # color=(255,255,255)
                            # frame=cv2.circle(frame,(int(x),int(y)),int(d/2),color,1)
                        
                        
                        
                        
                            flag_Procesa_Frame_0_0.value=False
                            flag_Procesa_Frame_1_0.value=False
                            flag_Procesa_Frame_0_1.value=False
                            flag_Procesa_Frame_1_1.value=False

                        flag_Frames_Procesados=True
                        #flag_Frames_Procesados_Done.value=True
                ###############calculo de fps####################
                t_end2= time.time()
                contador+=1
                totalTime += t_end2 - t_start2
                t_start2=t_end2
                if totalTime>1:
                    last_contador=contador
                    contador=totalTime=0
                flag_Frames_Procesados=False
                t_end = time.time()
                TimeWorking += t_end - t_start
                t_start = t_end
                if (TimeSleeping+TimeWorking)>1:
                    DataProcess['core{}'.format(process_name)]=TimeWorking*100/(TimeSleeping+TimeWorking)
                    try:
                        DataProcess['core{}estado'.format(process_name)]="Core {}: ON -->{:3.1f}% {}FPS Proceso:Procesa_Analisis_Frames_(...)".format(process_name+1,DataProcess['core{}'.format(process_name)],last_contador)
                    except:
                        pass
                    TimeSleeping=0
                    TimeWorking=0   
                        
                        # DataProcess['frame0_procesado'],pts0,_=Procesa0.Procesa_Frame(0,frame0,DataProcess)    
                        # DataProcess['frame1_procesado'],_,pts1=Procesa1.Procesa_Frame(1,frame1,DataProcess)    

def Procesa_3D_(process_name,DataProcess,flag_VideoProcessCaptureDone_01,flag_Frames_Procesados_Done):

    dedo_calculo=0##dedo indice
    DataProcess["index_write_{}".format(process_name)]=-1
    DataProcess["index_read_{}".format(process_name)]=-1
    write_log(DataProcess,process_name,"Proceso (Procesa_3D_) activado...")
    
    
    

    t_start = time.time()
    
    TimeWorking=0
    TimeSleeping=0
   
    try:
        R=DataProcess['calibracion'][0].R #######R=Rotacion
        t=DataProcess['calibracion'][0].t #######t=traslación
        matrix=DataProcess['calibracion'][0].matrix
    except:
        print("Matrices no encontradas!!")
        write_log(DataProcess,process_name,"Error (Procesa_3D_) Matrices no encontradas!!...")
        
    Get3D_=calc3D.Get3D(DataProcess,process_name)
    cube_points=None
    DataProcess['cube_points']=[cube_points]

    user32 = ctypes.windll.user32
    screensize = user32.GetSystemMetrics(78), user32.GetSystemMetrics(79)
    DataProcess['weight']=window_weight_size=screensize[0]
    DataProcess['height']=window_height_size=screensize[1]
    print(window_weight_size,window_height_size)
    write_log(DataProcess,process_name,"Tamaño de las ventanas detectado=({},{})".format(window_weight_size,window_height_size))
    x_tmp=y_tmp=z_tmp=0
    contador=totalTime=last_contador=0
    t_start2= time.time()
    while DataProcess['run']:
        #if flag_Frames_Procesados_Done.value:
        try:
            t_end = time.time()
            TimeSleeping += t_end - t_start
            t_start = t_end
            

            # frame0=DataProcess['frame0_read'].copy()
            # frame1=DataProcess['frame1_read'].copy()
            # pts0=pts1=[]
            # DataProcess['frame0_procesado'],pts0,_=Procesa0.Procesa_Frame(0,frame0,DataProcess)    
            # DataProcess['frame1_procesado'],_,pts1=Procesa1.Procesa_Frame(1,frame1,DataProcess)    
            
            pts0=DataProcess['pts0'].copy()
            pts1=DataProcess['pts1'].copy()
            flag_Frames_Procesados_Done.value=False
            
            if len(pts0)>0 and len(pts1)>0:
                pts0=DataProcess['pts0']
                pts1=DataProcess['pts1']
                pts3d=calc3D.GetTriangulatedPts(pts0,pts1,matrix,R,t,cv2.triangulatePoints)


                try:
                    cube_points=Get3D_.Rotate_Translate_3D(pts3d)#"2 Manos detectadas"
    #                DataProcess['log_pos_cube_xyz_']=(cube_points[0][0][0],cube_points[0][1][0],cube_points[0][2][0])
                    DataProcess['cube_points']=[cube_points]
                    Determina_Acciones_mano(DataProcess)

                    
                    # x_size=abs(cube_points[0][0][0]-cube_points[1][0][0])##componente x
                    # y_size=abs(cube_points[2][1][0]-cube_points[0][1][0])##componente x
                    x_tmp=cube_points[3+dedo_calculo][0][0]#-cube_points[0][0][0]
                    y_tmp=cube_points[3+dedo_calculo][1][0]#-cube_points[0][1][0]
                    z_tmp=cube_points[3+dedo_calculo][2][0]
                except:
                    pass


                # x_tmp=cube_points[2][0][0]#-cube_points[0][0][0]
                # y_tmp=cube_points[2][1][0]#-cube_points[0][1][0]
                # z_tmp=cube_points[2][2][0]


                #print(x_tmp,y_tmp,z_tmp)


                x=-x_tmp*200
                y=-y_tmp*200
                z=z_tmp*10


                #DataProcess['log_Procesa_frames_']="x={:.3f} y={:.3f} z={:.3f}".format(x,y,posxyz[2])#max_x=36,max_y=-8,z=0
                DataProcess['log_Procesa_3D_']=[x,y,z]
                DataProcess['cube_points']=cube_points
                #print(posxyz)         

            else:
                pass
                # if len(pts0)>0 or len(pts1)>0:
                #     DataProcess['log_Procesa_frames_']="1 Mano detectadas"
                # else:
                #     DataProcess['log_Procesa_frames_']="..."
            ###############calculo de fps####################
            t_end2= time.time()
            contador+=1
            totalTime += t_end2 - t_start2
            t_start2=t_end2
            if totalTime>1:
                last_contador=contador
                contador=totalTime=0
            ##LIBERA frame_read PARA NUEVA CAPTURA mediante flag_ProcessAnalisisWork
            flag_VideoProcessCaptureDone_01.value=False
            t_end = time.time()
            TimeWorking += t_end - t_start
            t_start = t_end
            if (TimeSleeping+TimeWorking)>1:
                #print("CC")
                DataProcess['core{}'.format(process_name)]=TimeWorking*100/(TimeSleeping+TimeWorking)
                try:
                    DataProcess['core{}estado'.format(process_name)]="Core {}:ON -->{:3.1f}% {}FPS Proceso:Procesa_3D_(...)".format(process_name+1,DataProcess['core{}'.format(process_name)],last_contador)
                except:
                    pass
                TimeSleeping=0
                TimeWorking=0    
        except:
            pass
     ##EN CASO DE QUE NO EXISTA ARCHIVO INICIAL PREVIO DE CALIBRACIÓN DE POSICION DE LAS CAMARAS Calibracion_Inicial.npy  SE GENERARIA AQUÍ



            



