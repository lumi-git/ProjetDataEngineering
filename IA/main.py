import json.decoder
import os
import time


def getHeader():
    return "sens,numerobus,numerobuskr,voiturekr,idbus,idligne,etat,destination, nomcourtligne,coordonnees,date,heure"


def timit(func):
    def wrapper(*args, **kwargs):
        print("Start")
        st = time.time()
        func(*args, **kwargs)
        print("End in " + str(time.time() - st) + "s")

    return wrapper


@timit
def main():
    """
    run this script inside a folder also containing a folder named Data
    it will create a folder named DataCopy and put the translated csv files inside
    """

    dir = os.listdir("data")

    for file in dir:
        with open("data/" + file, 'r') as f:
            with open("dataCopy/" + file.replace("txt", "csv"), 'w') as g:
                data = file.split("_")[1:]
                date = data[0]
                heure = data[1].replace("-", ":").replace(".txt", "")
                res = getHeader() + "\n"

                for l in f.readlines():
                    tab = l.replace("\n", "").replace("{", "").replace("}", "").split(",")[:-3]
                    coords = l.replace("\n", "").replace("{", "").replace("}", "").split("coordonnees")[
                        1]
                    coords = coords.replace(",", ";").replace(":", "").replace("'", "")

                    if len(tab) > 8:
                        vals = tab[0].split(":")
                        res += vals[1]
                        for i in tab[1:]:
                            vals = i.split(":")
                            res += "," + vals[1]
                        res += "," + coords
                        res += "," + date
                        res += "," + heure
                        res += "\n"

                g.write(res)


main()
