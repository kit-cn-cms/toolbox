import os
import printer
import shutil

def mkdir(path, overwrite = False, versioning = False, subcall = False):
    if not os.path.isabs(path):
        path = os.path.abspath(path)

    # check if subdirectories exist first
    subdir = os.path.dirname(path)
    if not os.path.exists(subdir):
        mkdir(subdir, subcall = True)

    if not os.path.exists(path):
        os.mkdir(path)
    elif versioning:
        printer.printInfo("directory already exists - appending index")
        idx = 1
        while(os.path.exists(path+"_v"+str(idx))): idx+=1
        path+="_v"+str(idx)

        os.mkdir(path)
    elif overwrite:
        printer.printInfo("directory {} already exists -- deleting first".format(path))
        shutil.rmtree(path)
        os.mkdir(path)
    else:
        # nothing needs to be done
        return os.path.abspath(path)

    if not subcall:
        printer.printPath("created directory {}".format(path))
    return os.path.abspath(path)
