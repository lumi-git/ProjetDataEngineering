import os
import threading
from utils import timit
from utils import printProgress

def getHeader():
    return "sens,numerobus,numerobuskr,voiturekr,idbus,idligne,etat,destination, nomcourtligne,coordonnees,date,heure"



class ProcessFiles(threading.Thread) :

    Counter = 0
    Lock = threading.Lock()

    def __init__(self, files, i, gSize):
        threading.Thread.__init__(self)
        self.files = files
        self.i = i
        self.GSize = gSize

    def run(self):
        for file in self.files :
            with open("./../Data/" + file, 'r') as f:
                with open("./../DataCopy/" + file.replace("txt","csv"), 'w') as g:
                    ProcessFiles.Lock.acquire()
                    ProcessFiles.Counter += 1
                    ProcessFiles.Lock.release()

                    if (ProcessFiles.Counter % 100 == 0):
                        os.system('cls' if os.name == 'nt' else 'clear')
                        printProgress(ProcessFiles.Counter, self.GSize)
                    if (ProcessFiles.Counter%100 == 0):
                        print(str(ProcessFiles.Counter) + "/" + str(self.GSize))
                    data = file.split("_")[1:]
                    date = data[0]
                    heure = data[1].replace("-",":").replace(".txt", "")
                    res = getHeader() + "\n"

                    for l in f.readlines():

                        tab = l.replace("\n", "").replace("{", "").replace("}", "").split(",")[:-3]
                        coords = l.replace("\n", "").replace("{", "").replace("}", "").split("coordonnees")[1]
                        coords = coords.replace(",",";").replace(":","").replace("'","")
                        coords = coords.split(";")[0] + ";" + coords.split(";")[1]
                        if len(tab) > 8 :
                            vals = tab[0].split(":")
                            res += vals[1]
                            for i in tab[1:] :
                                vals = i.split(":")
                                res += "," + vals[1]

                            if l.find("destination") == -1:
                                res += ",None"

                            res += "," + coords
                            res += "," + date
                            res += "," + heure
                            res += "\n"
                    g.write(res)
        print("Thread " + str(self.i) + " done")

@timit
def main(time):

    """
    run this script inside a folder also containing a folder named Data
    it will create a folder named DataCopy and put the translated csv files inside
    """
    
    dir = os.listdir("./../Data")
    j = 0
    for file in dir:
        j+=1
        if (j%100 == 0):
            print(str(j) + "/" + str(len(dir)))

        with open("./../Data/" + file, 'r') as f:
            with open("./../DataCopy/" + file.replace("txt","csv"), 'w') as g:
                data = file.split("_")[1:]
                date = data[0]
                heure = data[1].replace("-",":").replace(".txt", "")
                res = getHeader() + "\n"
                
                for l in f.readlines():
                    tab = l.replace("\n", "").replace("{", "").replace("}", "").split(",")[:-3]
                    coords = l.replace("\n", "").replace("{", "").replace("}", "").split("coordonnees")[1]
                    coords = coords.replace(",",";").replace(":","").replace("'","")
                    coords = coords.split(";")[0] + ";" + coords.split(";")[1]
                    if len(tab) > 8 :
                        vals = tab[0].split(":")
                        res += vals[1]
                        for i in tab[1:] :
                            vals = i.split(":")
                            res += "," + vals[1]
                        res += "," + coords
                        res += "," + date
                        res += "," + heure
                        res += "\n"
                g.write(res)

@timit
def mainThreaded(time):
    dir = os.listdir("./../Data")

    threads = []
    #divide the dir in n parts and create n threads for these part
    n = 8
    gSize = len(dir)
    for i in range(n):
        threads.append(ProcessFiles(dir[i::n], i, gSize))

    for t in threads :
        t.start()

    for t in threads :
        t.join()



mainThreaded()