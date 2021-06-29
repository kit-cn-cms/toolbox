import ROOT

import sys
import numpy as np

from toolbox import printer
from toolbox import plotSetup as ps
import hpUtil
from Setters import HSSetters

class HistogramSetup(HSSetters):
    def getStackTemplatesInOrder(self, templates):
        '''
        loop over all templates and find out if they are to be put into the stack 
        then order them by stacking order defined by integral or the plottingOrder
        '''
        stackTemplates = []
        # loop over templates and get all that are to be in stack
        for proc in templates:
            if templates[proc].isData: continue
            if templates[proc].partOfMerged: continue
            if proc in self.plotAsLine: continue
            if not self.includeOnly is None:
                if not proc in self.includeOnly:
                    continue
            stackTemplates.append(proc)
        
        # get integral values of templates
        stackIntegrals = {p: templates[p].nom.Integral() for p in stackTemplates}

        # sort by integral (biggest first)
        orderedTemplates = []
        for proc in sorted(stackIntegrals, key=stackIntegrals.get, reverse=True):
            if proc in self.plottingOrder: continue
            orderedTemplates.append(proc)

        # reverse the order if option is set
        if self.highestIntegralOnTop:
            orderedTemplates.reverse()

        # append the processes predefined by plottingOrder
        orderedTemplates+=self.plottingOrder

        # returns list of processes. first process is lowest in stack
        return orderedTemplates

    def getLineTemplates(self, templates, stackIntegral):
        '''
        get all templates that are to be plot as lines with their scaling factor
        '''
        lineTemplates = {}
        # loop over templates and get all that are to be lines
        for proc in templates:
            if templates[proc].isData: continue
            if templates[proc].partOfMerged: continue
            if not self.includeOnly is None:
                if not proc in self.includeOnly:
                    continue
            if proc in self.plotAsLine:
                lineTemplates[proc] = self.plotAsLine[proc]
            if proc in self.plotAsBoth:
                lineTemplates[proc] = self.plotAsBoth[proc]

        lineHistograms = {}
        lineErrors = {}
        for proc in lineTemplates:
            lineHistograms[proc] = templates[proc].nom.Clone()
            scale = lineTemplates[proc]
            if scale == -1:
                scale = stackIntegral/(lineHistograms[proc].Integral()+1e-10)
            lineTemplates[proc] = scale
            lineHistograms[proc].Scale(scale)

            lineErrors[proc] = {}
            if self.scaleLineErrors:
                errorScale = scale
            else:
                errorScale = 1.
            # loop over systematics 
            for sys in templates[proc].upValues:
                lineErrors[proc][sys] = ROOT.TGraphAsymmErrors(lineHistograms[proc].Clone())
                for iBin in range(lineHistograms[proc].GetNbinsX()):
                    lineErrors[proc][sys].SetPointEYlow( 
                        iBin, templates[proc].dnValues[sys][iBin]*errorScale)
                    lineErrors[proc][sys].SetPointEYhigh(
                        iBin, templates[proc].upValues[sys][iBin]*errorScale)
                    lineErrors[proc][sys].SetPointEXlow( 
                        iBin, lineHistograms[proc].GetBinWidth(iBin+1)/2.)
                    lineErrors[proc][sys].SetPointEXhigh( 
                        iBin, lineHistograms[proc].GetBinWidth(iBin+1)/2.)

        '''
        lineTemplates:  {procName: lineScale}
        lineHistograms: {procName: template}
        lineErrors:     {procName: {sysGroup: errorband}}
        '''
        return lineTemplates, lineHistograms, lineErrors

    def getData(self, templates):
        '''
        get data template based on either real data or pseudo date
        also edits the uncertainties of pseudo data to be sqrt(N)
        '''
        if self.realData:
            printer.printInfo("\tloading real data histogram")
            data = templates["data_obs"].nom.Clone()
            return data

        else:
            printer.printInfo("\tloading pseudo data histogram")
            # get list of pseudodata processes
            processes = self.pseudodataProcesses
            # if no information is given just use the background
            if processes is None:
                processes = []
                for proc in templates:
                    if templates[proc].isData: continue
                    if templates[proc].partOfMerged: continue
                    if proc in self.plotAsLine: continue
                    if not self.includeOnly is None:
                        if not proc in self.includeOnly:
                            continue
                    processes.append(proc)

            # build pseudodata histogram
            pseudodata = None
            for proc in processes:
                if pseudodata is None:
                    pseudodata = templates[proc].nom.Clone()
                else:
                    pseudodata.Add(templates[proc].nom.Clone())

            # set poissonian bin error
            for iBin in range(pseudodata.GetNbinsX()):
                pseudodata.SetBinError(iBin+1, np.sqrt(pseudodata.GetBinContent(iBin+1)))
            return pseudodata

    def stackTemplates(self, templates, stackTemplates):
        '''
        stack templates for plotting
        also load the uncertainty bands for the stack
        '''
        stackedHistograms = []
        stackResUp = {}
        stackResDn = {}
        
        # build histogram stacks
        stack = None
        tempTemplates = [t for t in stackTemplates]
        for proc in tempTemplates:
            printer.printInfo("\tstacking: "+proc)
            if not proc in templates:
                printer.printWarning(
                    "\tprocess {} is not defined".format(proc))
                stackTemplates.pop(stackTemplates.index(proc))
                continue
            # adding template to stakc
            if stack is None:
                stack = templates[proc].nom.Clone()
            else:
                stack.Add(templates[proc].nom.Clone())
            stackedHistograms.append(stack.Clone())

            # looping over defined systematics
            for sys in templates[proc].upValues:
                if not sys in stackResUp:
                    stackResUp[sys] = np.zeros(templates[proc].nom.GetNbinsX())
                if not sys in stackResDn:
                    stackResDn[sys] = np.zeros(templates[proc].nom.GetNbinsX())
                # stat uncertainty is directly inferred from binerror of stack
                if sys == "stat":
                    for iBin in range(templates[proc].nom.GetNbinsX()):
                        stackResUp[sys][iBin] = stack.GetBinError(iBin+1)
                        stackResDn[sys][iBin] = stack.GetBinError(iBin+1)
                    continue
                # looping over bins of other systs and adding them lin/quad
                for iBin in range(templates[proc].nom.GetNbinsX()):
                    if self.sumSystsBetweenProcessesLinear:
                        stackResUp[sys][iBin] += templates[proc].upValues[sys][iBin]
                        stackResDn[sys][iBin] += templates[proc].dnValues[sys][iBin]
                    else:
                        stackResUp[sys][iBin] = np.sqrt(
                            stackResUp[sys][iBin]**2 + templates[proc].upValues[sys][iBin]**2)
                        stackResDn[sys][iBin] = np.sqrt(
                            stackResDn[sys][iBin]**2 + templates[proc].dnValues[sys][iBin]**2)

        # build TAsymErrorGraphs
        stackErrors = {}
        for sys in stackResDn:
            stackErrors[sys] = ROOT.TGraphAsymmErrors(stack.Clone())
            for iBin in range(stack.GetNbinsX()):
                stackErrors[sys].SetPointEYlow( iBin, stackResDn[sys][iBin])
                stackErrors[sys].SetPointEYhigh(iBin, stackResUp[sys][iBin])
                stackErrors[sys].SetPointEXlow( iBin, stack.GetBinWidth(iBin+1)/2.)
                stackErrors[sys].SetPointEXhigh(iBin, stack.GetBinWidth(iBin+1)/2.)

        return stackedHistograms, stackErrors
                
    def getStackIntegral(self, stackedHistograms):
        '''
        get integral of stack and flag if there even is a stack
        '''
        hasHistStack = False
        stackIntegral = 1.
        if len(stackedHistograms) > 0:
            stackIntegral = stackedHistograms[-1].Integral()
            hasHistStack = True
        
        return hasHistStack, stackIntegral

    def getPlotRange(self, stackedHistograms, lineHistograms):
        ''' 
        determine x-axis plot range
        '''
        yMax = 0.
        yMinMax = 1e10
        for h in [stackedHistograms[-1]]+lineHistograms.values():
            yMax =    max(yMax, h.GetBinContent(h.GetMaximumBin()))
            yMinMax = min(yMinMax, h.GetBinContent(h.GetMaximumBin()))
        if self.logY:   
            return yMinMax/1000+1e-10, yMax*10
        else:
            return 1e-2, yMax*1.5

    def getDataInfo(self, histStack = True):
        '''
        get info if data is used and label for data
        '''
        # determine if data is used
        # data will not be used of there is no stack of histograms
        useData = ((not self.plotBlind) and histStack)

        # get data label    
        if self.realData:
            dataLabel = self.dataLabel
        else:
            dataLabel = self.pseudodataLabel

        return useData, dataLabel


    def getRatioInfo(self, useData):
        '''
        figure out of there is a ratio plot and which one
        also determine the canvas indices for the ratios
        '''
        doRatio     = False
        doubleRatio = False

        # canvas index of ratios
        fracIdx = 2
        diffIdx = 3

        if (self.ratio or self.differenceRatio) and useData:
            doRatio = True
            if self.ratio and self.differenceRatio:
                doubleRatio = True
            if not self.ratio:
                diffIdx = 2

        return doRatio, doubleRatio, fracIdx, diffIdx

    def getyTitle(self, divideByBinWidth, xLabel):
        '''
        get title on y axis
        per default it is 'Events'
        '''
        yTitle = "Events"
    
        # add info when divide by bin width was activated
        if divideByBinWidth:
            if xLabel.endswith("[GeV]"):
                yTitle+= " / GeV"
            else:
                yTitle+= " / bin width"

        return yTitle

    def setupHistogram(self, h, line, yMin, yMax, yTitle, xLabel, fillColor, doRatio):
        '''
        set plotting style for histograms in stack and as lines
        '''
        # edit range
        h.GetYaxis().SetRangeUser(yMin, yMax)

        # edit y axis
        h.GetYaxis().SetTitle(yTitle)
        h.GetYaxis().SetTitleSize(
            h.GetYaxis().GetTitleSize()*1.5)
        h.GetYaxis().SetLabelSize(
            h.GetYaxis().GetLabelSize()*1.2)

        # edit x axis
        h.GetXaxis().SetTitle("")
        if not doRatio:
            h.GetXaxis().SetTitle(xLabel)

        # edit title an stats
        h.SetTitle("")
        h.SetStats(False)

        # edit plotting style
        if line:
            h.SetFillColor(0)
            h.SetLineColor(fillColor)
            h.SetLineWidth(2)
        else:
            h.SetFillColor(fillColor)
            h.SetLineColor(ROOT.kBlack)
            h.SetLineWidth(self.stackLineWidth)



    def getListOfErrorbands(self, hasHistStack, stackTemplates, lineTemplates, templates):
        '''
        determine list of errorbands to be drawn based on the options that are set
        '''
        if self.removeSystErrors:
            errorbands = []
        elif not self.onlyPlotErrorGroups is None:
            errorbands = self.onlyPlotErrorGroups
        else:
            # TODO find better method to automatically determine syst groups
            if hasHistStack:
                errorbands = templates[stackTemplates[-1]].majorSystGroups
            else:
                errorbands = templates[lineTemplates.keys()[0]].majorSystGroups

        if self.statError:
            errorbands = list(errorbands)
            errorbands.append("stat")

        return errorbands

    def setupErrorband(self, g, syst, line = False, processColor = None):
        '''
        get style in which errorband should be drawn
        '''
        ebStyle, ebColor, ebAlpha = hpUtil.getErrorStyle(syst)
        g.SetFillStyle(ebStyle)
        if line:
            ebColor = processColor
        g.SetLineColorAlpha(ebColor, ebAlpha)
        g.SetFillColorAlpha(ebColor, ebAlpha)

    def setupDataHistogram(self, data):
        '''
        set style of data histogram
        '''
        data.SetLineColor(ROOT.kBlack)
        data.SetMarkerStyle(20)
        data.SetFillStyle(0)
        data.SetMarkerSize(1.5)
        data.SetLineWidth(1)

    def getRatioLine(self, stack, frac, dataLabel, doubleRatio, xLabel):
        '''
        get and setup line drawn to ratio plot
        works for frac and difference ratio
        adjusted with 'frac' option
        '''
        # get line from stack clone
        line = stack.Clone()
        line.Divide(line)
        line.SetFillStyle(0)
        
        # get yaxis label 
        if frac:
            label = self.ratioLabel.replace("$DATA",dataLabel)
        else:
            label = self.differenceRatioLabel.replace("$DATA",dataLabel)
        line.GetYaxis().SetTitle(label)

        # get xaxis label
        xTitle = xLabel
        if doubleRatio and frac:
            xTitle = ""
        line.GetXaxis().SetTitle(xTitle)

        # scale axis legends
        line.GetXaxis().SetLabelSize(line.GetXaxis().GetLabelSize()*2.4)
        line.GetXaxis().SetTitleSize(line.GetXaxis().GetTitleSize()*3)
        if doubleRatio and frac:
            line.GetYaxis().SetLabelSize(line.GetYaxis().GetLabelSize()*3.3)
            line.GetYaxis().SetTitleSize(line.GetYaxis().GetTitleSize()*2.5)
            line.GetYaxis().SetTitleOffset(0.3)
        else:
            line.GetYaxis().SetLabelSize(line.GetYaxis().GetLabelSize()*2.2)
            line.GetYaxis().SetTitleSize(line.GetYaxis().GetTitleSize()*1.8)
            line.GetYaxis().SetTitleOffset(0.5)

        # set bin contents and errors
        line.GetYaxis().SetNdivisions(505)
        line.GetXaxis().SetLabelOffset(0.01)
        if frac: val = 1
        else:    val = 0
        for i in range(line.GetNbinsX()):
            line.SetBinContent(i+1, val)
            line.SetBinError(i+1, 0)

        # set line style
        line.SetLineWidth(1)
        line.SetLineColor(ROOT.kBlack)

        # set range
        line.GetYaxis().SetRangeUser(0.5,1.5)

        return line 

    def getRatioData(self, data, stack, frac = True):
        '''
        get data histogram for ratio plot
        also return min and max values
        '''
        r = data.Clone()
        if frac:
            rMax = 1
            rMin = 1
            r.Divide(stack.Clone())
        else:
            rMax = 0
            rMin = 0

        for iBin in range(r.GetNbinsX()):
            if not frac:
                r.SetBinContent(iBin+1,
                    (r.GetBinContent(iBin+1)-stack.GetBinContent(iBin+1)))
            rMax = max(r.GetBinContent(iBin+1), rMax)   
            rMim = min(r.GetBinContent(iBin+1), rMin)   

        r.SetLineColor(ROOT.kBlack)
        r.SetLineWidth(1)
        r.SetMarkerStyle(20)
        ROOT.gStyle.SetErrorX(0)
        return r, rMin, rMax
        
    def setupRatioErrorband(self, g, frac = True):
        '''
        setup errorband for ratio plot
        adjust errorband size to ratio
        '''
        for iBin in range(g.GetN()):
            x = g.GetPointX(iBin)
            y = g.GetPointY(iBin)
            #g.GetPoint(iBin, x, y)
            if not frac:
                g.SetPoint(iBin, x, 1)
            else:
                g.SetPoint(iBin, x, 1)
                if y > 0:
                    g.SetPointEYlow( iBin,  g.GetErrorYlow(iBin)/y)
                    g.SetPointEYhigh(iBin, g.GetErrorYhigh(iBin)/y)
                else:
                    g.SetPointEYlow(iBin, 0)
                    g.SetPointEYhigh(iBin, 0)




    def drawHistogram(self, plotName, xLabel, channelLabel, lumi, 
            divideByBinWidth, outFile, templates):
        ''' 
        routine to setup the histograms
        get stack histograms, line histograms and data
        plot them in first canvas and add errorbands
        add fractional ratio and difference ratio plot including errorbands
        '''

        # figure out which processes in which order are included in the stack
        # lowest is first
        stackTemplates = self.getStackTemplatesInOrder(templates)

        # get list of stack histograms and also TGraphAsymErrors for uncertainties
        stackedHistograms, stackErrors = self.stackTemplates(templates, stackTemplates)

        # get stack integral
        hasHistStack, stackIntegral = self.getStackIntegral(stackedHistograms)
    
        # get histogram lines to be plotted
        lineTemplates, lineHistograms, lineErrors = self.getLineTemplates(templates, stackIntegral)

        # get data
        useData, dataLabel = self.getDataInfo(hasHistStack)
        if useData:
            data = self.getData(templates)

        # get plotting range 
        yMin, yMax = self.getPlotRange(stackedHistograms, lineHistograms)

        # get info about ratios
        doRatio, doubleRatio, fracIdx, diffIdx = self.getRatioInfo(useData)

        # get yTitle
        yTitle = self.getyTitle(divideByBinWidth, xLabel)
    
        # load canvas
        c = ps.getCanvas(plotName,
            log         = self.logY,
            ratio       = doRatio,
            doubleRatio = doubleRatio,
            sideLegend  = True
            )

        # determine which errorbands to use
        errorbands = self.getListOfErrorbands(
            hasHistStack, stackTemplates, lineTemplates, templates)

        # plot stack histograms on canvas
        c.cd(1)
        nLegendEntries = 0
        firstPlot = True
        print(stackTemplates)
        print(stackedHistograms)
        for idx in range(len(stackTemplates)-1, -1, -1):
            proc = stackTemplates[idx]
            printer.printInfo("\tadding process to stack {}".format(proc))

            self.setupHistogram(stackedHistograms[idx], False,
                yMin, yMax, yTitle, xLabel, templates[proc].color, doRatio)

            # draw histogram
            if firstPlot:
                stackedHistograms[idx].Draw("histo")
                firstPlot = False
            else:
                stackedHistograms[idx].Draw("histo same")
        
            nLegendEntries+=1

        # add errorbands on stack
        for syst in errorbands:
            printer.printInfo("\tadding errorband {} on stack".format(syst))
            if not syst in stackErrors:
                printer.printWarning("\t\tno errorband for sys group {} found".format(syst))
                continue
            self.setupErrorband(stackErrors[syst], syst, line = False)

            # draw errorband
            stackErrors[syst].Draw("same2")
            nLegendEntries+=1
            
        # plot all the lines to be plot
        for line in lineTemplates:
            printer.printInfo("\tdrawing histogram line {}".format(line))

            # setup histogram
            self.setupHistogram(lineHistograms[line], True,
                yMin, yMax, yTitle, xLabel, templates[line].color, doRatio)

            # draw histogram
            if firstPlot:
                lineHistograms[line].Draw("histo")
                firstPlot = False
            else:
                lineHistograms[line].Draw("histo same")

            nLegendEntries+=1

            # include errorbars on lines
            if not self.errorbandOnLines:
                continue

            # draw errorband for lines
            for syst in errorbands:
                printer.printInfo("\tadding errorband {} on line {}".format(syst, line))
                if not syst in lineErrors[line]:
                    printer.printWarning("\t\tno errorband for sys group {} found".format(syst))
                    continue

                # setup errorband
                self.setupErrorband(lineErrors[line][syst], 
                    syst, line = True, processColor = templates[line].color)

                # draw errorband
                lineErrors[line][syst].Draw("same2")


        if useData:
            # setup and draw data histogram
            self.setupDataHistogram(data)
            data.Draw("histPEX0same")       
            nLegendEntries+=1        
    
        # redraw the axis
        if hasHistStack:
            stackedHistograms[-1].Draw("axissame")

        # setup legend
        l = ROOT.TLegend(0.81,0.93*(1.-nLegendEntries/14.),0.98,0.93)
        l.SetBorderSize(0)
        # add data entry
        if useData:
            l.AddEntry(data, dataLabel, "P")
        # add line entries
        for line in lineTemplates:
            lineLabel = templates[line].label
            if not lineTemplates[line] == 1:
                lineLabel+= " (x {:.0f})".format(lineTemplates[line])
            l.AddEntry(lineHistograms[line], lineLabel, "L")
        # add stack entries
        for idx in range(len(stackTemplates)-1, -1, -1):
            proc = stackTemplates[idx]
            l.AddEntry(stackedHistograms[idx], templates[proc].label, "F")
        # add uncertainty entries
        for syst in errorbands:
            if not syst in stackErrors:
                continue
            l.AddEntry(stackErrors[syst], syst, "F")
        # draw legend
        l.Draw()
            
        # build fractional ratio
        if self.ratio:
            c.cd(fracIdx)
    
            # get line 
            line = self.getRatioLine(stackedHistograms[-1], True,
                dataLabel, doubleRatio, xLabel)

            # get data histogram 
            r, rMin, rMax = self.getRatioData(data, stackedHistograms[-1], True)

            # set ratio range
            line.GetYaxis().SetRangeUser(0.5, 1.5)

            # draw ratio line
            line.DrawCopy("histo")

            # draw ratio data
            r.DrawCopy("sameP")

            # add errorbands
            ratioErrors = {}
            for syst in errorbands:
                if not syst in stackErrors:
                    printer.printWarning("\t\tno errorband for sys group {} found".format(syst))
                    continue

                # setup ratio errorband
                ratioErrors[syst] = stackErrors[syst].Clone()
                self.setupRatioErrorband(ratioErrors[syst], frac = True)

                # draw errorband
                ratioErrors[syst].Draw("same2")

            # redraw the line and data
            line.DrawCopy("histo same")
            r.DrawCopy("sameP")

        # build fractional ratio
        if self.differenceRatio:
            c.cd(diffIdx)

            # get line
            dline = self.getRatioLine(stackedHistograms[-1], False,
                dataLabel, doubleRatio, xLabel)

            # get data histogram
            d, dMin, dMax = self.getRatioData(data, stackedHistograms[-1], False)

            # set ratio range
            dline.GetYaxis().SetRangeUser(
                1.5*max(dMin, -0.2*dMax), 1.5*max(dMax, -0.2*dMin))

            # draw ratio line
            dline.DrawCopy("histo")

            # draw ratio data
            d.DrawCopy("sameP")
        
            # add errorbands
            diffErrors = {}
            for syst in errorbands:
                if not syst in stackErrors:
                    printer.printWarning("\t\tno errorband for sys group {} found".format(syst))
                    continue

                # setup ratio errorband
                diffErrors[syst] = stackErrors[syst].Clone()
                self.setupRatioErrorband(diffErrors[syst], frac = False)

                # draw errorband
                diffErrors[syst].Draw("same2")

            # redraw the line and data
            dline.DrawCopy("histo same")
            d.Draw("sameP")


        # add some labels
        ps.printCMSLabel(c, privateWork = self.privateWork, ratio = doRatio)
        if not lumi is None:
            ps.printLumiLabel(c, lumi = lumi, ratio = doRatio, sideLegend = True)
        if not channelLabel is None:
            ps.printChannelLabel(c, channelLabel, ratio = doRatio)
           
        # save output
        c.SaveAs(outFile)
        c.SaveAs(outFile.replace(".pdf", ".png"))

            
