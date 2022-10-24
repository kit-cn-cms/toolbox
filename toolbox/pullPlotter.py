import ROOT
ROOT.gStyle.SetEndErrorSize(3.)
ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch(True)
import os
import numpy as np
import re

import toolbox

class Fit:
    def loadFile(self, path, opts):
        if not os.path.exists(path):    
            toolbox.printError("\troot file does not exist - skipping")
            toolbox.printError("\t{}".format(path))
            return

        # open file and get fits
        self.rfile = ROOT.TFile(path)
        if not opts.include_sb: 
            self.fit_s = None
        else:
            self.fit_s = self.rfile.Get("fit_s")
        self.fit_b = self.rfile.Get("fit_b")
        if not hasattr(self.fit_b, "floatParsFinal") or not opts.include_bonly:
            self.fit_b = None
        self.modes = []
        if not self.fit_s is None:
            self.modes.append("s")
        if not self.fit_b is None:
            self.modes.append("b")
        print(self.modes)
        print(self.fit_s)
        print(self.fit_b)


        self.parameters = {}
        self.nuisances = {}
        self.poiSet   = {}
        self.poiNames = {}
        self.size = {}

        # get fitted parameters
        if not self.fit_s is None:
            if self.is_good_fit(self.fit_s, opts, "s+b"):
                self.parameters["s"] = self.fit_s.floatParsFinal()
            else:
                toolbox.printWarning("WARNING: fit status is not good for s+b fit")
        if not self.fit_b is None:
            if self.is_good_fit(self.fit_b, opts, "b"):
                self.parameters["b"] = self.fit_b.floatParsFinal()
            # else:
                # toolbox.printWarning("WARNING: fit status is not good for b-only fit")

        self.getNuisances(opts)

    def is_good_fit(self, result, opts, fit):
        # print(result)
        if result.status() == 0 and result.covQual() == 3:
            return True
        toolbox.printWarning("WARNING: This is not a good {} fit!".format(fit))
        toolbox.printWarning("\tStatus: {0}\tQuality: {1}".format(result.status(), result.covQual()))
        if not opts.check_fit_status:
            toolbox.printWarning("skipping fit status is active, will ignore warning")
        return not opts.check_fit_status #DANGERZONE!


    def getNuisances(self, opts):
        for mode in self.modes:
            self.nuisances[mode] = []
            self.poiSet[mode] = ROOT.RooArgList(mode)
            self.poiNames[mode] = []
            for i in range(self.parameters[mode].getSize()):
                nuis = self.parameters[mode].at(i)
                name = nuis.GetName()

                if opts.exclude_mcstat:
                    if "prop_bin" in name or "rate_bin" in name:
                        continue
                if not opts.unblind and (name == "r" or name.startswith("r_")):
                    continue
                if not opts.exclude is None:
                    # exclude nuisances matching the regex
                    # print("---")
                    # print(opts.exclude)
                    # print(name)
                    # print(re.match(opts.exclude, name))
                    # print(re.search(opts.exclude, name))
                    if not re.search(opts.exclude, name) is None: continue
                if not opts.include_only is None:
                    if re.match(opts.include_only, name) is None: continue

                self.nuisances[mode].append(name)
                # match POIs
                if name == "r" or name.startswith("r_"):
                    self.poiSet[mode].add(nuis)
                    self.poiNames[mode].append(name)

            self.nuisances[mode] = sorted(list(self.nuisances[mode]))
            self.size[mode] = len(self.nuisances[mode])
    
    def getValue(self, nuis, mode = "s"):
        try:
            value = self.parameters[mode].find(nuis).getVal()
        except:
            toolbox.printError("\tparameter {} not in diagnostics file".format(nuis))
            value = 0.
        return value
    
    def close(self):
        self.rfile.Close()
        del self.rfile


class Pulls(Fit):
    def __init__(self, path, opts):
        toolbox.printInfo("loading pulls from {}".format(path))
        self.loadFile(path, opts)
        self.loadPulls()

    def loadPulls(self):
        pulls = {}
        pulls["s"] = {}
        pulls["b"] = {}

        # loop over all nuisances
        for mode in self.modes:
            for param in self.nuisances[mode]:
                nuis = self.parameters[mode].find(param)
                pulls[mode][param] = Pull(nuis)

        self.results = pulls

class Pull:
    def __init__(self, nuis):
        self.name = nuis.GetName()
        self.mu   = float(nuis.getVal())
        self.up   = float(nuis.getErrorHi())
        self.down = abs(float(nuis.getErrorLo()))

    @classmethod
    def empty(cls, name):
        self.name = name
        self.mu   = 0.
        self.up   = 0.
        self.down = 0.
        
