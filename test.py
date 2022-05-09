# from concurrent.futures import ThreadPoolExecutor
# #from tqdm import tqdm
# import multiprocessing

# def generate_rgb3(args):    
#     img, a, b, c = args # sacamos los argumentos de la tupla
#     ms = read_ms(img)
#     rgb = get_rgb(ms)
#     return save_png(img, rgb)

# num_cores = multiprocessing.cpu_count()

# args = [(img, 1, 2, 3) for img in frames] # lista de tuplas con argumentos

# with ThreadPoolExecutor(max_workers=num_cores) as pool:
#     with tqdm(total=len(images)) as progress:
#         futures = []

#         for arg in args:
#             future = pool.submit(generate_rgb3, arg) # enviamos la tupla de argumentos
#             future.add_done_callback(lambda p: progress.update())
#             futures.append(future)

#         results = []
#         for future in futures:
#             result = future.result()
#             results.append(result)
from multiprocessing import Process,Manager,Value
import time
import sys
import psutil

def f(name,b,Flag):
    print('hello', name)
    print(b.value,Flag['flag'])
    Flag['flag']=True
    print(b.value,Flag['flag'])
    for x in range(3):
        print(psutil.cpu_percent(interval=1, percpu=True))
    #b['flag']=True
    b.value+=1

    

if __name__ == '__main__':
    Flag=Manager() .dict()
    Flag['flag']=False
    a=Value('i',0)
    p = Process(target=f, args=('bob',a,Flag))
    p.start()
    #p.join()
    #time.sleep(0.1)
    #print(Flag)
    print("a",a.value)
    print(sys.version)
    #time.sleep(1)
    for _ in range(10000):
        print("b",a.value,end="\r")

        # p = psutil.Process(os.getpid()) >>> p.nice() 0 >>> p.nice(10)