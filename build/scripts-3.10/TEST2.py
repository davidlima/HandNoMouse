import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsDropShadowEffect
from PyQt5.QtCore import  QPropertyAnimation,QEasingCurve
from PyQt5.QtGui  import QColor
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QFileDialog
from PyQt5.uic import loadUi
import threading
import time
from video import Video_
import multiprocessing as mp
from PyQt5.QtCore import QTimer,QDateTime


class VentanaPrincipal(QMainWindow):
    
    arg_={'run':True}
    
    cpu_count=0
    def __init__(self):
        global cpu_count
        super(VentanaPrincipal, self).__init__()
        loadUi('imagenes\\menu1.ui', self)
        self.arg_.update({'self':self})
        self.arg_.update({'visible':True})
        
        cpu_count = mp.cpu_count()
        process = list(range(cpu_count))    ##numero de nucleos disponibles!!                                                                                                                                                
        process=dict.fromkeys(process, False)
        self.arg_.update(process)
        
        self.page3_lb1.setText("Núm Cores disponibles: {}".format(cpu_count))
        


        # timer = QtCore.QTimer()
        # timer.timeout.connect(self.showTime)
        # timer.start(1000)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.showTime)
        self.timer.start(1000)

        # self.timerEvent.start(1000)
        # self.timer.timeout.connect(self.showTime)
        
        
        

        #eliminar barra y de titulo - opacidad
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setWindowOpacity(1)
        self.setWindowTitle("HandNoMouse")
        self.bt_restaurar.hide()

        self.arg_.update({'window_width':self.page1_lb0.width()})
        #print("width=",self.arg_['window_width'],self.page1_lb0.height())

		#menu lateral
        self.bt_menu.clicked.connect(self.mover_menu)


        #SizeGrip
        self.gripSize = 10
        self.grip = QtWidgets.QSizeGrip(self)
        self.grip.resize(self.gripSize, self.gripSize)

        # mover ventana
        self.frame_superior.mouseMoveEvent = self.mover_ventana

        self.bt1.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page1))
        self.bt2.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page2))
        self.bt3.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page3))
        self.bt4.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page4))
        self.bt5.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page5))

        ####PAGE1
        self.page1_bt1.clicked.connect(self.fn_page1_bt1)
        self.page1_ck1.stateChanged.connect(self.fn_page1_ck1)

        ####PAGE2
        self.page2_bt1.clicked.connect(self.fn_page2_bt1)
        
        
        
        self.bt_minimizar.clicked.connect(self.control_bt_minimizar)		
        self.bt_restaurar.clicked.connect(self.control_bt_normal)
        self.bt_maximizar.clicked.connect(self.control_bt_maximizar)
        self.bt_cerrar.clicked.connect(self.control_bt_exit)#self.close())

    def control_bt_exit(self):
        
        self.arg_['run']=False
        time.sleep(1)
        self.close()
        #sys.exit()
    def control_bt_minimizar(self):
        self.showMinimized()		

    def  control_bt_normal(self): 
        if self.arg_['visible']:
            self.arg_['visible']=False
            time.sleep(0.2)
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
            time.sleep(0.2)
            t=1
        else:t=0
        self.showMaximized()
        self.bt_maximizar.hide()
        self.bt_restaurar.show()
        self.arg_['window_width']=self.page1_lb0.width()
        time.sleep(0.2)
        if t==1:self.arg_['visible']=True

    def mover_menu(self):
        if self.arg_['visible']:
            self.arg_['visible']=False
            self.page1_ck1.setChecked(False)
            time.sleep(0.3)

            
        
        width = self.frame_lateral.width()
        normal = 0
        if width==0:
            extender = 200
        else:
            extender = normal
        
        self.animacion = QPropertyAnimation(self.frame_lateral, b'minimumWidth')
        self.animacion.setDuration(300)
        self.animacion.setStartValue(width)
        self.animacion.setEndValue(extender)
        self.animacion.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
        self.animacion.start()
        
        

    ## SizeGrip
    def resizeEvent(self, event):
        if self.arg_['visible']:
            self.arg_['visible']=False
            self.page1_ck1.setChecked(False)
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

    def showTime(self):
        global cpu_count
        
        time=QDateTime.currentDateTime()
        timeDisplay=time.toString('dddd dd-MM-yyyy hh:mm:ss ')
        self.frame_inferior_lb1.setText(timeDisplay)
        texto=""
        #print(cpu_count)
        for _ in range(cpu_count):
            #print(_)
            texto+="Core {}: {}\n".format(_+1,self.arg_[_])
        self.page3_lb2.setText(texto)

        

    def fn_page1_bt1(self):      
        #self.page1_lb1.setText("HOY")
        # _arg_=[self.arg_]
        # print(_arg_)
        # print(_arg_[0]['run'])
        self.page1_bt1.setEnabled(False)
        self.page1_ck1.setChecked(True)
        self.arg_['visible']=True
        t0=threading.Thread(target=Video_, args=(0,[self.arg_]))
        t0.start()


        t1=threading.Thread(target=Video_, args=(1,[self.arg_]))
        t1.start()

    def fn_page1_ck1(self,state):
       # print("state",state)
        if state == 2:
            self.arg_['visible']=True
            
            
        else:
            self.arg_['visible']=False
        
      #  print(self.arg_['visible'])

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
        print(dir)
        self.page2_lEdit1.setText(dir)

         

if __name__ == "__main__":
     app = QApplication(sys.argv)
     mi_app = VentanaPrincipal()
     mi_app.show()
     app.exec_()
     #sys.exit(app.exec_())  

