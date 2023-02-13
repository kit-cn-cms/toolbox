import ROOT
ROOT.gStyle.SetEndErrorSize(3.)
ROOT.gROOT.SetBatch(True)
ROOT.PyConfig.IgnoreCommandLineOptions = True

import os
import sys
import numpy as np

from pprint import pprint

import toolbox
import toolbox.plotSetup as ps
from optparse import OptionParser

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def splitEqualy(a, n):
    k, m = divmod(len(a), n)
    return (a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n))

def drawPulls(fitResults, fitLabels=["s","b"], plotPath="pulls", plotOptions = [], nPerPage=None, nPages=None):
    plotName = os.path.basename(plotPath)

    assert(len(fitResults) == len(fitLabels)), "need to provide same number of fit results and fit labels"

    nuisances = []
    for fit in fitResults:
        nuisances += fit.keys()
    nuisances = sorted(list(set(nuisances)))
    print(nuisances)
    if nPerPage != None and nPages == None:
        nuis_chunks = list(chunks(nuisances, nPerPage))
    elif nPerPage == None and nPages != None:
        nuis_chunks = splitEqualy(nuisances, nPages)
    else:
        nuis_chunks = [nuisances]

    for index,nuisances in enumerate(nuis_chunks):

        nBins = len(nuisances)
        nFits = len(fitLabels)
        scale = 1.
        if nFits>4: scale = 0.5
        if nFits>8: scale = 0.25
        offset = (nFits-1)/10.

        xVals = np.arange(0.5, nBins+0.5)
        xErrs = np.array([0.]*nBins)

        pulls = {}
        maxValue = 2.
        minValue = -2.
        for i, fit in enumerate(fitLabels):
            thisFit = fitResults[i]
            pulls[fit] = {}
            up, mu, down = [], [], []

            for nuis in nuisances:
                if nuis in thisFit:
                    up.append(thisFit[nuis].up)
                    mu.append(thisFit[nuis].mu)
                    down.append(thisFit[nuis].down)
                else:
                    up.append(0.)
                    mu.append(0.)
                    down.append(0.)
            pulls[fit]["up"] = np.array(up)
            pulls[fit]["mu"] = np.array(mu)
            pulls[fit]["down"] = np.array(down)
            # print(pulls)
            maxValue = max(maxValue, max(pulls[fit]["mu"]+pulls[fit]["up"]))
            minValue = min(minValue, min(pulls[fit]["mu"]-pulls[fit]["down"]))
        
        maxValue = int(maxValue)+1
        minValue = int(minValue)-1
        

        # draw line at zero
        zeroLine = ps.getLineWithAxisSetup(
            plotName = plotName, nBins = nBins, yValue = 0., yErr = 1.,
            yMin = minValue, yMax = maxValue, xLabels = nuisances,
            yLabel = "(#hat{#theta}-#theta_{0})/#Delta#theta")
        zeroLine.GetXaxis().SetLabelSize(zeroLine.GetXaxis().GetLabelSize()*0.5)
        zeroLine.GetYaxis().SetTitleSize(zeroLine.GetYaxis().GetTitleSize()*1.2)
        zeroLine.LabelsOption("v")
        # zeroLine.SetTitle("Nuisance Parameters")
        zeroLine.SetTitle("")


        
        for idx, fit in enumerate(fitLabels):
            thisFit = pulls[fit]
            points = np.array([x+(idx*0.2-offset)*scale for x in xVals])
            g = ROOT.TGraphAsymmErrors(nBins, points, thisFit["mu"],
                xErrs, xErrs, thisFit["down"], thisFit["up"])

            if fit in plotOptions:
                color = toolbox.checkArgument("color", plotOptions[fit], default = str(61+2*idx))
                color = eval(color)
            else:
                if fit.startswith("s+b"):
                    color = ROOT.kRed
                elif fit.startswith("b-only"):
                    color = ROOT.kBlue
                else:
                    color = idx+1

            g.SetLineColor(color)
            g.SetMarkerColor(color)
            g.SetMarkerStyle(20)
            g.SetMarkerSize(1)
            g.SetLineWidth(2)

            pulls[fit]["g"] = g.Clone()

        canvas = ps.getCanvas(name = plotName, pulls = True)
        canvas.cd(1)


        zeroLine.Draw("e2")
        zeroLine.Draw("histsame")
        zeroLine.GetXaxis().SetLabelSize(zeroLine.GetXaxis().GetLabelSize()*1.5)
        for fit in fitLabels:
            pulls[fit]["g"].Draw("same ep")
        canvas.SetGridx()
        canvas.RedrawAxis()
        canvas.RedrawAxis("g")

        legend = ps.getLegend(pulls = True)
        for fit in fitLabels:
            legend.AddEntry(pulls[fit]["g"], fit, "EPL")
        legend.AddEntry(zeroLine, "prefit", "FL")
        legend.Draw("same")

        # if plotPath != "pulls":
        #     ps.printCustomLabel(canvas, label = plotPath, 
        #     ratio = False, wideCanvas = False, pulls = True)


        canvas.SaveAs(plotPath+"_pulls_{}.pdf".format(index))
        canvas.SaveAs(plotPath+"_pulls_{}.png".format(index))
        canvas.Clear()


parser = OptionParser()
parser.add_option("--include-mcstat", dest = "exclude_mcstat",
    default = True, action = "store_false",
    help = "include mc stat uncertainties in the pull plots")
parser.add_option("--include-only", dest = "include_only",
    default = None,
    help = "regex of nuisance parameters to include in plot")
parser.add_option("--exclude", dest = "exclude",
    default  = None,
    help = "regex of nuisance parameters to exclude in plot")
parser.add_option("--exclude-bonly", dest = "include_bonly",
    default = True, action = "store_false",
    help = "dont plot background only plots")
parser.add_option("--exclude-sb", dest = "include_sb",
    default = True, action = "store_false",
    help = "dont plot s+b pulls")
parser.add_option("-u", "--unblind", dest = "unblind",
    default = False, action = "store_true",
    help = "also show pulls for POI r")
parser.add_option("--check_fit_status", dest = "check_fit_status",
    default = False, action = "store_true",
    help = "stop if fit status is not good")
parser.add_option("-o", "--output", dest = "output",
    default = None, help="output filename")
parser.add_option("-n", "--nPerPage", dest = "nPerPage",
    default = None, help="Number of nuisances per page", type="int")
parser.add_option("-p", "--nPages", dest = "nPages",
    default = None, help="Number of pages to distribute pulls to", type="int")
parser.add_option("-H", "--hilfe", dest = "help",
    default = False, action="store_true", help="print this help message")

(opts, args) = parser.parse_args()

if opts.help:
    parser.print_help()
    sys.exit(0)
if opts.output is None:
    opts.output = os.path.basename(args[0]).replace(".root", "")

# if not opts.unblind:
    # if opts.exclude is None:
        # opts.exclude = "r"
    # else:
        # opts.exclude += "|'\ r \b'"
print(opts.exclude)
# exit()

pulls =[]
for fit in args:
    pulls.append(toolbox.Pulls(fit,opts))

results = []
labels = []
for i, pull in enumerate(pulls):
    if opts.include_sb:
        results.append(pull.results["s"])
        if len(args) == 1:
            labels.append("s+b")
        else:
            labels.append(os.path.basename(args[i]).replace(".root", "")+" s+b "+str(i))
    if opts.include_bonly:
        results.append(pull.results["b"])
        if len(args) == 1:
            labels.append("b-only")
        else:
            labels.append(os.path.basename(args[i]).replace(".root", "")+" b-only "+ str(i))

drawPulls(  fitResults= results,
            fitLabels = labels,
            plotPath  = opts.output,
            nPerPage  = opts.nPerPage,
            nPages    = opts.nPages)
