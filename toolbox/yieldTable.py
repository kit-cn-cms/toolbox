import pandas as pd
import toolbox.printer as printer

def yieldTable(df, outputPath, axis = 0):
    """
    generate a yield table from a dataframe

    dataframe structure:
                    data    dataMC  soverb  srootb  proc1   proc2   ...
    feature
    A       isSig                                   True    False   ...
            ratio           1.23    0.123   1.23        
            unc                                     0.123   0.234   ...
            yield   123                             12.3    1.23    ...
    B       isSig   
            ratio
            unc
            yield
    ...
    """

    # columns 
    columns = df.columns.values

    # processes as ratios
    isRatio = df[df.index.get_level_values(1) == "isSig"].iloc[0].isna()
    isSig   = df[df.index.get_level_values(1) == "isSig"].iloc[0] == 1
    isBkg   = df[df.index.get_level_values(1) == "isSig"].iloc[0] == 0
    
    ratios     = df[df.columns[isRatio]]
    ratioNames = ratios.columns.values

    sigs       = df[df.columns[isSig]]
    sigProcs   = list(sorted(sigs.columns.values))

    bkgs       = df[df.columns[isBkg]]
    bkgProcs   = list(sorted(bkgs.columns.values))

    # features
    features = list(sorted(set(df.index.get_level_values(0))))

    yieldTemplate  = "${:12.3f} \\pm {:10.3f}$"
    valueTemplate  = "${:12.3f}$               "
    stringTemplate = "{:<59}"
    headTemplate   = "{:<29}"
    midrule        = "\\midrule"
    # build table with axis == 0:
    if axis == 0:
        tableString = ["\\begin{tabular}{l|"+"l"*len(features)+"}"]

        # header
        header = stringTemplate.format("")
        for f in features:
            header+=" & "+headTemplate.format(translateFeature(f))
        header+= " \\\\"
        tableString.append(header)
        tableString.append(midrule)

        # data
        if "data" in ratioNames:
            line = stringTemplate.format("Data")
            for f in features:
                line+=" & "+valueTemplate.format(ratios["data"].loc[f, "yield"])
            line+= " \\\\"
            tableString.append(line)
            tableString.append(midrule)

        # signal yields
        for s in sigProcs:
            line = stringTemplate.format(translateProc(s))
            for f in features:
                line+=" & "+yieldTemplate.format(
                    sigs[s].loc[f, "yield"], sigs[s].loc[f, "unc"])
            line+= " \\\\"
            tableString.append(line)
        tableString.append(midrule)

        # background yields
        for b in bkgProcs:
            line = stringTemplate.format(translateProc(b))
            for f in features:
                line+=" & "+yieldTemplate.format(
                    bkgs[b].loc[f, "yield"], bkgs[b].loc[f, "unc"])
            line+= " \\\\"
            tableString.append(line)
        tableString.append(midrule)
        
        # dataMC
        if "dataMC" in ratioNames:
            line = stringTemplate.format("Data/MC")
            for f in features:
                line+=" & "+valueTemplate.format(ratios["dataMC"].loc[f, "ratio"])
            line+= " \\\\"
            tableString.append(line)
            tableString.append(midrule)

        # SB
        if "soverb" in ratioNames:
            line = stringTemplate.format("$S/B$")
            for f in features:
                line+=" & "+valueTemplate.format(ratios["soverb"].loc[f, "ratio"])
            line+= " \\\\"
            tableString.append(line)

        if "soversb" in ratioNames:
            line = stringTemplate.format("$S/(S+B)$")
            for f in features:
                line+=" & "+valueTemplate.format(ratios["soversb"].loc[f, "ratio"])
            line+= " \\\\"
            tableString.append(line)

        if "srootb" in ratioNames:
            line = stringTemplate.format("$S/\\sqrt{B}$")
            for f in features:
                line+=" & "+valueTemplate.format(ratios["srootb"].loc[f, "ratio"])
            line+= " \\\\"
            tableString.append(line)
                
        tableString.append("\\end{tabular}")

    with open(outputPath, "w") as f:
        f.write("\n".join(tableString))
    printer.printPath("wrote yield table to {}".format(outputPath))

def translateProc(p):
    fmap = {
        "vjets": "V+jets",
        "wjets": "W+jets",
        "zjets": "Z+jets",
        "singlet": "single top",
        }
    if p in fmap:
        return fmap[p]

    p = p.replace("tt", "$t\\bar{t}$+")
    if p.endswith("+"): p = p[:-1]
    p = p.replace("bb", "$b\\bar{b}$")
    p = p.replace("cc", "$c\\bar{c}$")
    if "unfold" in p:
        p = p.replace("_unfold_", " (")
        p+=")"
        p = p.replace("mindR", "$min\\Delta R$")
    
    return p.replace("_"," ")
    

def translateFeature(f):
    f = f.replace("_"," ")
    return f


