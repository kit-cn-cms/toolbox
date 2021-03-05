import ROOT
import sys
import os
import math 

openedROOTFiles=[]

def checkForROOTFiles(args):
  openedFiles=[]
  if len(args)<=1:
    return []
  for a in args:
    if ".root" in a:
      if os.path.exists(a):
        f=ROOT.TFile(a,"READ")
        if f.IsOpen() and not f.IsZombie() and not f.TestBit(ROOT.TFile.kRecovered):
          openedFiles.append(f)
        else:
          print "Error while opening file", a
  print "Opened following ROOT files in READ-only mode"
  for f in openedFiles:
    print f.GetName()
  print openedFiles
  return openedFiles


thePyArgs=sys.argv

bro=ROOT.TBrowser

openedROOTFiles=checkForROOTFiles(thePyArgs)
if len(openedROOTFiles)>0:
  fh1=openedROOTFiles[0]
  print "The first file has the shorthand fh1"

def getPoissonProb(obs,pred):
  if pred==0:
    print "WARINING zero predicted in poisson function. Setting to 0.00001"
    pred=0.00001
  r=math.exp(-pred)*math.pow(pred,obs)/float(math.factorial(obs))
  return  r

def getNL(val):
  return -math.log(val)

def getLogNormal(theta, kappa, centralValue):
  r=math.exp(-1.0*(math.log(theta/float(centralValue))*math.log(theta/float(centralValue)))/float(2*(math.log(kappa)*math.log(kappa))))/float(math.sqrt(2*3.1415)*math.log(kappa)*theta)
  return r

def subtractQuadratic(val1, val2):
  o=math.sqrt(val1*val1 - val2*val2)
  return o


def addQuadratic(invals=[]):
  o=0.0
  for v in invals:
    o=math.sqrt(o*o + val2*val2)
  return o

def addQuadratic(val1, val2):
  return addQuadratic([val1,val2])

def load_roofitresult(rfile, results = "fit_s"):
  result = rfile.Get(results)
  if not isinstance(result, ROOT.RooFitResult):
    result = rfile.Get("fit_mdf")
    if not isinstance(result, ROOT.RooFitResult):
      return None
  if not (result.status() == 0 and result.covQual() == 3):
    print "Detected problems with fit in %s!" % rfile.GetName()
    print "\tFit Status (should be 0):", result.status()
    print "\tCovariance Matrix Quality (should be 3):", result.covQual()
  return result


def load_variable(result, parname):
  var = result.floatParsFinal().find(parname)
  if isinstance(var, ROOT.RooRealVar):
    return var

def getErrors(var, results = "fit_s"):
  for f in openedROOTFiles:
    result = load_roofitresult(rfile = f, results = results)
    if result:
      v = load_variable(result = result, parname = var)
      if v:
        print f.GetName(), "\t", v.getError()
      else:
        print "could not load %s from %s" % (var, f.GetName())
    else:
      print "could not load fit_s from %s" % f.GetName()

def getAsymErrors(var, results = "fit_s"):
  for f in openedROOTFiles:
    result = load_roofitresult(rfile = f, results = results)
    if result:
      v = load_variable(result = result, parname = var)
      if v:
        print f.GetName(), "\t", v.getErrorHi(), "\t", v.getErrorLo()
      else:
        print "could not load %s from %s" % (var, f.GetName())
    else:
      print "could not load fit_s from %s" % f.GetName()

def getValue(var, results = "fit_s"):
  for f in openedROOTFiles:
    result = load_roofitresult(rfile = f, results = results)
    if result:
      v = load_variable(result = result, parname = var)
      if v:
        print f.GetName(), "\t", v.getVal()
      else:
        print "could not load %s from %s" % (var, f.GetName())
    else:
      print "could not load %s from %s" % (results, f.GetName())
def getCorrelations(var1, var2, results = "fit_s"):
  for f in openedROOTFiles:
    result = load_roofitresult(rfile = f, results = results)
    if result:
      corr = result.correlation(var1, var2)
      print f.GetName(), "\t", corr
    else:
      print "could not load fit_s from %s" % f.GetName() 

def load_model_config(workspace):
    #open workspace to get ModelConfig
    if isinstance(workspace, ROOT.RooWorkspace):
        return workspace.obj("ModelConfig")

def quantile_within_one_sigma(results = "fit_s", skiplist = [], debug = False):
  print "Calculating percentage of variables with pull within one sigma for '%s'" % results
  for f in openedROOTFiles:
    result = load_roofitresult(rfile = f, results = results)
    name = os.path.basename(f.GetName())
    name = name.replace("fitDiagnostics_", "").replace(".root", "")
    if result:
      variables = result.floatParsFinal().contentsString().split(",")
      nvars = 0
      nvars_in_one_sigma = 0
      for var in variables:
        if var in skiplist:
          if debug: print "skipping variable '%s'" % var
          continue
        nvars += 1

        v = load_variable(result = result, parname = var)
        if v:
          if v.getVal() <= 1:
            if debug: print "var: %s\t %s" % (var, str(v.getVal()))
            nvars_in_one_sigma += 1
        else:
          print "could not load %s from %s" % (var, f.GetName())
      quantile = float(nvars_in_one_sigma)/nvars * 100
      print "{0}\t{1}\t({2}/{3})".format(name, quantile, nvars_in_one_sigma, nvars)
    else:
      print "could not load %s from %s" % (results, f.GetName())
