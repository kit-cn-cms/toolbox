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
parser.add_option("-r", dest = "requirement", default = None,
    help = "name regex requirement of histograms")

(opts, args) = parser.parse_args()

inputs = []
for f in args:
    if "*" in f:
        inputs += glob.glob(f)
    else:
        inputs += [f]

rootfiles = {}
sums_integrals = {}
sums_entries = {}
sums_bins = {}
for inf in inputs:
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
    toolbox.printDelim("-")

if opts.sums:
    toolbox.printAction("SUMMARY:",1)
    for k in sums_integrals:
        toolbox.printInfo("{}: summed Integral: {}".format(k, sums_integrals[k]))
        if opts.sums:
            toolbox.printPath("\t{}".format(sums_bins[k]))
    for k in sums_entries:
        toolbox.printInfo("{}: summed Entries: {}".format(k, sums_entries[k]))


    
