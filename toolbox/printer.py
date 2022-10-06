
def printInfo(cmd, nbefore = 0, nafter = 0):
    printBreak(nbefore)
    print("\033[0;32m{}\033[0m".format(cmd))
    printBreak(nafter)

def printAction(cmd, nbefore = 0, nafter = 0):
    printBreak(nbefore)
    print("\033[1;33m{}\033[0m".format(cmd))
    printBreak(nafter)

def printPath(cmd, nbefore = 0, nafter = 0):
    printBreak(nbefore)
    print("\033[0;37m{}\033[0m".format(cmd))
    printBreak(nafter)

def printCommand(cmd, nbefore = 0, nafter = 0):
    printBreak(nbefore)
    print("\033[0;31m{}\033[0m".format(cmd))
    printBreak(nafter)

def printWarning(cmd, nbefore = 0, nafter = 0):
    printBreak(nbefore)
    print("\033[7;93m{}\033[0m".format(cmd))
    printBreak(nafter)

def printError(cmd, nbefore = 0, nafter = 0):
    printBreak(nbefore)
    print("\033[7;91m{}\033[0m".format(cmd))
    printBreak(nafter)

def printResult(cmd, nbefore = 0, nafter = 0):
    printBreak(nbefore)
    print("{}".format(cmd))
    printBreak(nafter)

def printDelim(char = "=", n = 50):
    print(str(char)*int(n))

def printBreak(n = 2):
    for _ in range(int(n)): print("")




def testPrint():
    printInfo("printInfo...")
    printAction("printAction...")
    printPath("printPath...")
    printCommand("printCommand...")
    printError("printError...")
    printWarning("printWarning...")
    printResult("printResult...")



    
