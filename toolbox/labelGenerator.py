import re
__jtRegex = r"((?:ge|le|)[0-9]+j_(?:ge|le|)[0-9]+t)"
__crRegex = r"_with_.*?_CR"
def getLabel(label, splitLine = True, fitName = False):
    if fitName:
        # delete first part
        label = label.split("_")[1:]
        return "\_".join(label)

    jtString = None
    match = re.search(__jtRegex, label)
    if not match is None:
        jtString = match.group(1)
        
    jtLabel = True
    if label.startswith("grouped_"):
        label = label.replace("grouped_","")
    if label.startswith("combined_"):
        label = label.replace("combined_","")
    if label.startswith("fitDiagnostics_bestfit_"):
        label = label.replace("fitDiagnostics_bestfit_","")
    if label.startswith("ljets_") and label.endswith("_hdecay"):
        label = label.replace("ljets_","").replace("_node_hdecay","")
        label = label.split("_")[-1]
        jtLabel = False

    # find CR name
    match = re.search(__crRegex, label)
    if not match is None:
        name, cr = label.split("_with_")
        cr = cr.replace("_CR","")
        label = "\\splitline{"+name+"}{CR: "+cr+"}"
        return label

    if not jtString is None and jtLabel:
        string_parts = jtString.split("_")

        cutstring = ""
        for part in string_parts:
            partstring = ""
            if part.startswith("ge"):
                n = part[2:-1]
                partstring += "\geq "
            elif part.startswith("le"):
                n = part[2:-1]
                partstring += "\leq "
            else:
                n = part[:-1]
                partstring += ""
            partstring += n


            if part.endswith("l"):
                partstring += " lepton"
            elif part.endswith("j"):
                partstring += " jet"
            elif part.endswith("t"):
                partstring += " b-tag"

            # plural
            if int(n)>1: partstring += "s"

            if not part == string_parts[-1]:
                partstring += ", "
            cutstring += partstring

        # splitline
        if "," in cutstring and splitLine:
            cutstring = cutstring.split(",")
            cutstring = "\\splitline{"+cutstring[0]+"}{"+cutstring[1]+"}"
        label = cutstring
    return label
