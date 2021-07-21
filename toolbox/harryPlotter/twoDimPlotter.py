from toolbox import printer
from toolbox import plotSetup as p
import ROOT

def plotTwoDim(inputFile, inputTemplate, outputPath, 
        xLabel = None, yLabel = None, plotLabel = None, processLabel = None,
        addBinLabels = False, logY = False, zRange = None, palette = None):
    printer.printAction("creating two dimensional plot of {}".format(inputTemplate))
    
    c = p.getCanvas(name = inputTemplate, twodim = True)
    c.SetBottomMargin(0.1)
    c.SetLeftMargin(0.1)
    c.SetTopMargin(0.1)
    c.SetRightMargin(0.1)
    if logY:
        c.SetLogy()

    if not palette is None:
        ROOT.gStyle.SetPalette(getattr(ROOT, palette))
    f = ROOT.TFile.Open(inputFile)
    t = f.Get(inputTemplate)
    t.SetStats(False)

    if not xLabel is None:
        t.GetXaxis().SetTitle(xLabel)
    if not yLabel is None:
        t.GetYaxis().SetTitle(yLabel)
    if not processLabel is None:
        t.SetTitle(t.GetTitle()+" ({})".format(processLabel))
    t.Draw("colz text1")
    if not plotLabel is None:
        p.printChannelLabel(c, plotLabel, ratio = False)
    if addBinLabels:
        ROOT.gStyle.SetPaintTextFormat(".3f")
        t.SetMarkerColor(ROOT.kBlack)
        t.SetMarkerSize(1.5)
    if not zRange is None:
        zmin, zmax = zRange.split(",")
        t.GetZaxis().SetRangeUser(float(zmin),float(zmax))
    c.Draw("axis same")
    c.SaveAs(outputPath)
    c.SaveAs(outputPath.replace(".pdf", ".png"))
    f.Close()
