import ROOT
ROOT.gROOT.SetBatch(True)

from toolbox import printer

class HPSetters:
    
    def SetNominalKey(self, key):
        self.nominalKey = key

    def SetSystematicKey(self, key):
        self.systKey = key

    def SetDataName(self, name):
        self.dataName = name

    def SetChannelName(self, name):
        self.channelName = name

    def SetDivideByBinWidth(self, val):
        self.divideByBinWidth = val

    def SetMoveOverflow(self, val):
        self.moveOverflow = val

    def SetSumSystsOfProcess(self, linear):
        self.sumSystsOfProcessLinear = linear

    # getters
    def GetNomKeyName(self, proc, channel):
        nomKey = self.nominalKey
        nomKey = nomKey.replace("$PROCESS", proc)
        nomKey = nomKey.replace("$CHANNEL", channel)
        return nomKey

    def GetSysKeyName(self, proc, channel, sys):
        sysKey = self.systKey
        sysKey = sysKey.replace("$PROCESS", proc)
        sysKey = sysKey.replace("$CHANNEL", channel)
        sysKey = sysKey.replace("$SYSTEMATIC", sys)
        return sysKey


class HSSetters:
    def __init__(self, nameTag = None):
        self.nameTag = nameTag

        self.setPlottingOrder()
        self.setHighestIntegralOnTop()
        self.setIncludeOnly()
        self.setPlotAsLine()
        self.setPlotInStack()
        self.setPlotAsBoth()
        self.setDontPlot()

        self.setLogY()
        self.setUseRealData()
        self.setPseudodataProcesses()
        self.setDataLabel()
        self.setPseudodataLabel()
        self.setPrivateWork()
    
        self.setPlotBlind()
        self.setStatError()
        self.setRemoveSystErrors()
        self.setErrorbandOnLines()
        self.setScaleLineErrors()
        self.setOnlyPlotErrorGroups()

        self.setRatio()
        self.setRatioLabel()
        self.setDifferenceRatio()
        self.setDifferenceRatioLabel()

        self.setSumSystsBetweenProcesses()

    def __str__(self):
        printer.printAction("\t==== Histogram Setup Summary ====")
        printer.printInfo("\tPlottingOrder:        {}".format(self.plottingOrder))
        printer.printInfo("\tHighestIntegralOnTop: {}".format(self.highestIntegralOnTop))
        printer.printInfo("\tIncludeOnly:          {}".format(self.includeOnly))
        printer.printInfo("\tPlotAsLine:           {}".format(self.plotAsLine))
        printer.printInfo("\tPlotAsBoth:           {}".format(self.plotAsBoth))
        printer.printInfo("\tLogY:                 {}".format(self.logY))
        printer.printInfo("\tPlotBlind:            {}".format(self.plotBlind))
        if not self.plotBlind:
            printer.printInfo("\tUseRealData:          {}".format(self.realData))
            if not self.realData:
                printer.printInfo("\tPseudodataProcesses   {}".format(self.pseudodataProcesses))
                printer.printInfo("\tPseudodataLabel:      {}".format(self.pseudodataLabel))
            else:
                printer.printInfo("\tDataLabel:            {}".format(self.dataLabel))
        printer.printInfo("\tPrivateWork:          {}".format(self.privateWork))
        printer.printInfo("\tAddStatError:         {}".format(self.statError))
        printer.printInfo("\tRemoveSystErrors:     {}".format(self.removeSystErrors))
        if self.statError or not self.removeSystErrors:
            printer.printInfo("\tErrorbandOnLines:     {}".format(self.errorbandOnLines))
            printer.printInfo("\tScaleLineErrors:      {}".format(self.scaleLineErrors))
            printer.printInfo("\tOnlyPlotErrorGroups:  {}".format(self.onlyPlotErrorGroups))
        printer.printInfo("\tAddRatio:             {}".format(self.ratio))
        if self.ratio:
            printer.printInfo("\tRatioLabel:           {}".format(self.ratioLabel))
        printer.printInfo("\tAddDifferenceRatio:   {}".format(self.differenceRatio))
        if self.differenceRatio:
            printer.printInfo("\tDifferenceRatioLabel: {}".format(self.differenceRatioLabel))
        return ""

    def setPlottingOrder(self, plottingOrder = []):
        self.plottingOrder = plottingOrder

    def setHighestIntegralOnTop(self, val = True):
        self.highestIntegralOnTop = val

    def setIncludeOnly(self, processes = None):
        self.includeOnly = processes

    def setPlotAsLine(self, processes = {}):
        self.plotAsLine = processes

    def setPlotInStack(self, processes = []):
        for p in processes:
            if p in self.plotAsLine:
                self.plotAsLine.pop(p)

    def setPlotAsBoth(self, processes = {}):
        self.plotAsBoth = processes
        for p in processes:
            if p in self.plotAsLine:
                self.plotAsLine.pop(p)

    def setDontPlot(self, processes = []):
        for p in processes:
            if p in self.plotAsLine:
                self.plotAsLine.pop(p)
            if p in self.includeOnly:
                self.includeOnly = [
                    io for io in self.includeOnly if not io == p]
    
    def setLogY(self, logY = False):
        self.logY = logY

    def setUseRealData(self, val = True):
        self.realData = val
        
    def setPseudodataProcesses(self, processes = None):
        self.pseudodataProcesses = processes

    def setDataLabel(self, label = "Data"):
        self.dataLabel = label

    def setPseudodataLabel(self, label = "Pseudo Data"):
        self.pseudodataLabel = label

    def setPrivateWork(self, val = True):
        self.privateWork = val

    def setPlotBlind(self, val = False):
        self.plotBlind = val

    def setStatError(self, val = True):
        self.statError = val

    def setRemoveSystErrors(self, val = False):
        self.removeSystErrors = val

    def setErrorbandOnLines(self, val = False):
        self.errorbandOnLines = val

    def setScaleLineErrors(self, val = True):
        self.scaleLineErrors = val

    def setOnlyPlotErrorGroups(self, groups = None):
        self.onlyPlotErrorGroups = groups


    def setRatio(self, val = True):
        self.ratio = val

    def setRatioLabel(self, label = "#frac{$DATA}{Background}"):
        self.ratioLabel = label


    def setDifferenceRatio(self, val = False):
        self.differenceRatio = val

    def setDifferenceRatioLabel(self, label = "$DATA - Background"):
        self.differenceRatioLabel = label


    def setSumSystsBetweenProcesses(self, linear = False):
        self.sumSystsBetweenProcessesLinear = linear

    def setStackLineWidth(self, val = 1):
        self.stackLineWidth = val

