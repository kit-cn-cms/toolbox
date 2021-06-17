import ROOT
import re 
import os
import subprocess

import printer

def getEntries(f, treeName = "MVATree"):
    rf = ROOT.TFile.Open(f, "READ")
    tree = rf.Get(treeName)
    entries = int(tree.GetEntries())
    rf.Close()
    return entries

debugFileCheck = False
def checkFile(f, treeName = None):
    if debugFileCheck: print("checking file {}".format(f))
    if not os.path.exists(f):
        return False

    if debugFileCheck: print("1")
    rf = ROOT.TFile.Open(f)
    if rf is None or len(rf.GetListOfKeys()) == 0 or rf.TestBit(ROOT.TFile.kZombie):
        return False

    if debugFileCheck: print("2")
    if rf.TestBit(ROOT.TFile.kRecovered):
        return False

    if debugFileCheck: print("3")
    if not treeName is None:
        tree = rf.Get(treeName)
        if tree is None:
            return False

        if debugFileCheck: print("4")
        if not type(tree) == ROOT.TTree:
            return False

        if debugFileCheck: print("5")
        nevts = tree.GetEntries()
        rf.Close()

        if debugFileCheck: print("6")
        if nevts < 0:
            return False
        if nevts == 0:
            printer.printInfo("empty file {}".format(f))

    return True

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]

def hadd(files, target, entries = -1, treeName = "Events", inChunks=True):
    # check availability of all files
    ok = True
    if not treeName is None:
        for f in files:
            if not checkFile(f, treeName):
                ok = False
                printer.printError("hadd input file {} is not ok".format(f))
        if not ok:
            return False


    if len(files) == 0:
        printer.printError("no files passed to hadd")
        return False
    if not inChunks:
        if len(files) == 1:
            cmd = ["cp"]+files+[target]
        else:
            cmd = ["hadd"]+["-fk"]+[target]+files
        # print(" ".join(cmd))
        # os.system("ulimit -s unlimited")
        os.system(" ".join(cmd))
    else:
        # hadd in chunks
        hadd_parts = []
        for i, ch in enumerate(chunks(files,500)):
            outFile = target.replace(".root","")+"_chunk_{}.root".format(i)
            hadd_parts.append(outFile)
            print(len(ch)) 
            cmd = "hadd -fk {outFile} {files} ".format(files=" ".join(ch), outFile=outFile)
            # print(cmd)
            subprocess.call(cmd, shell=True)
            print("-"*50)
        # hadd all chunks together
        cmd = "hadd {outFile} {files}".format(files =" ".join(hadd_parts), outFile = target)
        print(cmd)
        subprocess.call(cmd, shell=True)
        # remove hadd parts
        cmd = "rm {files}".format(files = " ".join(hadd_parts))
        print(cmd)
        subprocess.call(cmd, shell=True)

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
                #printer.printError("cutflow step {} not in first file".format(match.group(2)))
                stages.append(match.group(2))
                values[match.group(2)] = 0
            
            values[match.group(2)] += int(match.group(3))

        if first: first = False    

    with open(target, "w") as t:
        for i, s in enumerate(stages):
            t.write("{}: {} : {}\n".format(
                i, s, values[s]))
    
    printer.printInfo("merged cutflow at {}".format(target))
    return True
