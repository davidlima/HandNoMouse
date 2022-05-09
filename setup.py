from distutils.core import setup
import py2exe
#https://geekytheory.com/generar-un-ejecutable-exe-a-partir-de-un-py/
#setup.py py2exe

####opcion n2   
# pyinstaller hello_world.py
#C:\Users\David\AppData\Local\Programs\Python\Python310

setup(
    name="Hand_No_Mouse",
    version="1.0",
    description="Mediante 2 cámaras y a través de visión estereoscópica se simula el uso del mouse con el movimiento de las manos en 3D",
    author="David Lima Granada",
    author_email="davidlimagranada@gmail.com",
    url="url del proyecto",
    license="tipo de licencia",
    scripts=["TEST2.py"],
    console=["TEST2.py"],
    options={"py2exe": {"bundle_files": 1}},
    zipfile=None,
)