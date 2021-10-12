import os
import toolbox.printer
def execute(cmd):
    if isinstance(cmd, list):
        cmd = " ".join(cmd)
    printer.printCommand(cmd)
    os.system(cmd)


