import ROOT

import sys
import numpy as np
from toolbox import printer
import hpUtil

class Template:
    '''
    Class that handles one template to be plot in a histogram
    Defines some features and loads all the systematically varied templates
    Also builds the residual errorbands
    '''
    def __init__(self, procName, systDict = None, systList = None, isData = False):
        self.procName = procName

        # is data
        self.isData = isData
        self.partOfMerged = False

        # systematics
        self.systs = {}
        self.allGroups = set()
        # majorSystGroups defines a set of uncertainty groups with no overlap
        self.majorSystGroups = set()
       
        # if systDict is passed load systs directly with SysGroup
        if not systDict is None:
            for sys in systDict:
                self.systs[sys] = systDict[sys]
                self.allGroups.update([systDict[sys]])
                self.majorSystGroups.update([systDict[sys]])
        # if only a list of systematics is passed all are 
        # per default put in "syst" list
        elif not systList is None:
            for sys in systList:
                self.systs[sys] = "syst"
                self.allGroups.update(["syst"])
                self.majorSystGroups.update(["syst"])

        self.loaded = False
        self.error  = False

        # default display options
        self.color = hpUtil.getHistColor(procName)
        self.label = procName


    @classmethod
    def mergeTemplates(cls, targetName, inputTemplates):
        '''
        merge already defined templates to another one
        '''
        # load all systeamtics defined for the merger
        systDict = {}
        for inputTemplate in inputTemplates:
            systDict.update(inputTemplate.systs)

        # init new template
        t = Template(targetName, systDict = systDict)

        # init new template histograms
        t.nom = None
        t.up = {}
        t.dn = {}

        # loop over input templates
        for inputTemplate in inputTemplates:
            # add nominal template
            if t.nom is None:
                t.nom = inputTemplate.nom.Clone()
            else:
                t.nom.Add(inputTemplate.nom.Clone())

            # add systematic templates
            for sys in inputTemplate.systs:    
                if not sys in t.up:
                    t.up[sys] = inputTemplate.up[sys].Clone()
                else:
                    t.up[sys].Add(inputTemplate.up[sys].Clone())
                if not sys in t.dn:
                    t.dn[sys] = inputTemplate.dn[sys].Clone()
                else:
                    t.dn[sys].Add(inputTemplate.dn[sys].Clone())

            inputTemplate.partOfMerged = True

        t.loaded = True
        return t

    def setStyle(self, color = None, label = None):
        # set color and label of template
        if not color is None:
            self.color = color
        if not label is None:
            self.label = label

    def loadTemplates(self, hp):
        '''
        load all the templates from the input files 
        '''
        if self.loaded: return

        # load templates from rootfile
        nomKeyName = hp.GetNomKeyName(self.procName, hp.channelName)
        if not hp.rf.GetListOfKeys().Contains(nomKeyName):
            printer.printWarning("key {} does not exist".format(nomKeyName))
            self.error = True

        self.nom = hp.rf.Get(nomKeyName)

        # load varied templates
        self.up = {}
        self.dn = {}
        for sys in self.systs:
            # load up and down variations
            upKeyName = hp.GetSysKeyName(self.procName, hp.channelName, sys+"Up")
            dnKeyName = hp.GetSysKeyName(self.procName, hp.channelName, sys+"Down")
            if not hp.rf.GetListOfKeys().Contains(upKeyName):
                printer.printWarning("sys key {} does not exist".format(upKeyName))
                self.error = True
            if not hp.rf.GetListOfKeys().Contains(dnKeyName):
                printer.printWarning("sys key {} does not exist".format(dnKeyName))
                self.error = True
            self.up[sys] = hp.rf.Get(upKeyName)
            self.dn[sys] = hp.rf.Get(dnKeyName)
        
        if self.error:
            sys.exit()
        self.loaded = True

    def modifyTemplates(self, hp):
        '''
        check if overflow needs to be moved 
        or template is supposed to be divided by bin width
        '''
        if not self.loaded:
            self.loadTemplates(hp)

        if hp.moveOverflow:
            hpUtil.moveOverflow(self.nom)
        if hp.divideByBinWidth:
            hpUtil.divideByBinWidth(self.nom)
    
        for sys in self.systs:
            if hp.moveOverflow:
                hpUtil.moveOverflow(self.up[sys])
                hpUtil.moveOverflow(self.dn[sys])
            if hp.divideByBinWidth:
                hpUtil.divideByBinWidth(self.up[sys])
                hpUtil.divideByBinWidth(self.dn[sys])


    def loadErrorbands(self, addStatErrorband = True, linear = False):
        """
        saves all residues of the variations in dictionaries, sorted by sysGroup
        can change between linear and quadratic summation of residues
        also saves stat error band
        """
        if self.isData: return

        printer.printInfo("\tloading errorbands for process {}".format(self.procName))
        # setup dictionaries for residuals per bin
        self.upValues = {}
        self.dnValues = {}
    
        # loop over systematics
        for sys in self.systs:

            # check which group the systematic belongs to
            group = self.systs[sys]
            # initialize group if it doesnt exist yet
            if not group in self.upValues:
                self.upValues[group] = np.zeros(self.nom.GetNbinsX())
            if not group in self.dnValues:
                self.dnValues[group] = np.zeros(self.nom.GetNbinsX())

            # loop over bins and get residuals
            for iBin in range(self.nom.GetNbinsX()):
                uRes = self.up[sys].GetBinContent(iBin+1) - self.nom.GetBinContent(iBin+1)
                dRes = self.dn[sys].GetBinContent(iBin+1) - self.nom.GetBinContent(iBin+1)
                # figure out which of these goes up and which goes down
                u = max(uRes, dRes)
                d = min(uRes, dRes)
                # only consider positive up and negative down variations
                u = max(0., u)
                d = min(0., d)

                # add to up/dnValues
                if linear:
                    self.upValues[group][iBin] += abs(u)
                    self.dnValues[group][iBin] += abs(d)
                else:
                    self.upValues[group][iBin] = np.sqrt(
                        self.upValues[group][iBin]**2 + u**2)
                    self.dnValues[group][iBin] = np.sqrt(
                        self.dnValues[group][iBin]**2 + d**2)

        # stat error
        self.upValues["stat"] = np.zeros(self.nom.GetNbinsX())
        self.dnValues["stat"] = np.zeros(self.nom.GetNbinsX())
        for iBin in range(self.nom.GetNbinsX()):
            self.upValues["stat"][iBin] = self.nom.GetBinError(iBin+1)
            self.dnValues["stat"][iBin] = self.nom.GetBinError(iBin+1)
        
        
    def defineUncertaintyGroup(self, name, members, linear = False):
        '''
        build group of uncertainties as new errorband from already defined groups
        '''
        if self.isData: return
        # check if group already defined
        if name in self.allGroups:
            printer.printError("group {} already defined".format(name))
            sys.exit()

        # just consider members that are actually defined for this process
        members = [m for m in members if m in self.allGroups]

        # check availability of members
        for m in members:
            if not (m in self.upValues and m in self.dnValues):
                printer.printError("group {} not in list of sysGroups".format(m))
                sys.exit()

        # init new residual array       
        self.upValues[name] = np.zeros(self.nom.GetNbinsX())
        self.dnValues[name] = np.zeros(self.nom.GetNbinsX())

        # add all the residuals from the members groups
        for member in members:
            for iBin in range(self.nom.GetNbinsX()):
                if linear:
                    self.upValues[name][iBin] += self.upValues[member][iBin]
                    self.dnValues[name][iBin] += self.dnValues[member][iBin]
                else:
                    self.upValues[name][iBin] = np.sqrt(
                        self.upValues[name][iBin]**2 + self.upValues[member][iBin]**2)
                    self.dnValues[name][iBin] = np.sqrt(
                        self.dnValues[name][iBin]**2 + self.dnValues[member][iBin]**2)

        # check if it has overlap with other predefined group
        addable = True
        for member in members:
            if not member in self.majorSystGroups:
                addable = False

        
        # remove member groups from majorSyst set if no overlap
        if not addable:
            printer.printWarning(
                "\tmerged systGroup {} not addable to systs "
                "due to overlap with other merged groups".format(name))
        else:
            # delete members from majorsystgroups
            for member in members:
                self.majorSystGroups.remove(member)
            self.majorSystGroups.update([name])

        # add group name to keep track
        self.allGroups.update(name)


