import time

BARSIZE = 50

def timit(func):
    def wrapper(*args, **kwargs):
        print("Start")
        st = time.time()
        func(st,*args, **kwargs)
        print("End in " + str(time.time() - st) + "s")
    return wrapper

def printProgress(i, size,time_  = 0 ):
    print("[" + "*" * int(BARSIZE * i / size) + " " * int(BARSIZE * (size - i) / size) + "] " + str(i) + "/" + str(
        size) + " files loaded")
    if time_ != 0:
        print(f" Time : {time.time()-time_} s")
