import sys
import os
import subprocess
import re
import optparse
import time

import pandas as pd

import toolbox

# option parser
parser = optparse.OptionParser(usage="yieldTable [opts] [args=tables]"
    "tables are csv files, multiple calls will be merged into one table")
parser.add_option("-o", dest = "output", 
    help = "output file path")
parser.add_option("--axis", dest = "axis", default = 0,
    help = "table direction 0 or 1")
(opts, args) = parser.parse_args()

if opts.output is None:
    toolbox.printError("need to specifcy output txt file")
    sys.exit()
if len(args) == 0:
    toolbox.printError("need to specify at least one input file")
    sys.exit()

# collect all yield tables
dfs = []
for table in args:
    df = pd.read_csv(table, index_col = [0,1])
    dfs.append(df)

df = pd.concat(dfs)
print(df)
toolbox.yieldTable(df, outputPath = opts.output, axis = int(opts.axis))
