from toolbox import printer
from toolbox import plotSetup as p
import ROOT

def plotTwoDim(inputFile, inputTemplate, outputPath, cmsLabel = "Simulation Preliminary",
        xLabel = None, yLabel = None, plotLabel = None, processLabel = None,
        addBinLabels = None, logY = False, logX = False, wide = False, zRange = None, palette = None,
        xaxis = None, yaxis = None
        ):
    printer.printAction("creating two dimensional plot of {}".format(inputTemplate))
    
    c = p.getCanvas(name = inputTemplate, twodim = True, wideCanvas = wide)
    c.SetBottomMargin(0.1)
    c.SetLeftMargin(0.1)
    c.SetTopMargin(0.1)
    c.SetRightMargin(0.1)
    if logY:
        c.SetLogy()
    if logX:
        c.SetLogx()

    if not palette is None:
        ROOT.gStyle.SetPalette(getattr(ROOT, palette))
    f = ROOT.TFile.Open(inputFile)
    t = f.Get(inputTemplate)
    t.SetStats(False)

    if not xLabel is None:
        t.GetXaxis().SetTitle(xLabel)
    if not yLabel is None:
        t.GetYaxis().SetTitle(yLabel)
    #if not processLabel is None:
    #    t.SetTitle(t.GetTitle()+" ({})".format(processLabel))
    #else:
    t.SetTitle("")
    if not plotLabel is None:
        p.printChannelLabel(c, plotLabel, ratio = False)
    if not addBinLabels is None:
        t.Draw("colz1 text1")
        c.SetGrid()
        ROOT.gStyle.SetPaintTextFormat(addBinLabels)
        t.SetMarkerColor(ROOT.kBlack)
        t.SetMarkerSize(0.7)
    else:
        t.Draw("colz1")
        #t.Draw("contz")
    if not xaxis is None:
        for i, elem in enumerate(xaxis.split(",")):
            if t.GetXaxis().GetNbins() < i: continue
            t.GetXaxis().SetBinLabel(i+1, elem)
    if not yaxis is None:
        for i, elem in enumerate(yaxis.split(",")):
            if t.GetYaxis().GetNbins() < i: continue
            t.GetYaxis().SetBinLabel(i+1, elem)

    if not zRange is None:
        zmin, zmax = zRange.split(",")
        t.GetZaxis().SetRangeUser(float(zmin),float(zmax))
    if not cmsLabel is None:
        p.printCMSLabel(c, privateWork = True, plotLabel = cmsLabel, ratio = False)
    c.Draw("axis same")
    c.SaveAs(outputPath)
    c.SaveAs(outputPath.replace(".pdf", ".png"))
    f.Close()
