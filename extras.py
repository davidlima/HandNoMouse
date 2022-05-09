import numpy as np
from PyQt5.QtCore import QDateTime
def write_log(DataProcess,process_name,texto):
    
    indice=DataProcess["index_write_{}".format(process_name)]
    if indice<99:
        indice+=1
    else:
        indice=0

    DataProcess["log_write_{}_{}".format(process_name,indice)]=texto
    DataProcess["index_write_{}".format(process_name)]=indice

    # print("log=","log_write_{}_{}".format(process_name,indice))
    # print("In=",DataProcess["log_write_{}_{}".format(process_name,indice)])
    # print(process_name,indice)

def read_log(DataProcess):
    for _ in range(30):
        try:
            while DataProcess["index_write_{}".format(_)]!=-1 and DataProcess["index_read_{}".format(_)]<DataProcess["index_write_{}".format(_)]:
                indice=DataProcess["index_read_{}".format(_)]
                if indice<99:
                    indice+=1
                else:
                    indice=0
                DataProcess["index_read_{}".format(_)]=indice
                time=QDateTime.currentDateTime()
                #timeDisplay=time.toString('dddd dd/MM/yyyy hh:mm:ss ')
                timeDisplay=time.toString('-->hh:mm:ss.z ')
                texto="{} Proceso nº {} --> {}".format(timeDisplay,_,DataProcess["log_write_{}_{}".format(_,indice)])
                #print(texto)
                write_log(DataProcess,100,texto)
                #DataProcess["log_read"+_][indice]=

        except:
            pass
        # DataProcess["log_write"+_][indice]=texto
        # DataProcess["index_write"+_]=indice



def DistanciaEuclideana(DataProcess,a,b):
    try:
        a_=np.array((DataProcess['cube_points'][0][a][0][0],DataProcess['cube_points'][0][a][1][0],DataProcess['cube_points'][0][a][2][0]))
        b_=np.array((DataProcess['cube_points'][0][b][0][0],DataProcess['cube_points'][0][b][1][0],DataProcess['cube_points'][0][b][2][0]))
        return np.linalg.norm(a_-b_)
    except:
        print("ERROR DistanciaEuclideana()",a,b)
        return 5###############################################################################################################################################

def Determina_Acciones_mano(DataProcess):
    d_pulgar=DistanciaEuclideana(DataProcess,0,4)
    d_indice=DistanciaEuclideana(DataProcess,0,8)
    if d_indice<d_pulgar:DataProcess['log_pos_cube_xyz_']="{:.2f} {:.2f} {:.2f} CLICK".format(d_pulgar,d_indice,d_indice/d_pulgar)
    else:DataProcess['log_pos_cube_xyz_']="{:.2f} {:.2f} {:.2f} OK".format(d_pulgar,d_indice,d_indice/d_pulgar)    
    # texto=''
    # for _ in range(20):
    #     texto+="{}-{}={}, ".format(_,_+1,DistanciaEuclideana(DataProcess,_,_+1))
    # print(texto)