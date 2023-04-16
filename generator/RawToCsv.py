import os
import threading
from utils import timit
from utils import printProgress


def getHeader():
    return "sens;numerobus;numerobuskr;voiturekr;idbus;idligne;etat;destination;nomcourtligne;coordonnees;ecartsecondes;date;heure"


class ProcessFiles(threading.Thread):
    Counter = 0
    Lock = threading.Lock()

    def __init__(self, files, i, gSize):
        threading.Thread.__init__(self)
        self.files = files
        self.i = i
        self.GSize = gSize

    def run(self):
        for file in self.files:
            with open("./Data/" + file, 'r') as f:
                with open("./DataCopy/" + file.replace("txt", "csv"), 'w') as g:
                    ProcessFiles.Lock.acquire()
                    ProcessFiles.Counter += 1
                    ProcessFiles.Lock.release()

                    if (ProcessFiles.Counter % 100 == 0):
                        os.system('cls' if os.name == 'nt' else 'clear')
                        printProgress(ProcessFiles.Counter, self.GSize)
                    if (ProcessFiles.Counter % 100 == 0):
                        print(str(ProcessFiles.Counter) + "/" + str(self.GSize))
                    data = file.split("_")[1:]
                    date = data[0]
                    heure = data[1].replace("-", ":").replace(".txt", "")
                    res = getHeader() + "\n"

                    lines = f.readlines()

                    if len(lines) == 0:
                        continue

                    for l in lines:
                        # remove the \n and accents
                        l = l.replace("\n", "")
                        l = l.replace("é", "e")
                        l = l.replace("è", "e")

                        l = l.strip()

                        if l.startswith("{"):
                            entry = eval(l)
                            sens = entry.get("sens", "0")
                            if type(sens) is str:
                                sens = 0
                            numerobus = entry.get("numerobus", "0")
                            numerobuskr = entry.get("numerobuskr", "")
                            voiturekr = entry.get("voiturekr", "")
                            if type(voiturekr) is list:
                                voiturekr = voiturekr[0]
                            idbus = entry.get("idbus", "")
                            idligne = entry.get("idligne", "")
                            etat = entry.get("etat", "")
                            destination = entry.get("destination", "")
                            nomcourtligne = entry.get("nomcourtligne", "")
                            coordonnees = entry.get("coordonnees", "")
                            ecartsecondes = entry.get("ecartsecondes", "0")

                            if etat != "Hors-service" and etat != "Haut-le-pied" and etat != "Inconnu" and voiturekr != "Hors-service" and voiturekr != "Haut-le-pied" and voiturekr != "Inconnu":
                                res += f"{sens};\"{numerobus}\";\"{numerobuskr}\";\"{voiturekr}\";\"{idbus}\";\"{idligne}\";\"{etat}\";\"{destination}\";\"{nomcourtligne}\";{coordonnees};{ecartsecondes};{date};{heure}\n"
                    g.write(res)

        print("Thread " + str(self.i) + " done")


@timit
def mainThreaded(time):
    dir = os.listdir("./Data")

    threads = []
    # divide the dir in n parts and create n threads for these part
    n = 2
    gSize = len(dir)
    for i in range(n):
        threads.append(ProcessFiles(dir[i::n], i, gSize))

    for t in threads:
        t.start()

    for t in threads:
        t.join()


mainThreaded()
