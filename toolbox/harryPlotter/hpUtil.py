import ROOT
from toolbox import printer




colorDict = {
    "ttZ":          ROOT.kCyan,
    "ttH":          ROOT.kBlue+1,
    "ttlf":         ROOT.kRed-7,
    "ttcc":         ROOT.kRed+1,
    "ttbb":         ROOT.kRed+3,
    "tt2b":         ROOT.kRed+2,
    "ttb":          ROOT.kRed-2,
    "tthf":         ROOT.kRed-3,
    "ttbar":        ROOT.kOrange,
    "ttmergedb":    ROOT.kRed-1,

    "sig":          601,
    "total_signal": 601,
    "bkg":          ROOT.kOrange,

    "defaultColor": 0
    }

def getHistColor(name):
    # edit some names for color dict
    if "ttH"  in name: name = "ttH"
    if "ttZ"  in name: name = "ttZ"
    if "ttbb" in name: name = "ttbb"

    # return color
    if name in colorDict:
        return colorDict[name]
    else:
        # increase color id for processes that are not defined
        colorDict["defaultColor"]+=1
        return colorDict["defaultColor"]


errorbandStyles = {
    "stat":         (1001, ROOT.kGray,     0.4),
    "syst":         (1001, ROOT.kBlack,    0.4),
    "experimental": (1001, ROOT.kRed,      0.3),
    "theo":         (1001, ROOT.kBlue,     0.3),

    "btag":         (3145, ROOT.kRed-4,    0.7),
    "jec":          (3145, ROOT.kOrange+1, 1.0),
    "jes":          (3145, ROOT.kOrange+3, 1.0),
    "jer":          (3145, ROOT.kOrange+5, 1.0),
    "uncl":         (3145, ROOT.kOrange+7, 1.0),
    "scale":        (3472, ROOT.kBlue+1,   1.0),
    "ps":           (3227, ROOT.kBlue+3,   1.0),
    "lindert":      (3227, ROOT.kBlue+5,   1.0),
    "pu":           (3244, ROOT.kMagenta,  1.0),
    "lep":          (3257, ROOT.kRed+1,    1.0),
    "ele":          (3257, ROOT.kRed+3,    1.0), 
    "muon":         (3257, ROOT.kRed+4,    1.0),
    "pho":          (3257, ROOT.kRed+2,    1.0),
    "topPt":        (3257, ROOT.kRed+6,    1.0),
    "toptagger":    (3257, ROOT.kGreen,    1.0),
   }

def getErrorStyle(sys):
    if sys in errorbandStyles:
        return errorbandStyles[sys]
    else:
        return errorbandStyles["syst"]



def moveOverflow(h):
    nBins = h.GetNbinsX()
    # underflow
    h.SetBinContent(1, h.GetBinContent(0)+h.GetBinContent(1))
    # overflow
    h.SetBinContent(nBins, h.GetBinContent(nBins+1))

    # underflow error
    h.SetBinError(1, ROOT.TMath.Sqrt(
        ROOT.TMath.Power(h.GetBinError(0),2) + ROOT.TMath.Power(h.GetBinError(1),2)))
    # overflow error
    h.SetBinError(nBins, ROOT.TMath.Sqrt(
        ROOT.TMath.Power(h.GetBinError(nBins),2) + ROOT.TMath.Power(h.GetBinError(nBins+1),2)))

    # delete underflow
    h.SetBinContent(0, 0)
    h.SetBinError(0, 0)

    # delete overflow
    h.SetBinContent(nBins+1, 0)
    h.SetBinError(nBins+1, 0)


def divideByBinWidth(h):
    for iBin in range(h.GetNbinsX()):
        width = h.GetXaxis().GetBinUpEdge(iBin+1) - h.GetXaxis().GetBinLowEdge(iBin+1)
        h.SetBinContent(iBin+1, h.GetBinContent(iBin+1)/width)
        h.SetBinError(iBin+1, h.GetBinError(iBin+1)/width)
        
