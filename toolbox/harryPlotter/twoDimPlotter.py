from toolbox import printer
from toolbox import plotSetup as p
import ROOT

def plotTwoDim(inputFile, inputTemplate, outputPath, 
        xLabel = None, yLabel = None, plotLabel = None, processLabel = None):
    printer.printAction("creating two dimensional plot of {}".format(inputTemplate))

    c = p.getCanvas(name = inputTemplate, twodim = True)

    f = ROOT.TFile.Open(inputFile)
    t = f.Get(inputTemplate)
    t.SetStats(False)

    if not xLabel is None:
        t.GetXaxis().SetTitle(xLabel)
    if not yLabel is None:
        t.GetYaxis().SetTitle(yLabel)
    if not processLabel is None:
        t.SetTitle(t.GetTitle()+" ({})".format(processLabel))
    t.Draw("colz")
    if not plotLabel is None:
        p.printChannelLabel(c, plotLabel, ratio = False)
    c.SaveAs(outputPath)
    f.Close()
