import os
import printer
def execute(cmd):
    if type(cmd)==list:
        cmd = " ".join(cmd)
    printer.printCommand(cmd)
    os.system(cmd)

