import sys
import os
import subprocess
import re
import optparse
import time

import printer


def setup_crab_query_parser(parser):
    parser.add_option("--resubmit", 
        default = False, dest = "do_resubmit", action = "store_true",
        help = "use flag if you want to resubmit failed jobs immediately."
               " automatically increases 'maxjobruntime' or 'maxmemory'"
               " if jobs failed with the corresponding error code."
               " also resubmits publication, but only if no jobs are in failed state.")
    parser.add_option("--add-crab-option", "-a", 
        dest = "additional_options", action = "append", default = [],
        help = "add options to the resubmit calls, for example        "
               " '--maxjobruntime=2750'"
               " allows multiple calls and overwrites automatically"
               " generated options from --resubmit")

    return parser

def printred(cmd):
    return "\033[1;31m{}\033[0m".format(cmd)
def printgreen(cmd):
    return "\033[1;32m{}\033[0m".format(cmd)
def printyellow(cmd):
    return "\033[1;33m{}\033[0m".format(cmd)
def printblue(cmd):
    return "\033[1;34m{}\033[0m".format(cmd)


def printcolor(cmd, groupname):
    cmd = str(cmd)
    # coloring options
    if "failed" in groupname:
        return printred(cmd)
    if "idle" in groupname:
        return printyellow(cmd)
    if "done" in groupname or "finished" in groupname:
        return printgreen(cmd)
    if "running" in groupname:
        return printblue(cmd)
    return cmd


def checkOptions(options, key):
    foundKey = False
    for opt in options:
        if key in opt:
            foundKey = True
    return foundKey

class CrabResult:
    __statusRegex    = r"[a-zA-Z]+ [0-9]+\.[0-9]\% \(\s*[0-9]+/[0-9]+\)"
    __jobNumberRegex = r"\( *([0-9]+)\/ *([0-9]+)\)"
    __errorRegex     = r"[0-9]+ jobs failed with exit code [0-9]+"
    def __init__(self, project_dir):
        self.path = project_dir
        self.name = os.path.basename(self.path)

        if not os.path.exists(self.path):
            printer.printError("project directory {} does not exist".format(self.path))
            sys.exit()

        self.njobs = -1
        self.detected_groups = {}

    def query(self):
        # build crab command
        command = ["crab", "status", self.path]
        
        process = subprocess.Popen(command, 
            stdout = subprocess.PIPE, 
            stderr = subprocess.STDOUT, 
            stdin  = subprocess.PIPE)

        process.stdin.write("\n")
        process.wait()
        self.query = process.communicate()[0]
        if "Enter GRID pass phrase" in self.query:
            printer.printError("need to init voms proxy")
            sys.exit()
        
        self.query = self.query.replace("\t"," ")
        self.query = self.query.replace("\n"," ")
        while "  " in self.query:
            self.query = self.query.replace("  "," ")
            
        return True

    def get_status(self):
        if "Status on the scheduler: COMPLETED" in self.query:
            self.status = "COMPLETED"
            self.status_str = printgreen("COMPLETED")
        elif "Status on the CRAB server: SUBMITTED" in self.query:
            self.status = "SUBMITTED"
            self.status_str = printblue("SUBMITTED")
        else:
            self.status = "FAILED"
            self.status_str = printred("FAILED")
            return False

        return True

    def get_jobstatus(self):
        # look for entries of job status
        # Jobs status: idle 46.9% ( 68/145) running 35.9% ( 52/145) unsubmitted 17.2% ( 25/145)
        jobstatus = self.query.split("Jobs status: ")
        if not len(jobstatus) == 2:
            return False

        jobstatus = jobstatus[1].split("Publication status")[0]
        self.groups = re.findall(self.__statusRegex, jobstatus)
        return True

    def get_pubstatus(self):
        self.pubgroups = []
        pubstatus = self.query.split("Publication status")
        if len(pubstatus) == 2:
            self.pubgroups = re.findall(self.__statusRegex, pubstatus)
        return True

    def collect_groups(self):
        # loop over all groups
        for group in self.groups+self.pubgroups:
            # get name of group
            groupname = group.split(" ")[0]

            # check if it is a pub group
            if not group in self.groups:
                groupname = "pub "+groupname

            # identify tail jobs
            if groupname == "jobs":
                groupname = "tail jobs"

            # identify total job number and done job number
            match = re.search(self.__jobNumberRegex, group)
            if match is None:
                printer.printError("group {} could not be parsed".format(group))
                return False
            finishedjobs = int(match.group(1))
            totaljobs    = int(match.group(2))

            # check if number of total jobs matches with previous groups
            if self.njobs == -1:
                self.njobs = totaljobs
            else:
                if not self.njobs == totaljobs:
                    printer.printError("{}, {}".format(info["njobs"], totaljobs))
                    printer.printError(
                        "ERROR: number of jobs doesnt match for project {}".format(self.name))
                    return False


            # save information of detected groups
            self.detected_groups[groupname] = finishedjobs

        return True

    def resubmit(self, additional_options):

        # check if some jobs failed
        if "failed" in self.detected_groups:
            printer.printBreak(1)
            printer.printDelim("=",30)
            
            # collect error log
            errorlog = self.query.split("Error Summary: ")
            if len(errorlog) == 2:  errorlog = errorlog[1]
            else:                   errorlog = None

            # resubmit options
            resubmit_options = additional_options

            printer.printInfo("found failed jobs: {}".format(
                self.detected_groups["failed"]))

            # search error log for more specific information
            if not errorlog is None:
                # find all errors
                errors = re.findall(self.__errorRegex, errorlog)

                for error in errors:
                    error = error.split(" jobs failed with exit code ")
                    failedjobs = int(error[0])
                    exitcode   = int(error[1])

                    print(printred("\texitcode: {:<7} | {:<5} jobs".format(exitcode, failedjobs)))

                    if exitcode == 50660:
                        printer.printInfo(
                            "\tApplication terminated by wrapper because using too much RAM (RSS)")
                        if not checkOptions(resubmit_options, "maxmemory"):
                            resubmit_options.append("--maxmemory=4000")
                    if exitcode == 50664:
                        printer.printInfo(
                            "\tApplication terminated by wrapper because using too much Wall Clock time")
                        if not checkOptions(resubmit_options, "maxjobruntime"):
                            resubmit_options.append("--maxjobruntime=2750")

            # builindg command for resubmitting
            printer.printAction("building resubmit command...")
            resub_command = ["crab", "resubmit"]+resubmit_options+[self.path]

            # resubmit command
            printer.printCommand(" ".join(resub_command))
            process = subprocess.Popen(resub_command, 
                stdout = subprocess.PIPE, 
                stderr = subprocess.STDOUT, 
                stdin  = subprocess.PIPE)
            process.wait()
            output = process.communicate()[0]

            # resubmit result
            printer.printResult(output)
            printer.printDelim("=",30)
            printer.printBreak(1)

        elif "pub failed" in self.detected_groups:
            printer.printBreak(1)
            printer.printDelim("=",30)
            printer.printInfo("failed publication for some jobs")

            # building command for resubmitting
            printer.printAction("building resubmit command ...")
            resub_command = ["crab", "resubmit", "--publication", self.path]

            printer.printCommand(" ".join(resub_command))
            process = subprocess.Popen(resub_command, 
                stdout = subprocess.PIPE, 
                stderr = subprocess.STDOUT, 
                stdin  = subprocess.PIPE)
            process.wait()
            output = process.communicate()[0]

            # resubmit result
            printer.printResult(output)
            printer.printDelim("=",30)
            printer.printBreak(1)


    def get_status_list(self, groups):
        status = []
        status.append(self.name)
        status.append(self.status_str)
        if self.njobs == -1:
            status.append("-")
        else:
            status.append(self.njobs)

        for entry in groups:
            if entry in self.detected_groups:
                if entry == "finished":
                    n = self.detected_groups[entry]
                    if self.njobs == -1:
                        string = n
                    else:
                        string = "{:<5s} ({:5.1f}%)".format(str(n), 100*float(n)/float(self.njobs))
                    status.append(printcolor(string, entry))
                else:
                    status.append(printcolor(self.detected_groups[entry], entry))
            else:
                status.append(printcolor("", entry))
        return status

    def get_njobs(self, entry):
        if entry == "totaljobs":
            if self.njobs == -1:
                return 0
            else:
                return self.njobs

        if entry in self.detected_groups:
            return self.detected_groups[entry]
        else:
            return 0



# function to collect crab query
def crab_query(project, opts):
    # initialize crab result class
    res = CrabResult(project)

    # perform crab query
    res.query()
    
    # query status and return if failed
    if not res.get_status():
        return res

    if not res.get_jobstatus():
        return res

    # check also for publication status
    res.get_pubstatus()

    # collect status group information
    if not res.collect_groups():
        return res

    # potential immediate resubmit
    if opts.do_resubmit:
        res.resubmit(opts.additional_options)   
    
    return res
    



# print summary table
def print_crab_summary(results):
    allGroups = []
    for res in results:
        allGroups += list(res.detected_groups.keys())
    allGroups = list(set(allGroups))

    # get length of result names
    maxLength = 50
    for res in results:
        if len(res.name) > maxLength:
            maxLength = len(res.name)
    

    # build template
    template = "{:<"+str(maxLength+1)+"} | {:<20} | {:<12} "
    for entry in allGroups:
        if "failed" in entry or "idle" in entry or "done" in entry or "running" in entry:
            template += "| {:<23} "
        elif "finished" in entry:
            template += "| {:<25} "
        else:
            template += "| {:<12} "

    output_lines = []

    # build header
    output_lines.append(template.format("NAME", printyellow("STATUS"), "TOTAL",
        *[printcolor(g,g) for g in allGroups]))

    # loop over results
    for res in results: 
        statusList = res.get_status_list(allGroups)
        output_lines.append(template.format(*statusList))

    # print total summary
    output_lines.append("-"*(maxLength+2)+"|")
    summaryStatus = ["TOTAL", printyellow("")]
    percentStatus = ["", printyellow("")]
    total = -1
    # loop over entries
    for entry in ["totaljobs"]+allGroups:
        totalsum = 0
        # add all results together
        for res in results: 
            totalsum += res.get_njobs(entry)
        summaryStatus.append(printcolor(totalsum,entry))
        
        # calculate percentages
        if entry == "totaljobs":
            percentStatus.append(printcolor("",entry))
            total = totalsum
        else:
            percentage = float(totalsum)/float(total)*100
            percentStatus.append(printcolor("{:.2f} %".format(percentage), entry))
    # add summary line
    output_lines.append(template.format(*summaryStatus))
    output_lines.append(template.format(*percentStatus))

    print("\n".join(output_lines))
