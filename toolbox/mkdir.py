import os
import printer

def mkdir(path):
    if not os.path.isabs(path):
        path = os.path.abspath(path)

    # check if subdirectories exist first
    subdir = os.path.dirname(path)
    if not os.path.exists(subdir):
        mkdir(subdir)

    if not os.path.exists(path):
        os.mkdir(path)
        printer.printPath("created directory {}".format(path))
    return os.path.abspath(path)
