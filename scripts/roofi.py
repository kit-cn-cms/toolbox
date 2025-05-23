import ROOT
import glob
import sys
import os
import re
import numpy as np
import optparse
import toolbox

parser = optparse.OptionParser()
parser.add_option("-I", dest = "integrals", default = False, action = "store_true",
    help = "print histogram integrals")
parser.add_option("-B", dest = "bins", default = False, action = "store_true",
    help = "print histogram bin contents")
parser.add_option("-S", dest = "sums", default = False, action = "store_true",
    help = "sum information over all input files")
parser.add_option("-E", dest = "entries", default = False, action = "store_true",
    help = "print histogram entries")
parser.add_option("-u", dest = "uncertainty", default = False, action = "store_true",
    help = "add uncertainty to integral")
parser.add_option("-r", dest = "requirement", default = None,
    help = "name regex requirement of histograms")

(opts, args) = parser.parse_args()

inputs = []
for f in args:
    if "*" in f:
        inputs += glob.glob(f)
    else:
        inputs += [f]

def proc_is_mc(k):
    p = k.split("__")[1]
    if p=="data_obs": return False
    if p.startswith("Single"): return False
    if p.startswith("EGamma"): return False
    #if p in ["ttjj", "ttcc", "ttbb"]: return False
    if p in ["ttj"]: return False
    return True

rootfiles = {}
sums_integrals = {}
sums_entries = {}
sums_bins = {}
for inf in inputs:
    mc_sum = 0.
    mc_unc_sq = 0.
    data_sum = 0.
    qcd_sum = 0.
    qcd_unc_sq = 0.

    toolbox.printAction("opening {}".format(inf),1)
    rootfiles[inf] = ROOT.TFile.Open(inf)
    keys = [k.GetName() for k in rootfiles[inf].GetListOfKeys()]
    if opts.integrals or opts.entries:
        for k in keys:
            if not opts.requirement is None:
                if not opts.requirement in k:
                    continue
            h = rootfiles[inf].Get(k)
            if opts.integrals:
                integral = h.Integral()
                sumw2 = sum(list(h.GetSumw2()))**0.5

                if proc_is_mc(k):
                    mc_sum += integral
                if "qcd" in k:
                    qcd_sum = integral
                if "data_obs" in k:
                    data_sum = integral

                if opts.uncertainty:
                    toolbox.printInfo("{}: Integral: {:.0f} +- {:.0f}".format(k, integral, sumw2))

                    if proc_is_mc(k):
                        mc_unc_sq += sumw2**2.
                    if "qcd" in k:
                        qcd_unc_sq = sumw2**2.

                else:
                    toolbox.printInfo("{}: Integral: {}".format(k, integral))
                if opts.sums:
                    if not k in sums_integrals:
                        sums_integrals[k] = 0
                        if opts.bins:
                            sums_bins[k] = np.zeros(h.GetNbinsX())
                    sums_integrals[k]+=integral
            if opts.bins:
                binContents = np.array([h.GetBinContent(iBin+1) for iBin in range(h.GetNbinsX())])
                toolbox.printPath("\t{}".format(binContents))
                if opts.bins:
                    sums_bins[k]+=binContents
            if opts.entries:
                entries = h.GetEntries()
                toolbox.printInfo("{}: Entries: {}".format(k, entries))
                if opts.sums:
                    if not k in sums_entries:
                        sums_entries[k] = 0
                    sums_entries[k]+=entries

    if opts.integrals:
        if opts.uncertainty:
            toolbox.printInfo("TotMC: Integral: {:.0f} +- {:.0f}".format(mc_sum, mc_unc_sq**0.5))
            qcd_frac = qcd_sum/mc_sum*100.
            frac_unc = ( (mc_unc_sq/mc_sum**2) + (qcd_unc_sq/qcd_sum**2) )**0.5
            toolbox.printInfo("qcdfrac: Integral: {:.2f} +- {:.2f}".format(qcd_frac, qcd_frac*frac_unc))

            datamc = data_sum  / mc_sum
            unc = ( 1./data_sum + ( mc_unc_sq/mc_sum**2) ) **0.5
            toolbox.printInfo("dataMC: {:.2f} +- {:.4f}".format(datamc, datamc*unc))
            

        else:
            toolbox.printInfo("TotMC: Integral: {:.0f}".format(mc_sum))
    toolbox.printDelim("-")

if opts.sums:
    toolbox.printAction("SUMMARY:",1)
    for k in sums_integrals:
        toolbox.printInfo("{}: summed Integral: {}".format(k, sums_integrals[k]))
        if opts.sums:
            toolbox.printPath("\t{}".format(sums_bins[k]))
    for k in sums_entries:
        toolbox.printInfo("{}: summed Entries: {}".format(k, sums_entries[k]))


    
