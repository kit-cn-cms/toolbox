import ROOT
ROOT.gROOT.SetBatch(True)

import pandas as pd

from toolbox import HarryPlotter
from toolbox import printer
  
if __name__ == "__main__":
    import optparse
    parser = optparse.OptionParser()


    dirOpts = optparse.OptionGroup(parser, "File and Directory Options")
    dirOpts.add_option("-i", "--inputfile", dest = "inputFile",
        help = "input file. Type depends on Input Method")
    dirOpts.add_option("-o", "--outfile", dest = "outputFile",
        help = "output pdf file")
    parser.add_option_group(dirOpts)


    keyOpts = optparse.OptionGroup(parser, "Histogram Key Options")
    keyOpts.add_option("-k","--nominalKey", dest = "nominalKey",
        default = "$PROCESS__$CHANNEL__nom",
        help = "key for nominal histograms")
    keyOpts.add_option("-s","--systKey", dest = "systKey",
        default = "$PROCESS__$CHANNEL__$SYSTEMATIC",
        help = "key for systematic histograms")
    keyOpts.add_option("-d","--dataName", dest = "dataName",
        help = "name of data histograms")
    keyOpts.add_option("-c","--channelName", dest = "channelName",
        help = "name of channel to produce plot")
    parser.add_option_group(keyOpts)

    # deploy different information loading methods
    # method A: datacard
    dcLoading = optparse.OptionGroup(parser, "Input Method: Datacard")
    dcLoading.add_option("--loadFromDatacard", dest = "loadFromDatacard",
        default = False, action = "store_true", 
        help = "activate Datacard Input Method")
    parser.add_option_group(dcLoading)

    # method B: systematic file
    sysLoading = optparse.OptionGroup(parser, "Input Method: Systematics File")
    sysLoading.add_option("--loadFromSystematics", dest = "loadFromSystematics",
        default = False, action = "store_true",
        help = "activate Systematics Input Method")
    parser.add_option_group(sysLoading)

    # method C: root file
    rfLoading = optparse.OptionGroup(parser, "Input Method: ROOT File")
    rfLoading.add_option("--loadFromROOTFile", dest = "loadFromROOTFile",
        default = False, action = "store_true",
        help = "activate ROOT File Input Method")
    parser.add_option_group(rfLoading)

    # method D: combineharvester output
    chLoading = optparse.OptionGroup(parser, "Input Method: Combine Harvester Output")
    chLoading.add_option("--loadFromHarvester", dest = "loadFromHarvester",
        default = False, action = "store_true",
        help = "activate Combine Harvester Input Method")
    parser.add_option_group(chLoading)

    # method E: command line options
    optLoading = optparse.OptionGroup(parser, "Input Method: Command Line Options")
    optLoading.add_option("--loadFromOptions", dest = "loadFromOptions",
        default = False, action = "store_true",
        help = "activate Command Line Input Method")
    parser.add_option_group(optLoading)


    # plot customization options
    plotOpts = optparse.OptionGroup(parser, "Plot Customization Options")
    plotOpts.add_option("--statErrorBand", dest = "addStatErrorBand",
        default = False, action = "store_true",
        help = "activate statistical error band")
    parser.add_option_group(plotOpts)

    # load option parser
    (opts, args) = parser.parse_args()
