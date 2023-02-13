print("using rootpy.py")
import ROOT
import sys

print("loading history")
import readline
for i in range(readline.get_current_history_length()):
    print(readline.get_history_item(i + 1))

def setStyle(obj, color = ROOT.kBlack, lw = 2):
    obj.SetLineColor(color)
    obj.SetLineWidth(lw)
    

def getHistInfo(obj, name):
    h = obj.Get(name)
    nbins = h.GetNbinsX()
    low = h.GetBinLowEdge(1)
    hi  = h.GetBinLowEdge(nbins+1)
    print(name, nbins, low, hi)


if sys.argv[-1].startswith("tree="):
    rootfiles = sys.argv[1:-1]
    treeName = sys.argv[-1].split("tree=")[1]
else:
    rootfiles = sys.argv[1:]
    treeName = "Events"

def ropen(rootfile):
    f = ROOT.TFile.Open(rootfile)
    tree = f.Get(treeName)
    return f, tree

def getBranches(t, query=None):
    branches = []
    for b in list(sorted(t.GetListOfBranches())):
        if not query:
            branches.append(b.GetName())
        elif query in b.GetName():
            branches.append(b.GetName())
    return list(sorted(branches))

    
def vars(t, query=None):
    branches = getBranches(t, query)
    for b in branches:
        print(b)

def printEvent(t, query=None):
    cont = True
    idx = 0
    branches = getBranches(t, query)
    while cont:
        t.GetEntry(idx)
        print("=== TESTEVENT ===")
        for b in branches:
            print("{:<60s} = {}".format(b, eval("t."+b)))
        print("=================")
        if "q" in raw_input(" quit loop with q "):
            cont = False
        idx+=1
        
print("call 'help()' to show features")
def help():
    print("usage:")
    print("\trootpy [ntuples] [tree=TREENAME]")
    print("\tlast argument is optional, default TREENAME = MVATree")
    print("-"*50)
    print("functions:")
    print("\tropen(ROOTFILE)    - returns TFile, MVATree")
    print("\tvars(TTree, query) - prints list of branches (if query only print matching branches)")
    

print("="*30)
print("loading events from tree {}".format(treeName))
rfiles = []
trees = []
for rf in rootfiles:
    print("loading {}".format(rf))
    f,t = ropen(rf)
    rfiles.append(f)
    trees.append(t)

f = rfiles[0]
t = trees[0]
print("opened files are accessible via 'rfiles' list")
print("opened trees are accessible via 'trees' list")
print("\tfirst file/tree also accesible via 'f/t'")

c = ROOT.TChain(treeName)
for cf in rootfiles:
    c.Add(cf)
print("\tall files added to chain c")
