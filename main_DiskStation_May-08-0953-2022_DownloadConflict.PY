import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsDropShadowEffect,QSystemTrayIcon
from PyQt5.QtCore import  QPropertyAnimation,QEasingCurve
from PyQt5.QtGui  import QColor,QIcon
#from PyQt5.QtGui import * 
#from PyQt5.QtWidgets import * 
from PyQt5 import QtCore, QtWidgets,QtGui
from PyQt5.QtWidgets import QFileDialog,QMessageBox
from PyQt5.Qt import Qt

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import plotly.graph_objects as go

from PyQt5.uic import loadUi
import threading
import time
from calc3D import Calculo_3D_
from procesos import MainProcess_
from video import ZoomClass
import numpy as np
import multiprocessing as mp
from PyQt5.QtCore import QTimer,QDateTime
from multiprocessing import Process,Manager,Value, parent_process
import cv2
from PyQt5.QtGui import QImage,QPixmap
from imutils.video import FPS
from imutils.video import FPS
import config
import pyautogui
from extras import read_log,write_log

from ctypes import pythonapi


class VentanaPrincipal(QMainWindow):
    
    arg_={'run':True}
    
    cpu_count=0
    def __init__(self):
        global cpu_count
        
        self.cont_idle=0
        self.cont_timer=0
        self.last_visible=False
        self.path='D:\\Python\\Proyecto4\\imagenes\\'
        super(VentanaPrincipal, self).__init__()
        loadUi(self.path+'menu1.ui', self)
        self.arg_.update({'self':self})
        self.arg_.update({'visible':True})
        self.setWindowIcon(QIcon(self.path+'hand2.png'))    
        self.main_proceso=2##proceso equivalente utilizado para almacenar texto y compartir entre multiples procesos

        self.trayIcon = QSystemTrayIcon(QIcon(self.path+'hand2.png'), self)
        self.trayIcon.activated.connect(self.control_bt_systemtrayicon)
        self.trayIcon.show()
        self.trayIcon.setToolTip("TFM VIU HandNoMouse")

        
         

 
        cpu_count = mp.cpu_count()
        process = list(range(cpu_count))    ##numero de nucleos disponibles!!                                                                                                                                                
        process=dict.fromkeys(process, False)

        self.totalOn=0###Tiempo total de ejecución
        self.zoom_=ZoomClass()##usado para realizar zoom sobre toda la pantalla
        self.zoom_check=False
        self.x_final=self.x_last=0
        self.y_final=self.y_last=0
        self.z_final=self.z_last=0
        self.xx=self.yy=self.zz=0

        self.DataProcess = Manager() .dict()
        self.FlagProcess = Manager() .dict()
        #self.DataProcess['exit']=False

        self.DataProcess["index_write_{}".format(self.main_proceso)]=-1
        self.DataProcess["index_read_{}".format(self.main_proceso)]=-1

        self.DataProcess["index_write_{}".format(100)]=-1##el proceso 100 es donde se copian todos los textos de todos los procesos
        self.DataProcess["index_read_{}".format(100)]=-1

        write_log(self.DataProcess,self.main_proceso,"Iniciando aplicación...")

        self.tmp=0


        
        self.visualizador3d=Canvas_(self,self.DataProcess)
        self.page6_layout2.addWidget(self.visualizador3d)
        

        

        self.calibracion=Calculo_3D_(self.DataProcess,self.main_proceso)
        self.DataProcess['Calibracion_inicial']=self.calibracion.LoadCalibracion(self)
        self.DataProcess['calibracion']=[self.calibracion]
        self.DataProcess['Calibracion_Vectores_xy_teclado_mouse']=self.calibracion.calibracion_recuperada
        
        #self.calibracion.LoadCalibracion_xy()

        try:
            
            t=np.load("calibracion\\Calibración_size_cam.npy",allow_pickle=True)
            self.DataProcess['croping0']=t[0]['0']
            self.DataProcess['croping1']=t[0]['1']
            self.DataProcess['croping']=True
            write_log(self.DataProcess,self.main_proceso,"Lectura del archivo Calibración_size_cam.npy correcto")
        except:
            QMessageBox.about(self, "Archivo Calibración_size_cam.npy no encontrado!", "Se requiere ir al apartado de calibración para generar un nuevo archivo")
            write_log(self.DataProcess,self.main_proceso,"Error leyendo archivo Calibración_size_cam.npy")
            self.DataProcess['croping']=False

        #self.DataProcess['log1']=['']
        

        self.flag_MainProcess=False#Value('i',False)
        self.flag_ProcessCaptureDone_0=False#Value('i',-1)
        self.flag_ProcessCaptureDone_1=False#Value('i',-1)
        self.flag_ProcessCaptureDone=False#Value('i',False)
        self.flag_ProcessAnalisisDone_0=False#Value('i',-1)
        self.flag_ProcessAnalisisDone_1=False#Value('i',-1)
        self.flag_ProcessAnalisisDone=False#Value('i',False)
        self.flag_Show=Value('i',False)

        self.FlagProcess['flag_MainProcess']=self.flag_MainProcess
        self.FlagProcess['flag_ProcessCaptureDone_0']=self.flag_ProcessCaptureDone_0
        self.FlagProcess['flag_ProcessCaptureDone_1']=self.flag_ProcessCaptureDone_1
        self.FlagProcess['flag_ProcessCaptureDone']=self.flag_ProcessCaptureDone
        self.FlagProcess['flag_ProcessAnalisisDone_0']=self.flag_ProcessAnalisisDone_0
        self.FlagProcess['flag_ProcessAnalisisDone_1']=self.flag_ProcessAnalisisDone_1
        self.FlagProcess['flag_ProcessAnalisisDone']=self.flag_ProcessAnalisisDone
        #self.FlagProcess['flag_Show']=Value('i',False)#self.flag_Show

        ###tooltips2
        self.page1_bt1.setToolTip("<h3>Inicia la ejecución de las 2 cámaras.<u>No ejecutar si no se dispone de los archivos de calibración necesarios... </u><\h3>")
        self.page1_ck1.setToolTip("<h3>Permite la visualización en tiempo real de las imágenes<\h3>")
        self.page1_ck_procesado.setToolTip("<h3>Permite la visualización del procesado en tiempo real de las imágenes<\h3>")
        self.page1_cBox0.setToolTip("<h3>Se debe seleccionar la cámara que se encuentre en la parte de la izquierda<\h3>")
        self.page1_cBox1.setToolTip("<h3>Se debe seleccionar la cámara que se encuentre en la parte de la derecha<\h3>")
        self.bt1.setToolTip("<h3>Inicio<\h3>")
        self.bt2.setToolTip("<h3>Ubicación de archivos necesarios para la calibración y funcionamiento del programa<\h3>")
        self.bt3.setToolTip("<h3>Visualización del estado de los diferentes nucleos/precesos trabajando<\h3>")
        self.bt4.setToolTip("<h3>Log de cada paso que se ejecuta dentro de la aplicación<\h3>")
        self.bt5.setToolTip("<h3>Calibración para sincronizar cámaras, ChessBoard, planos de funcionamiento,...<\h3>")
        self.page5_bt1.setToolTip("<h3>Sincronización cámaras 3D. Se requiere captar unas 100 imágenes de forma sincronizada para poder encontrar la matriz que sincronice ambas cámaras.<\h3>")
        self.page5_bt2.setToolTip("<h3>Detección plano xy (ubicación teclado y mouse).Se requiere mover la mano en contacto con la mesa en la ubicación habitual del teclado y del mouse para calibrar la zona de trabajo (x,y,z=0)<\h3>")
        self.page5_bt3.setToolTip("<h3>Detección plano xy (ubicación pantalla táctil). Se requiere mover el dedo indice en contacto con la pantalla para calibrar la zona de trabajo (x,y,z=0)<\h3>")
        self.page5_bt4.setToolTip("<h3>Afinar tamaño de captura de cada cámara. Se precisan movimientos en la zona de trabajo para eliminar la visión sobrante panorámica de la cámara<\h3>")
        self.page5_bt5.setToolTip("<h3>Chess Board Matrix. Imágenes previamente guardadas en el directorio de calibración son analizadas para encontrar la matriz propia de las cámaras<\h3>")


        



        
        
        self.arg_.update({'core':process})
        self.arg_.update({'flag_DoThread':[False,False]})     
        self.page3_lb1.setText("Núm Cores disponibles: {}".format(cpu_count))
        self.bt1.setEnabled(False)
        self.bt_last=self.bt1
        # timer = QtCore.QTimer()
        # timer.timeout.connect(self.showTime)
        # timer.start(1000)
        self.t_start = time.time()
        self.fps=FPS().start()
        self.fps2=FPS().start()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.fn_timer)
        self.timer.start(10)
        # self.timerEvent.start(1000)
        # self.timer.timeout.connect(self.showTime)
        #eliminar barra y de titulo - opacidad
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setWindowOpacity(1)
        self.setWindowTitle("HandNoMouse")
        self.bt_restaurar.hide()
        self.page1_ck_DoSomething.hide()
        self.arg_.update({'window_width':self.page1_lb0.width()})
        #print("width=",self.arg_['window_width'],self.page1_lb0.height())
		#menu lateral
        self.bt_menu.clicked.connect(self.mover_menu)
        #SizeGrip
        self.gripSize = 10
        self.grip = QtWidgets.QSizeGrip(self)
        self.grip.resize(self.gripSize, self.gripSize)

        self.tmp=0

        
        # mover ventana
        self.frame_superior.mouseMoveEvent = self.mover_ventana
        self.bt1.clicked.connect(self.fn_page1)#lambda: self.stackedWidget.setCurrentWidget(self.page1))
        self.bt2.clicked.connect(self.fn_page2)
        self.bt3.clicked.connect(self.fn_page3)
        self.bt4.clicked.connect(self.fn_page4)
        self.bt5.clicked.connect(self.fn_page5)
        self.bt6.clicked.connect(self.fn_page6)
        self.bt7.clicked.connect(self.fn_page7)

        ####PAGE1
        self.page1_bt1.clicked.connect(self.fn_page1_bt1)
        self.page1_bt2.clicked.connect(self.fn_page1_bt2)
        self.page1_ck1.stateChanged.connect(self.fn_page1_ck1)
        self.page1_ck_zoom.clicked.connect(self.fn_page1_ck_zoom)
        self.page1_ck_DoSomething.clicked.connect(self.fn_page1_ck_DoSomething)
        
        ####PAGE2
        self.page2_bt1.clicked.connect(self.fn_page2_bt1)

        ####PAGE5
        self.page5_bt1.clicked.connect(self.fn_page5_bt1)        
        self.page5_bt2.clicked.connect(self.fn_page5_bt2)        
        self.page5_bt3.clicked.connect(self.fn_page5_bt3)        
        self.page5_bt4.clicked.connect(self.fn_page5_bt4)        
        self.page5_bt5.clicked.connect(self.fn_page5_bt5)        
        
        
        
        self.bt_minimizar.clicked.connect(self.control_bt_minimizar)		
        self.bt_restaurar.clicked.connect(self.control_bt_normal)
        self.bt_maximizar.clicked.connect(self.control_bt_maximizar)
        self.bt_cerrar.clicked.connect(self.control_bt_exit)#self.close())



        
    def keyPressEvent(self,event):
        #print("OK.",event.text())#event.key())
        pass
    def fn_page1(self):
        self.stackedWidget.setCurrentWidget(self.page1)
        self.bt1.setEnabled(False)
        self.bt_last.setEnabled(True)
        self.bt_last=self.bt1
    def fn_page2(self):
        self.stackedWidget.setCurrentWidget(self.page2)
        self.bt2.setEnabled(False)
        self.bt_last.setEnabled(True)
        self.bt_last=self.bt2
    def fn_page3(self):
        self.stackedWidget.setCurrentWidget(self.page3)
        self.bt3.setEnabled(False)
        self.bt_last.setEnabled(True)
        self.bt_last=self.bt3
    def fn_page4(self):
        self.stackedWidget.setCurrentWidget(self.page4)
        self.bt4.setEnabled(False)
        self.bt_last.setEnabled(True)
        self.bt_last=self.bt4
    def fn_page5(self):
        self.stackedWidget.setCurrentWidget(self.page5)
        self.bt5.setEnabled(False)
        self.bt_last.setEnabled(True)
        self.bt_last=self.bt5
    def fn_page6(self):
        self.stackedWidget.setCurrentWidget(self.page6)
        self.bt6.setEnabled(False)
        self.bt_last.setEnabled(True)
        self.bt_last=self.bt6
    def fn_page7(self):
        self.stackedWidget.setCurrentWidget(self.page7)
        self.bt7.setEnabled(False)
        self.bt_last.setEnabled(True)
        self.bt_last=self.bt7
    
        


    def control_bt_exit(self):
        
        #self.arg_['run']=False
        self.DataProcess['run']=False
        self.zoom_.exit()
      ######################################################  self.dialog.close()
        time.sleep(1)
        self.close()
        #sys.exit()
    def control_bt_minimizar(self):
        self.showMinimized()		
        self.hide()
    def control_bt_systemtrayicon(self):
        self.show()
        self.control_bt_normal()		
        
        

    def  control_bt_normal(self): 
        if self.arg_['visible']:
            self.arg_['visible']=False
            self.last_visible=True
            self.cont_idle=0
           # time.sleep(0.2)
            t=1
        else:t=0
        self.showNormal()		
        self.bt_restaurar.hide()
        self.bt_maximizar.show()
        self.arg_['window_width']=self.page1_lb0.width()
        if t==1:self.arg_['visible']=True

    def  control_bt_maximizar(self): 
        if self.arg_['visible']:
            self.arg_['visible']=False
            self.last_visible=True
            self.cont_idle=0
           # time.sleep(0.2)
            t=1
        else:t=0
        self.showMaximized()
        self.bt_maximizar.hide()
        self.bt_restaurar.show()
        self.arg_['window_width']=self.page1_lb0.width()
       # time.sleep(0.2)
        if t==1:self.arg_['visible']=True

    def mover_menu(self):
        if self.arg_['visible']:
            self.arg_['visible']=False
            self.page1_ck1.setChecked(False)
            self.last_visible=True
            self.cont_idle=0
          #  time.sleep(0.3)

            
        
        width = self.frame_lateral.width()
        normal = 0
        if width==0:
            extender = 200
            self.bt_menu.setIcon(QIcon(self.path+'hide_menu.png'))
        else:
            extender = normal
            self.bt_menu.setIcon(QIcon(self.path+'show_menu.png'))
        
        self.animacion = QPropertyAnimation(self.frame_lateral, b'minimumWidth')
        self.animacion.setDuration(800)
        self.animacion.setStartValue(width)
        self.animacion.setEndValue(extender)
        self.animacion.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
        self.animacion.start()
        
        

    ## SizeGrip
    def resizeEvent(self, event):
        if self.arg_['visible']:
            self.arg_['visible']=False
            self.page1_ck1.setChecked(False)
            self.last_visible=True
            self.cont_idle=0
            time.sleep(0.2)
            t=1
        else:t=0
        rect = self.rect()
        self.grip.move(rect.right() - self.gripSize, rect.bottom() - self.gripSize)
        self.arg_['window_width']=self.page1_lb0.width()
        time.sleep(0.2)
        #if t==1:self.arg_['visible']=True

    ## mover ventana
    def mousePressEvent(self, event):
        self.clickPosition = event.globalPos()

    def mover_ventana(self, event):
        if self.isMaximized() == False:			
            if event.buttons() == QtCore.Qt.LeftButton:
                self.move(self.pos() + event.globalPos() - self.clickPosition)
                self.clickPosition = event.globalPos()
                event.accept()

        if event.globalPos().y() <=20:
            self.showMaximized()
        else:
            self.showNormal()

    def fn_timer(self):
        self.cont_timer+=10

        try:
            if self.DataProcess['exit']:
                self.DataProcess['run']=False
                self.DataProcess['exit']=False###para no encolar y repetir mientras se cierra
                box = QMessageBox()
                box.setIcon(QMessageBox.Question)
                box.setWindowTitle("Calibración Guardada!!")
                box.setText("Se requiere reiniciar la aplicación para que los cambios tengan efecto")
                box.setStandardButtons(QMessageBox.Yes)
                buttonY = box.button(QMessageBox.Yes)
                buttonY.setText('Al aceptar se cerrará el programa')
                box.exec_()
                print("Si")
                self.close()
        except:
            pass

        try:
            #print(self.DataProcess['log_Procesa_frames_'])
            #if len(self.DataProcess['log_Procesa_frames_'])>0:
            
            tmp=self.DataProcess['log_Procesa_frames_']
            
            self.x_final=(tmp[0])
            self.y_final=(tmp[1])
            self.z_final=(tmp[2])







            #texto="(x={:.2f}, y={:.2f}, z={:.2f}) {}".format(tmp[0],tmp[1],tmp[2],texto)
            
            #  texto="(x={:.2f}, y={:.2f}, z={:.2f}) ".format(x*c,y*c,z*c)
            
            #texto="(x={:.2f}, y={:.2f}, z={:.2f}) {}".format(self.x_last,self.y_last,self.z_last,texto)
            #texto="(x={:.2f},{:.2f} y={:.2f},{:.2f} z={:.2f},{:.2f}) ".format(self.x_last,self.x_final,self.y_last,self.y_final,self.z_last,self.z_final)
            
            

            if self.x_last!=self.x_final or self.y_last!=self.y_final or self.z_last!=self.z_final:
                self.fps2.stop()
                if self.fps2.elapsed()>0:
                    texto="{:3d} FPS".format(int(1//self.fps2.elapsed()))
                else:
                    texto=' -  FPS'
                self.fps2.start()
                x=-(self.x_last-self.x_final)
                y=-(self.y_last-self.y_final)
                z=self.z_last#-self.z_final
                c=5
                # x=x*5
                # y=y*2

                xx=x*x
                yy=y*y
                if x<0:xx=-xx
                if y<0:yy=-yy
                self.xx=int(xx)
                self.yy=int(yy)
                self.zz=int(z)
               # texto="(x={}, y={}, z={} {}) ".format(self.xx,self.yy,self.zz,texto)
                #texto="(x={:3.2f}, y={:3.2f}, z={:3.2f} ) ".format(x,y,z)
                texto="(x={:3.2f}, y={:3.2f}, z={:3.2f} ) ".format(self.x_last,self.y_last,self.z_last)
                #print(texto)
                self.frame_inferior_lb3.setText(texto)
                self.x_last=self.x_final
                self.y_last=self.y_final
                self.z_last=self.z_final



            #if len(self.DataProcess['log_pos_cube_xyz_'])>0:
            
            #self.frame_inferior_lb3.setText(str(self.DataProcess['log_pos_cube_xyz_']))
        except:
            pass


        ########Zoom se actualiza cada 100 mseg###############################
        self.totalOn+=10
        if self.zoom_check:
            cord_x,cord_y=pyautogui.position()
           # x,y=pyautogui.size()
           # print(x,y,cord_x,cord_y)

            #pyautogui.moveTo(cord_x-self.xx,cord_y-self.yy)



           # print(self.totalOn,self.totalOn%3000)
       #     if self.totalOn%3000==0:
        #    pos = pyautogui.position()
        #    self.zoom_.zoom(factor_zoom, pos[0], pos[1])
            factor_zoom=2.0
            #texto_="({},{})".format(pos[0],pos[1])
            #print(texto_)
            if self.x_final!=0 and self.y_final!=0:
                self.zoom_.zoom(factor_zoom, self.x_final,self.y_final)

        if self.cont_timer>500:
            read_log(self.DataProcess)##########################################
            self.show_log()
            
            
            # if self.totalOn>40000:##########################cerrar tras 20 segundos
            #     self.control_bt_exit()
            self.showTime()
            self.cont_timer=0
            

            # try:
            #     if len(self.DataProcess['log_Procesa_capture_'])>0:self.frame_inferior_lb2.setText(self.DataProcess['log_Procesa_capture_'])
            # except:
            #     pass
                
            for _ in config.log_.keys():
                if len(config.log_[_])>0:
                    print("-->",config.log_[_])
                    config.log_text__+=config.log_[_]
                    config.log_[_]=''
           # self.page1_tEdit1.setText(str(config.log_))#text__)
        if self.flag_Show.value:# and self.flag_ProcessCaptureDone_1.value:
          #  self.flag_Show.value=False
            self.t_end = time.time()
            totalTime = self.t_end - self.t_start
            self.t_start = time.time()
            
            if self.arg_['visible']:
                self.fn_show_captured_windows()
                
                #self.FlagProcess['flag_Show']=0
            else:
                self.page1_lb0.setText("X")
                self.page1_lb1.setText("X")

                
            # if totalTime>0:
            #     self.frame_inferior_lb2.setText('{:3d} FPS'.format(int(1//totalTime)))
            # else:
            #     self.frame_inferior_lb2.setText(' -  FPS')
            # self.fps.stop()
            # if self.fps.elapsed()>0:
            #     self.frame_inferior_lb2.setText("{:3d} FPS".format(int(1//self.fps.elapsed())))
            # else:
            #      self.frame_inferior_lb2.setText(' -  FPS')
            # self.fps.start()
            


    def showTime(self):
        global cpu_count
        
        time=QDateTime.currentDateTime()
        #timeDisplay=time.toString('dddd dd/MM/yyyy hh:mm:ss ')
        timeDisplay=time.toString(' hh:mm:ss ')
        # pos = pyautogui.position()
        # timeDisplay="({},{})".format(pos[0],pos[1])
        # print(timeDisplay)
        self.frame_inferior_lb1.setText(timeDisplay)
        texto=""
        #print(cpu_count)
        for _ in range(cpu_count):
            #print(_)
            texto+="Core {}: {}\n".format(_+1,self.arg_['core'][_])
        self.page3_lb2.setText(texto)
        
        self.cont_idle+=1
        if self.cont_idle>1 and self.last_visible:
            self.last_visible=False
            self.page1_ck1.setChecked(True)
            self.arg_['visible']=True


    def fn_page1_ck_zoom(self):
        self.zoom_check=self.page1_ck_zoom.isChecked()
        if self.zoom_check==False:
            print("False")
            pos = pyautogui.position()
            self.zoom_.zoom(1.0,0,0)# pos[0], pos[1])
        

      #  cam0=self.page1_cBox0.currentText()

    def fn_page1_ck_DoSomething(self):
        try:
            write_log(self.DataProcess,self.main_proceso,"fn_page1_ck_DoSomething - Guardado...")
            t=[{'0':self.DataProcess[0],'1':self.DataProcess[1]}]
            #print("t=",self.DataProcess[1])
            #print("t=",t)
            np.save('calibracion\\Calibración_size_cam.npy',np.array(t))#,dtype=object))
        except:
            write_log(self.DataProcess,self.main_proceso,"fn_page1_ck_DoSomething - error")
    def fn_page1_bt1(self):      #Bóton visible ON/OFF
        #self.page1_lb1.setText("HOY")
        # _arg_=[self.arg_]
        # print(_arg_)
        # print(_arg_[0]['run'])
        write_log(self.DataProcess,self.main_proceso,"Iniciando procesasamiento en cores y capturadoras")
        self.DataProcess['run']=True
        self.page1_bt1.setEnabled(False)
        self.page1_ck1.setChecked(True)
        self.arg_['visible']=True


        camara_num=0
        # manager = Manager() 
        # DataProcess = manager.dict()
    #    DataProcess['frame']=frame#arg[1][0]['frame']
#        self.DataProcess['run']=True#self.arg[1][0]['run']
        #DataProcess['flag_DoThread'][camara_num]=arg[1][0]['flag_DoThread']
        self.DataProcess['camara_num']=camara_num
        self.DataProcess['core']=True
        

   
        cam0=int(self.page1_cBox0.currentText())
        cam1=int(self.page1_cBox1.currentText())
        
        P0=Process(target=MainProcess_, args=([cam0,cam1],self.DataProcess,self.flag_Show)).start()

    ##############PAGE1  
    def fn_page1_ck1(self,state):
       # print("state",state)
        if state == 2:
            self.arg_['visible']=True
        else:
            self.arg_['visible']=False
      #  print(self.arg_['visible'])

    def fn_page1_bt2(self):
        pass


        #self.hide()
        #self.setWindowFlags((self.windowFlags() & ~Qt.WindowFullscreenButtonHint) )#| Qt.CustomizeWindowHint)
        #time.sleep(2)
        #self.show()
        #self.setWindowFlags((self.windowFlags() & ~Qt.WindowFullscreenButtonHint) )#| ~Qt.CustomizeWindowHint)
    ##############PAGE2
    def fn_page2_bt1(self):
        # dlg = QFileDialog()
        # dlg.setFileMode(QFileDialog.AnyFile)
        # dlg.setFilter("Text files (*.txt)")
        # filenames = QStringList()
		
        # if dlg.exec_():
        #     filenames = dlg.selectedFiles()
        #fname = QFileDialog.getOpenFileName(self, 'Open file', 'c:\\',"Image files (*.jpg *.gif)")
        dir = QFileDialog.getExistingDirectory(self, "Open Directory","D:\\Python\\Proyecto4",
            QFileDialog.ShowDirsOnly| QFileDialog.DontResolveSymlinks)
        #print(dir)
        self.page2_lEdit1.setText(dir)

        ##############PAGE5
    def fn_page5_bt1(self):
        box = QMessageBox()
        box.setIcon(QMessageBox.Question)
        box.setWindowTitle("Sincronización cámaras 3D")
        box.setText("Se requiere captar unas 100 imágenes de forma sincronizada para poder encontrar la matriz que sincronice ambas cámaras")
        box.setStandardButtons(QMessageBox.Yes|QMessageBox.No)
        buttonY = box.button(QMessageBox.Yes)
        buttonY.setText('Al aceptar en 5 segundos comenzará la captura')
        buttonN = box.button(QMessageBox.No)
        buttonN.setText('Cancelar')
        box.exec_()
        if box.clickedButton() == buttonY:
            self.DataProcess['run']=False
            print("Si")
            self.DataProcess['Calibracion_inicial']=False
            self.fn_page1()
            time.sleep(0.1)
            self.fn_page1_bt1()
        elif box.clickedButton() == buttonN:
            print("No")
    def fn_page5_bt2(self):
        box = QMessageBox()
        box.setIcon(QMessageBox.Question)
        box.setWindowTitle("Detección plano xy (ubicación teclado y mouse)")
        box.setText("Se requiere mover la mano en contacto con la mesa en la ubicación habitual del teclado y del mouse para calibrar la zona de trabajo (x,y,z=0)")
        box.setStandardButtons(QMessageBox.Yes|QMessageBox.No)
        buttonY = box.button(QMessageBox.Yes)
        buttonY.setText('Al aceptar en 5 segundos comenzará la captura')
        buttonN = box.button(QMessageBox.No)
        buttonN.setText('Cancelar')
        box.exec_()
        if box.clickedButton() == buttonY:
            print("Calibración aceptada 2")
            self.DataProcess['run']=False
            print("Si")
            self.DataProcess['Calibracion_Vectores_xy_teclado_mouse']=False
            self.fn_page1()
            time.sleep(0.1)
            self.fn_page1_bt1()
        elif box.clickedButton() == buttonN:
            print("No")
    def fn_page5_bt3(self):
        box = QMessageBox()
        box.setIcon(QMessageBox.Question)
        box.setWindowTitle("Detección plano xy (ubicación pantalla táctil)")
        box.setText("Se requiere mover el dedo indice en contacto con la pantalla para calibrar la zona de trabajo (x,y,z=0)")
        box.setStandardButtons(QMessageBox.Yes|QMessageBox.No)
        buttonY = box.button(QMessageBox.Yes)
        buttonY.setText('Al aceptar en 5 segundos comenzará la captura')
        buttonN = box.button(QMessageBox.No)
        buttonN.setText('Cancelar')
        box.exec_()
        if box.clickedButton() == buttonY:
            print("Si")
            self.fn_page1()
        elif box.clickedButton() == buttonN:
            print("No")

    def fn_page5_bt4(self):
        box = QMessageBox()
        box.setIcon(QMessageBox.Question)
        box.setWindowTitle("Afinar tamaño de captura de cada cámara")
        box.setText("Se precisan movimientos en la zona de trabajo para eliminar la visión sobrante panorámica de la cámara")
        box.setStandardButtons(QMessageBox.Yes|QMessageBox.No)
        buttonY = box.button(QMessageBox.Yes)
        buttonY.setText('Al aceptar en 5 segundos comenzará el ajuste. Para detenerlo pulsar el botón \"stop\"')
        buttonN = box.button(QMessageBox.No)
        buttonN.setText('Cancelar')
        box.exec_()
        if box.clickedButton() == buttonY:
            self.page1_ck_DoSomething.show()
            print("Si")
            self.DataProcess['croping']=False
            self.fn_page1()
            time.sleep(0.1)
            self.fn_page1_bt1()
        elif box.clickedButton() == buttonN:
            print("No")
    
    def fn_page5_bt5(self):
        QMessageBox.about(self,"Chess Board Matrix","Imágenes previamente guardadas en el directorio de calibración son analizadas para encontrar la matriz propia de las cámaras")
    def fn_show_captured_windows(self):


        self.visualizador3d.draw_()###################################################################################################################################################


        ###PARA MOSTRAR EN PANTALLA por PyQt
        down_width = self.page1_lb0.width()# 300
        down_height = self.page1_lb0.height()# 200
        down_points = (down_width, down_height)
        try:
            if self.DataProcess['run']:
                if self.page1_ck_procesado.isChecked():
                    frame0 = cv2.resize(self.DataProcess['frame0_procesado'], down_points, interpolation= cv2.INTER_LINEAR)
                    frame1 = cv2.resize(self.DataProcess['frame1_procesado'], down_points, interpolation= cv2.INTER_LINEAR)

                else:
                    frame0 = cv2.resize(self.DataProcess['frame0_read'], down_points, interpolation= cv2.INTER_LINEAR)
                    frame1 = cv2.resize(self.DataProcess['frame1_read'], down_points, interpolation= cv2.INTER_LINEAR)
                height, width, channel = frame0.shape
                step = channel * width
                self.fps.stop()
                if self.fps.elapsed()>0:
                    texto="{:3d} FPS".format(int(1//self.fps.elapsed()))
                else:
                    texto=' -  FPS'
                self.fps.start()
                # create QImage from image
                frame2=cv2.cvtColor(frame0,cv2.COLOR_BGR2RGB)
                qImg= QImage(frame2.data, width, height, step, QImage.Format_RGB888)
                cv2.putText(frame2, "Cam 0", (10, 20), cv2.FONT_HERSHEY_SIMPLEX,0.5, (255, 0, 0), 1, cv2.LINE_AA)
                cv2.putText(frame2, texto, (10, 50), cv2.FONT_HERSHEY_SIMPLEX,0.5, (255, 0, 0), 1, cv2.LINE_AA)
                self.page1_lb0.setPixmap(QPixmap.fromImage(qImg))
                frame2=cv2.cvtColor(frame1,cv2.COLOR_BGR2RGB)
                qImg= QImage(frame2.data, width, height, step, QImage.Format_RGB888)
                cv2.putText(frame2, "Cam 1", (10, 20), cv2.FONT_HERSHEY_SIMPLEX,0.5, (255, 0, 0), 1, cv2.LINE_AA)
                self.page1_lb1.setPixmap(QPixmap.fromImage(qImg))
            else:
                self.page1_lb0.setText("X")
                self.page1_lb1.setText("X")

        except:
            pass
           # print("Error")
    def show_log(self):
        try:
            while self.DataProcess["index_write_{}".format(100)]!=-1 and self.DataProcess["index_read_{}".format(100)]<self.DataProcess["index_write_{}".format(100)]:
                indice=self.DataProcess["index_read_{}".format(100)]
                if indice<99:
                    indice+=1
                else:
                    indice=0
                self.DataProcess["index_read_{}".format(100)]=indice
                texto=self.DataProcess["log_write_{}_{}".format(100,indice)]
                
                #texto0=self.page1_tEdit1.toPlainText()
                # print("0",texto0)
                # print("1",texto)
                self.page1_tEdit1.setText(self.page1_tEdit1.toPlainText()+"\n"+texto)
                self.page1_tEdit1.moveCursor(QtGui.QTextCursor.End)
                self.page4_lb1.setText(self.page1_tEdit1.toPlainText()+"\n"+texto)
                self.page4_lb1.moveCursor(QtGui.QTextCursor.End)
                
        except:
            pass
    ##########################################page6

import plotly.graph_objects as go
from PyQt5.QtWebKitWidgets  import QWebEngineView
class Canvas_(FigureCanvas):
    def __init__(self,parent,DataProcess):
        self.parent=parent
        self.DataProcess=DataProcess
        self.fig,self.ax=plt.subplots(1,dpi=100,figsize=(5,5),sharey=True,facecolor='white')
        nombres=['Core 1','Core 2','Core 3','Core 4','Core 5']
        colores=['red','green','green','orange','orange']
        tamaño=[95,40,42,75,70]
        self.ax.bar(nombres,tamaño,color=colores)
        self.fig.suptitle('Grafica',size=9)
        super().__init__(self.fig)
        self.setParent(self.parent)
       # self.fig.update_layout(autosize=False,width=900,height=900)
       # self.fig.show()
    def draw_(self):

        try:
        

            self.fig=go.Figure(data=[go.Scatter3d(x=self.DataProcess['cube_points'][:][0][0],y=self.DataProcess['cube_points'][:][1][0],z=self.DataProcess['cube_points'][:][2][0],
            mode='markers',marker=dict(size=5,color='red',opacity=0.5))])




        
            
            self.fig.show()


            html = '<html><body>'
            html += plt.offline.plot(self.fig, output_type='div', include_plotlyjs='cdn')
            html += '</body></html>'

            # we create an instance of QWebEngineView and set the html code
            plot_widget = QWebEngineView()
            plot_widget.setHtml(html)

            # set the QWebEngineView instance as main widget
            self.setCentralWidget(plot_widget)



        except:
            print("error draw()")
            pass

import tkinter as tk
if __name__ == "__main__":
    config.init()
    app = QApplication(sys.argv)

    mi_app = VentanaPrincipal()
    mi_app.show()

    app.exec_()
    sys.exit(app.exec_())  


