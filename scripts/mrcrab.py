import sys
import os
import subprocess
import re
import optparse
import time

import toolbox

# option parser
parser = optparse.OptionParser(usage="mrcrab [opts] [args=projects]")
parser = toolbox.setup_crab_query_parser(parser)
(opts, args) = parser.parse_args()

# collect all crab porjects
projects = []
for p in args:
    if "*" in p:
        projects += glob.glob(p)
    else:
        projects += [p]

toolbox.printInfo("checking jobs:")
for p in projects: toolbox.printPath("\t"+p) 
toolbox.printDelim("=",30)

results = []
for project in projects:
    toolbox.printAction("querying job {}".format(project))
    
    result = toolbox.crab_query(project, opts)
    results.append(result)

toolbox.print_crab_summary(results)
