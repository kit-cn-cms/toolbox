import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

import os
import sys
import pandas as pd

import toolbox.printer

#############################################################
# adapted from pyroot-plotscripts/tools/utis/Systematics.py #
# by L. Reuter and P. Keicher                               #
#############################################################
class SystematicsHandler:
    '''
    use this class to read systematics.csv files as used in hogwarts and pyroot-plotscrits
    '''
    def __init__(self, path):

        # load systematics csv file
        self.systematics = pd.read_csv(path, sep = ",")
        self.systematics.fillna("-", inplace = True)

    def cloneProcesses(self, processDict):
        '''
        {"originalProcess": ["newProcesses", ...], ...}
        clone the systematic setup of one process to multiple new processes
        '''
        # loop over processes to clone
        for ogProcess in processDict:
            # loop over new processes
            for newProcess in processDict[ogProcess]:
                self.systematics[newProcess] = self.systematics[ogProcess]

    def prepareSystematics(self, processes):
        '''
        remove deactivated systematics and processes
        '''
        self.allProcesses = processes

        # drop unnecessary columns
        columns = ["Uncertainty", "Type", "Construction", "Up", "Down", "SysGroup"]+processes
        self.systematics.drop(
            self.systematics.columns.difference(columns), 1, inplace = True)
        self.systematics = self.systematics[columns]

        # drop all unnecessary lines
        self.systematics = self.systematics[
            ~self.systematics[processes].eq("-", axis = 0).all(axis = 1)]
        self.systematics = self.systematics[
            ~self.systematics["Uncertainty"].str.startswith("#")]

        # build dicts for different syst types
        self.weightSysts    = self.constructSystDict("weight")
        self.variationSysts = self.constructSystDict("variation")
        self.rateSysts      = self.constructSystDict("rate")
        
    def constructSystDict(self, sysType):
        '''
        construct dictionary of systematics for each type
        '''
        systDict = {}
        df = self.systematics.loc[self.systematics["Construction"] == sysType]
        for i, syst in df.iterrows():
            systName = syst["Uncertainty"]

            exprUp = syst["Up"]
            exprDn = syst["Down"]

            if exprUp == "-" and exprDn == "-":
                systDict[systName] = "-"
            elif exprUp == "-":
                systDict[systName] = exprDn
            elif exprDn == "-":
                systDict[systName] = exprUp
            else:
                systDict[systName+"Up"]   = exprUp
                systDict[systName+"Down"] = exprDn
        return systDict


    def getSysTypeDictForProcess(self, process, sysType):
        '''
        get dictionary of systematics for a process+type combination
        '''
        varSys = self.systematics[self.systematics["Construction"] == sysType]
        varSys = varSys[~varSys[process].eq("-")]

        systInfo = {}

        # construct up table
        dfup = varSys.loc[:, ["Uncertainty", "Up"]]
        dfup.loc[:,"Uncertainty"]+="Up"
        dfup.set_index("Uncertainty", drop = True, inplace = True)
        dfup = dfup.loc[~dfup["Up"].eq("-")]
        systInfo.update(dfup.to_dict()["Up"])

        # construct down table
        dfdown = varSys.loc[:, ["Uncertainty", "Down"]]
        dfdown.loc[:,"Uncertainty"]+="Down"
        dfdown.set_index("Uncertainty", drop = True, inplace = True)
        dfdown = dfdown.loc[~dfdown["Down"].eq("-")]
        systInfo.update(dfdown.to_dict()["Down"])

        return systInfo

    def getSysTypeValueDictForProcess(self, process, sysType):
        '''
        get systematic values for process+type combination
        '''
        varSys = self.systematics[self.systematics["Type"] == sysType]
        if "-" in varSys[process]:
            varSys = varSys[~varSys[process].eq("-")]

        systInfo = {}
        
        # construct process table
        df = varSys.loc[:, ["Uncertainty", process]]
        df.set_index("Uncertainty", drop = True, inplace = True)
        systInfo.update(df.to_dict()[process])

        print(systInfo)
        exit()

        return systInfo 

    def getProcessSystUpDown(self, process, systName):
        varSys = self.systematics.loc[:, ["Uncertainty", "Up", "Down", process]]
        varSys.set_index("Uncertainty", drop = True, inplace = True)
        up = varSys.loc[systName, "Up"]
        down = varSys.loc[systName, "Down"]
        return up, down

    def getAllWeightSysts(self):
        return self.weightSysts.keys()

    def getAllWeightExpressions(self):
        return self.weightSysts.values()



    def checkJEC(self, process, trees, treeName = "Events"):
        # check if JECs are present in trees for given process
        failed = False
        jecs = self.getSysTypeDictForProcess(process, "variation").values()
        if len(jecs) == 0:
            return True
        
        # loop over trees 
        for tree in trees:
            rf = ROOT.TFile(tree)
            t  = rf.Get(treeName)
            branches = [b.GetName() for b in t.GetListOfBranches()]
            for jec in jecs:
                if not any([b.endswith(jec) for b in branches]):
                    printer.printError(
                        "couldnt find JEC branches for {} in {} samples".format(
                            jec, process))
                    failed = True

        return not failed

