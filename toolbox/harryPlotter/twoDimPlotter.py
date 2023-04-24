from toolbox import printer
from toolbox import plotSetup as p
import ROOT

def plotTwoDim(inputFile, inputTemplate, outputPath, 
        xLabel = None, yLabel = None, plotLabel = None, processLabel = None,
        addBinLabels = None, logY = False, zRange = None, palette = None):
    printer.printAction("creating two dimensional plot of {}".format(inputTemplate))
    
    c = p.getCanvas(name = inputTemplate, twodim = True)
    c.SetBottomMargin(0.1)
    c.SetLeftMargin(0.15)
    c.SetTopMargin(0.1)
    c.SetRightMargin(0.20)
    if logY:
        c.SetLogy()

    if not palette is None:
        ROOT.gStyle.SetPalette(getattr(ROOT, palette))
    f = ROOT.TFile.Open(inputFile)
    t = f.Get(inputTemplate)
    t.SetStats(False)

    if not xLabel is None:
        t.GetXaxis().SetTitle("|"+xLabel+"|")
        t.GetXaxis().SetTitleOffset(1.3)
        t.GetXaxis().SetNdivisions(-3)
    if not yLabel is None:
        t.GetYaxis().SetTitle(yLabel+" (GeV)")
    if not processLabel is None:
        t.SetTitle(t.GetTitle()+" ({})".format(processLabel))
    t.GetZaxis().SetTitle("Efficiency")
    t.GetZaxis().SetTitleOffset(1.8)
    
    if plotLabel.endswith("_l"):
        plotLabel = "LF-jets"
    if plotLabel.endswith("_c"):
        plotLabel = "c-jets"
    if plotLabel.endswith("_b"):
        plotLabel = "b-jets"
    t.GetYaxis().SetRangeUser(30, 1000)
    c.SetLogy()
    t.SetTitle("")

    ROOT.gStyle.SetLineWidth(2)


    t.Draw("colz text1")
    # if not plotLabel is None:
        # p.printChannelLabel(c, plotLabel, ratio = False)
    if not addBinLabels is None:
        ROOT.gStyle.SetPaintTextFormat(addBinLabels)
        t.SetMarkerColor(ROOT.kBlack)
        t.SetMarkerSize(1.6)
    if not zRange is None:
        zmin, zmax = zRange.split(",")
        t.GetZaxis().SetRangeUser(float(zmin),float(zmax))

    cms = ROOT.TLatex(0.15, 0.91, 'CMS#scale[0.7]{ private work}'  )
    cms.SetNDC()
    cms.SetTextSize(0.05)
    cms.Draw("same")

    label = ROOT.TLatex(0.7, 0.91, plotLabel  )
    label.SetNDC()
    label.SetTextSize(0.04)
    label.Draw("same")



    c.Draw("axis same")
    c.SaveAs(outputPath)
    c.SaveAs(outputPath.replace(".pdf", ".png"))
    f.Close()
