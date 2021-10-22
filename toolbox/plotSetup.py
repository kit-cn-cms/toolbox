import ROOT

def getCanvas(name = "canvas", 
    log = False, pulls = False, 
    ratio = False, doubleRatio = False, 
    twodim = False, sideLegend = False,
    wideCanvas = False):
    x = 0
    r = 0
    w = 0
    l = 0
    if sideLegend:
        x = 256
        r = 0.15
    if wideCanvas:
        w = 768
        l = -0.05
    # generate canvas
    if doubleRatio:
        canvas = ROOT.TCanvas(name, name, 1024+x+w, 1280)
        canvas.Divide(1,3)
        canvas.cd(1).SetPad(0., 0.4, 1.0, 1.0)
        canvas.cd(1).SetTopMargin(0.07)
        canvas.cd(1).SetBottomMargin(0.0)

        canvas.cd(2).SetPad(0., 0.25, 1.0, 0.4)
        canvas.cd(2).SetTopMargin(0.0)
        canvas.cd(2).SetBottomMargin(0.0)

        canvas.cd(3).SetPad(0., 0.0, 1.0, 0.25)
        canvas.cd(3).SetTopMargin(0.0)
        canvas.cd(3).SetBottomMargin(0.1/0.25)

        canvas.cd(1).SetRightMargin(0.05+r)
        canvas.cd(2).SetRightMargin(0.05+r)
        canvas.cd(3).SetRightMargin(0.05+r)

        canvas.cd(1).SetLeftMargin(0.15+l)
        canvas.cd(2).SetLeftMargin(0.15+l)
        canvas.cd(3).SetLeftMargin(0.15+l)

        canvas.cd(1).SetTicks(1,1)
        canvas.cd(2).SetTicks(1,1)
        canvas.cd(3).SetTicks(1,1)
    elif ratio:
        canvas = ROOT.TCanvas(name, name, 1024+x+w, 1024)
        canvas.Divide(1,2)
        canvas.cd(1).SetPad(0.,0.3,1.0,1.0)
        canvas.cd(1).SetTopMargin(0.07)
        canvas.cd(1).SetBottomMargin(0.0)

        canvas.cd(2).SetPad(0.,0.0,1.0,0.3)
        canvas.cd(2).SetTopMargin(0.0)
        canvas.cd(2).SetBottomMargin(0.4)

        canvas.cd(1).SetRightMargin(0.05+r)
        canvas.cd(1).SetLeftMargin(0.15+l)
        canvas.cd(1).SetTicks(1,1)

        canvas.cd(2).SetRightMargin(0.05+r)
        canvas.cd(2).SetLeftMargin(0.15+l)
        canvas.cd(2).SetTicks(1,1)
    elif twodim:
        canvas = ROOT.TCanvas(name, name, 1024+x, 1024)
        canvas.SetBottomMargin(0.2)
        canvas.SetLeftMargin(0.2)
        canvas.SetTopMargin(0.2)   
        canvas.SetRightMargin(0.2+r)
    else:
        canvas = ROOT.TCanvas(name, name, 1024+x+w, 768)
        canvas.SetTopMargin(0.07)
        if not pulls:
            canvas.SetBottomMargin(0.15)
        if pulls:
            canvas.SetBottomMargin(0.25)
        canvas.SetRightMargin(0.05+r)
        canvas.SetLeftMargin(0.15+l)
        canvas.SetTicks(1,1)

    if log: canvas.cd(1).SetLogy()
    return canvas

def getDoubleCanvas(name = "canvas"):
    canvas = ROOT.TCanvas(name, name, 1300, 700)
    canvas.Divide(2,1)
    canvas.cd(1).SetPad(0.,0.,0.5,1.)
    canvas.cd(1).SetTopMargin(0.07)
    canvas.cd(1).SetBottomMargin(0.15)
    canvas.cd(2).SetPad(0.5,0.0,1.,1.)
    canvas.cd(2).SetTopMargin(0.07)
    canvas.cd(2).SetBottomMargin(0.15)
    return canvas

def getLegend(pulls = False, ratio = False):
    if pulls:
        legend=ROOT.TLegend(0.7,0.8,0.98,0.98)
        legend.SetFillColor(0)
        legend.SetTextFont(42)
    elif ratio:
        legend=ROOT.TLegend(0.05,0.1,0.18,0.35)
        legend.SetBorderSize(1)
        legend.SetLineStyle(1)
        legend.SetTextFont(42)
        legend.SetTextSize(0.07)
        legend.SetFillStyle(0)
    else:
        legend=ROOT.TLegend(0.6,0.7,0.95,0.9)
        legend.SetBorderSize(0)
        legend.SetLineStyle(0)
        legend.SetTextFont(42)
        legend.SetTextSize(0.03)
        legend.SetFillStyle(0)
    return legend

def printChannelLabel(pad, channelLabel, ratio = True, wideCanvas = False):
    pad.cd(1)
    l = pad.GetLeftMargin()
    t = pad.GetTopMargin()
    r = pad.GetRightMargin()
    b = pad.GetBottomMargin()

    latex = ROOT.TLatex()
    latex.SetNDC()
    latex.SetTextColor(ROOT.kBlack)
    
    x = 0.
    y = 0.
    if ratio:
        x+= 0.05
        y+= 0.02
    if wideCanvas and ratio:
        x+=-0.06
    latex.DrawLatex(l+0.04+x,1.-t-0.08+y, channelLabel)

def printCMSLabel(pad, privateWork = True, plotLabel = "private work", 
        ratio = True, wideCanvas = False):
    pad.cd(1)
    l = pad.GetLeftMargin()
    t = pad.GetTopMargin()
    r = pad.GetRightMargin()
    b = pad.GetBottomMargin()

    latex = ROOT.TLatex()
    latex.SetNDC()
    latex.SetTextColor(ROOT.kBlack)
    latex.SetTextSize(0.04)

    text = "CMS"
    if privateWork: text += " #bf{#it{"+plotLabel+"}}"
    x = 0.
    y = 0.
    if ratio:
        x+=0.04
        y+=0.03
    if wideCanvas:
        x+=-0.07
    latex.DrawLatex(l+0.06+x,1.-t+0.01+y, text)

def printLumiLabel(pad, lumi, ratio = True, sideLegend = False, wideCanvas = False):
    pad.cd(1)
    l = pad.GetLeftMargin()
    t = pad.GetTopMargin()
    r = pad.GetRightMargin()
    b = pad.GetBottomMargin()

    latex = ROOT.TLatex()
    latex.SetNDC()
    latex.SetTextColor(ROOT.kBlack)
    latex.SetTextSize(0.04)
    text = "#bf{"+str(lumi)+" fb^{-1} (13 TeV)}"
    offset = 0.
    if sideLegend and ratio:
        offset = 0.12
    elif sideLegend and not ratio:
        offset = 0.02
    if wideCanvas:
        offset-= 0.05        
    if ratio: latex.DrawLatex(1.-r-0.15-offset,1.-t+0.04, text)
    else:     latex.DrawLatex(1.-r-0.15-offset,1.-t+0.01, text)

def getHorizontalLine(y, minVal, maxVal, style):
    if y is None: return None
    if minVal is None or maxVal is None: return None
    line = ROOT.TLine(minVal, y, maxVal, y)
    line.SetLineStyle(style)
    return line

def getVerticalLine(x, minVal, maxVal, style):
    if x is None: return None
    if minVal is None or maxVal is None: return None
    line = ROOT.TLine(x, minVal, x, maxVal)
    line.SetLineStyle(style)
    return line

def getLineWithAxisSetup(plotName, nBins, yValue, yMin, yMax, xLabels, yLabel, yErr = 0.):
    line = ROOT.TH1F(
        plotName+"_{}line".format(yValue), 
        plotName+"_{}line".format(yValue),
        nBins, 0., nBins)
    for iBin in range(line.GetNbinsX()+1):
        line.SetBinContent(iBin, yValue)
        line.SetBinError(iBin, yErr)
    line.SetLineWidth(2)
    line.SetLineColor(ROOT.kBlack)
    if yErr > 0.:
        line.SetFillColor(ROOT.kGray)
    line.GetXaxis().SetRangeUser(0., nBins)
    line.GetYaxis().SetRangeUser(yMin, yMax)
    line.SetStats(False)
    for iBin in range(line.GetNbinsX()):
        line.GetXaxis().SetBinLabel(iBin+1, xLabels[iBin])
    line.SetTitle("")
    if line.GetNbinsX() > 8:
        line.LabelsOption("v")
    else:
        line.LabelsOption("h")
    line.GetXaxis().SetLabelSize(line.GetXaxis().GetLabelSize()*1.5)
    line.GetYaxis().SetLabelSize(line.GetYaxis().GetLabelSize()*1.2)

    line.GetYaxis().SetTitle(yLabel)
    return line

def setupHistogram(hist, lw = 2, lc = ROOT.kBlack, fc = None, ls = 1):
    hist.SetLineColor(lc)
    hist.SetLineWidth(lw)
    hist.SetLineStyle(ls)
    if not fc is None:
        hist.SetFillColor(fc)

cldict = {
    1: {
        "68.27%"    : 1,
        "90%"       : 2.71,
        "95%"       : 3.84,
        "95.45%"    : 4,
        "99%"       : 6.63,
        "99.73%"    : 9
    },
    2: {
        "68.27%"    : 2.30,
        "90%"       : 4.61,
        "95%"       : 5.99,
        "95.45%"    : 6.18,
        "99%"       : 9.21,
        "99.73%"    : 11.83
    },
    3: {
        "68.27%"    : 3.53,
        "90%"       : 6.25,
        "95%"       : 7.82,
        "95.45%"    : 8.03,
        "99%"       : 11.34,
        "99.73%"    : 14.16
    },
    4: {
        "68.27%"    : 3.53,
        "90%"       : 6.25,
        "95%"       : 7.82,
        "95.45%"    : 8.03,
        "99%"       : 11.34,
        "99.73%"    : 14.16
    }
}

def getCLvalue(cl, nPOIs):
    if not nPOIs in cldict:
        return None

    cls = cldict[nPOIs]
    if not cl in cls:
        return None

    return cls[cl]


def findCrossing(graph, value, start, stop):
    if not graph or not value: return None

    granularity = 1e-3
    stepsize    = 1e-6
    deltaBest   = 9999

    sign = 1
    if stop < start:
        sign = -1

    xBest = start
    for i in range(int(abs(start-stop)/stepsize)):
        x = start + sign*i*stepsize

        yVal = graph.Eval(x)
        delta = abs(value - yVal)
        if delta < deltaBest:
            deltaBest = delta
            xBest = x

        if deltaBest < granularity:
            return xBest
    
    return None

