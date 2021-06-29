import ROOT
ROOT.gROOT.SetBatch(True)

import pandas as pd
import sys

#############################################################
# adapted from pyroot-plotscripts/tools/utis/Plots.py       #
# by L. Reuter, P. Keicher and J.v.d.Linden                 #
#############################################################

from Template import Template
from Setters import HPSetters

from toolbox import printer

class HarryPlotter(HPSetters):
    def __init__(self, plotName, inputFile, outputFile, 
            xLabel = None, channelLabel = None, lumi = None):

        # some settings for the output histograms
        self.plotName   = plotName
        self.outputFile = outputFile

        # xLabel can be inferred from plotName if no label is passed
        self.xLabel = plotName
        if not self.xLabel is None:
            self.xLabel = xLabel

        # label for top of plot (e.g. jet tag region)
        self.channelLabel = channelLabel

        # lumi for lumi label
        self.lumi = lumi

        # input file where templates are stored
        self.inputFile  = inputFile

        # initialize templates dict
        self.templates = {}

        # list of histogram setups
        self.histogramSetups = []

    def loadFromDatacard(self):
        '''
        Load all the information from datacard input
        '''
        pass

    def loadFromSystFile(self, systFile):
        '''
        Load all the information from a systematics csv file
        '''
        printer.printAction(
            "loading process and systematics information from systematics file...",2)

        # loading information from crosssection of systematic csv file and input root file
        self.rf = ROOT.TFile(self.inputFile)
        self.sf = pd.read_csv(systFile, sep = ",")
        self.sf.fillna("-", inplace = True)

        # get all process names that are defined in the systematics file
        columns = ["Uncertainty", "Type", "Construction", "Up", "Down", "SysGroup"]
        systFileProcesses = self.sf.columns.difference(columns)

        # get cross section of processes that are also defined in the root file
        self.processNames = []
        for proc in systFileProcesses:
            nomKeyName = self.GetNomKeyName(proc, self.channelName)
            if self.rf.GetListOfKeys().Contains(nomKeyName):
                self.processNames.append(proc)

        # prune systematics file
        columns = ["Uncertainty", "Type", "SysGroup"]+self.processNames
        self.sf.drop(self.sf.columns.difference(columns), 1, inplace = True)
        self.sf = self.sf[columns]

        # drop all unneccessary lines
        self.sf = self.sf[
             self.sf["Type"] == "shape"]
        self.sf = self.sf[
            ~self.sf[self.processNames].eq("-", axis = 0).all(axis = 1)]
        self.sf = self.sf[
            ~self.sf["Uncertainty"].str.startswith("#")]
 
        # loop over processes and build one template class per process
        for proc in self.processNames:
            printer.printInfo("\tloading templates for process {}".format(proc))
            systs = self.sf[~self.sf[proc].eq("-")].loc[:, ["Uncertainty", "SysGroup"]]
            systs.set_index("Uncertainty", drop = True, inplace = True)
            systs = systs.to_dict()["SysGroup"]

            self.templates[proc] = Template(
                procName = proc,
                systDict = systs
                )
            self.templates[proc].loadTemplates(self)

        if not self.dataName is None:
            self.templates[self.dataName] = Template(
                procName = self.dataName,
                isData   = True)
            self.templates[self.dataName].loadTemplates(self)

    def loadFromROOTFile(self):
        '''
        load all the information from a root file with the templates
        '''
        pass

    def loadFromHarvester(self):
        '''
        load all the information from combine harvester input
        '''
        pass
    
    def loadFromOptions(self):
        '''
        load all the information from command line options
        '''
        pass






    def mergeTemplates(self, targetName, originalNames):
        # function is called once per merge template
        '''
        define a merged template 
        '''
        printer.printAction(
            "\tmerging processes {} to {}".format(",".join(originalNames), targetName))

        if targetName in self.templates:
            printer.printWarning("\t merged template {} already in templates".format(targetName))
            sys.exit()

        # get all templates that are to be merged
        ogTemplates = []
        for ogName in originalNames:
            if not ogName in self.templates:
                printer.printWarning("\t process {} for merge {} not defined".format(
                    ogName, targetName))
                continue
            ogTemplates.append(self.templates[ogName])

        # build new template
        self.templates[targetName] = Template.mergeTemplates(
            targetName     = targetName,
            inputTemplates = ogTemplates)


    def loadErrorbands(self):
        '''
        load errorbands for all templates
        '''
        printer.printAction("constructing errorbands ...",1)
        for proc in self.templates:
            self.templates[proc].loadErrorbands(
                linear = self.sumSystsOfProcessLinear
                )
                 
   
    def defineUncertaintyGroup(self, name, members):
        '''
        define a new group of systematics based on other groups
        '''
        printer.printAction(
            "constructing combined uncertainty group {} from {}...".format(
                name, ",".join(members)),1)

        # do that for each template
        for proc in self.templates:
            self.templates[proc].defineUncertaintyGroup(
                name, members, linear = self.sumSystsOfProcessLinear)
 
    
    def addHistogramSetup(self, hs):
        '''
        add a histogram setup for plotting
        '''
        printer.printInfo(
            "\tadding histogram setup {}".format(hs.nameTag))
        self.histogramSetups.append(hs)



    def plot(self):
        '''
        call plotting routine for each defined histogram setup
        '''
        printer.printAction("drawing histograms...", 2)
        
        # looping over histogram setups
        for setup in self.histogramSetups:
            # printing overview of settings
            printer.printAction("drawing histogram with setup {}...".format(setup.nameTag),1)
            print(setup)

            # define output name based on name tag
            outFile = self.outputFile
            if not setup.nameTag == "default":
                outFile = outFile.replace(".pdf", "_{}.pdf".format(setup.nameTag))

            # call drawing routine
            setup.drawHistogram(
                self.plotName, 
                self.xLabel, 
                self.channelLabel, 
                self.lumi, 
                self.divideByBinWidth,
                outFile, 
                self.templates)


