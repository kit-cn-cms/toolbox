import ROOT
import re 
import os

import printer

def getEntries(f, treeName = "MVATree"):
    rf = ROOT.TFile.Open(f, "READ")
    tree = rf.Get(treeName)
    entries = int(tree.GetEntries())
    rf.Close()
    return entries

def checkFile(f, treeName = None):
    if not os.path.exists(f):
        return False

    rf = ROOT.TFile.Open(f)
    if rf is None or len(rf.GetListOfKeys()) == 0 or rf.TestBit(ROOT.TFile.kZombie):
        return False

    if rf.TestBit(ROOT.TFile.kRecovered):
        return False

    if not treeName is None:
        tree = rf.Get(treeName)
        if tree is None:
            return False

        nevts = tree.GetEntries()
        rf.Close()
        if nevts < 0:
            return False
        if nevts == 0:
            printer.printInfo("empty file {}".format(f))

    return True


def hadd(files, target, entries = -1, treeName = "Events"):
    if entries<=0: treeName = None

    # check availability of all files
    ok = True
    for f in files:
        if not checkFile(f, treeName):
            ok = False
            printer.printError("hadd input file {} is not ok".format(f))
    if not ok:
        return False


    if len(files) == 0:
        printer.printError("no files passed to hadd")
        return False
    if len(files) == 1:
        cmd = ["cp"]+files+[target]
    else:
        cmd = ["hadd"]+["-fk"]+[target]+files

    os.system(" ".join(cmd))

    if entries >= 0:
        haddedEntries = getEntries(target, treeName)
        if not int(entries) == int(haddedEntries):
            printer.printError("number of entries after hadd dont match up")
            printer.printError("source: {} | target: {}".format(entries, haddedEntries))
            return False

    return True

cutflowRegex = r"([0-9]+): (.*?) : ([0-9]+)"
def mergeCutflow(files, target):
    stages = []
    values = {}
    first = True
    for f in files:
        with open(f, "r") as c:
            lines = c.readlines()

        for l in lines:
            match = re.search(cutflowRegex, l)
            if match is None:
                printer.printError("cutflow file not parseable")
                return False        
    
            if first:
                stages.append(match.group(2))
                values[match.group(2)] = 0

            if not match.group(2) in stages:
                printer.printError("cutflow files not compatible")
                return False
            
            values[match.group(2)] += int(match.group(3))

        if first: first = False    

    with open(target, "w") as t:
        for i, s in enumerate(stages):
            t.write("{}: {} : {}\n".format(
                i, s, values[s]))
    
    printer.printInfo("merged cutflow at {}".format(target))
    return True
