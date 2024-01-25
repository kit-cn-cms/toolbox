import sys
import os
import glob
import numpy as np
import subprocess 
import stat
import re
import time
import optparse
import sys

import toolbox.printer as printer

submitTemplateNAF = """
universe = vanilla
executable = /bin/zsh
arguments = {arg}
error  = {dir}/{name}submitScript.$(Cluster)_$(ProcId).err
log    = {dir}/{name}submitScript.$(Cluster)_$(ProcId).log
output = {dir}/{name}submitScript.$(Cluster)_$(ProcId).out
run_as_owner = true
Requirements = ( OpSysAndVer == "CentOS7" )
RequestMemory = {memory}
RequestDisk = {disk}
+RequestRuntime = {runtime}
Request_Cpus = {ncores}
JobBatchName = {batchname}
"""

submitTemplateETP = """
universe = docker
executable = /bin/zsh
arguments = {arg}
error  = {dir}/{name}submitScript.$(Cluster)_$(ProcId).err
log    = {dir}/{name}submitScript.$(Cluster)_$(ProcId).log
output = {dir}/{name}submitScript.$(Cluster)_$(ProcId).out
run_as_owner = true
Requirements = ( OpSysAndVer == "CentOS7" )
RequestMemory = {memory}
RequestDisk = {disk}
+RequestWalltime = {runtime}
JobBatchName = {batchname}
accounting_group=cms.higgs
requirements = TARGET.ProvidesIO && TARGET.ProvidesEKPResources
docker_image = mschnepf/slc7-condocker
"""

def submitToBatch(workdir, list_of_shells, memory_ = "1000", disk_ = "1000000", runtime_ = "43200", ncores_ = "1", use_proxy = False, proxy_dir_ = "", name_ = ""):
    ''' submit the list of shell script to the NAF batch system '''

    # write array script for submission
    arrayScript = writeArrayScript(workdir, list_of_shells, name_)

    # write submit script for submission
    submitScript = writeSubmitScript(workdir, arrayScript, len(list_of_shells), memory_, disk_, runtime_, ncores_, use_proxy, proxy_dir_, name_)
        
    # submit the whole thing
    jobID = condorSubmit( submitScript)
    return [jobID]

def writeArrayScript(workdir, files, name_):
    path = os.path.abspath(workdir+"/"+name_+"_arraySubmit.sh")
    files = [os.path.abspath(f) for f in files]
    
    code = """
#!/bin/bash
subtasklist=(
%(tasks)s
)
thescript=${subtasklist[$SGE_TASK_ID]}
echo "starting dir: $PWD"
echo "${thescript}"
echo "$SGE_TASK_ID"
. $thescript
    """ % ({"tasks":"\n".join(files)})

    with open(path, "w") as f:
        f.write(code)

    st = os.stat(path)
    os.chmod(path, st.st_mode | stat.S_IEXEC)
    
    #print("wrote array script "+str(path))
    return path


def writeSubmitScript(workdir, arrayScript, nScripts, memory_, disk_, runtime_, ncores_, use_proxy, proxy_dir_, name_):
    path = workdir+"/"+name_+"_submitScript.sub"
    logdir = workdir+"/logs"
    if not os.path.exists(logdir):
        os.makedirs(logdir)

    code = ""
    if "naf" in os.environ["HOSTNAME"]:
        code += submitTemplateNAF
    else:
        code += submitTemplateETP

    code = code.format(
        arg = os.path.abspath(arrayScript),
        dir = os.path.abspath(logdir),
        memory = memory_,
        disk = disk_,
        runtime = runtime_,
        name = name_,
        ncores = ncores_,
        batchname = name_.replace(".txt",""))

    if use_proxy:
        code+="""
environment = X509_USER_PROXY={proxy_dir}
getenv = True
use_x509userproxy = True
x509userproxy = {proxy_dir}""".format(proxy_dir = proxy_dir_)

    code+="""
Queue Environment From (
"""
    for taskID in range(nScripts):
        code += "\"SGE_TASK_ID="+str(taskID+1)+"\"\n"
    code += ")"

    with open(path, "w") as f:
        f.write(code)

    #print("wrote submit script "+str(path))
    return path

def condorSubmit(submitPath):
    submitCommand = "condor_submit -terse "+ submitPath
    printer.printCommand("submitting {}".format(submitCommand))
    tries = 0
    jobID = None
    while not jobID:
        process = subprocess.Popen(submitCommand.split(), stdout = subprocess.PIPE, stderr = subprocess.STDOUT, stdin = subprocess.PIPE)
        process.wait()
        output = process.communicate()
        print(output)
        try:
            jobID = int(output[0].decode().split(".")[0])
        except:
            print("something went wrong with calling the condir_submit command, submission of jobs was not successful")
            print("DEBUG:")
            print(output)
            tries += 1
            jobID = None
            time.sleep(60)
        if tries>10:
            print("job submission was not successful after ten tries - exiting without JOBID")
            sys.exit(-1)
    return jobID




def monitorJobStatus(jobIDs = None, queryInterval = 60, nTotalJobs = None):
    ''' 
        monitoring of jobs via condor_q function. 
        Loops condor_q output until all scripts have been terminated

        jobIDs: list of IDs of jobs to be monitored 
            (if no argument is given, all jobs of the current NAF user are monitored)
    
    no return 
    '''

    allfinished=False
    errorcount = 0
    printer.printAction( "checking job status in condor_q ...",1)
    command = ["condor_q"]
    # adding jobIDs to command
    if jobIDs:
        command += jobIDs
        command = [str(c) for c in command]
    command += ["-totals"]#, "|", "grep", "'Total for query'"]
    sTime = time.time()

    # counts
    times = []
    runs = []
    idles = []
    helds = []
    totals = []
    while not allfinished:
        time.sleep(queryInterval)
        # calling condor_q command
        a = subprocess.Popen(command, 
            stdout=subprocess.PIPE,stderr=subprocess.STDOUT,stdin=subprocess.PIPE)
        a.wait()
        qstat = a.communicate()[0]
        nrunning = 0
        querylines = [line for line in qstat.decode().split("\n") if "Total for query" in line]

        # check if query matches
        if len(querylines) == 0:
            errorcount += 1
            # sometimes condor_q is not reachable - if this happens a lot something is probably wrong
            printer.printWarning("line does not match query")
            if errorcount == 30:
                printer.printWarning(
                    "something is off - condor_q has not worked for {} minutes ...".format(
                        int(30*queryInterval/60)))
                time.sleep(120)
            if errorcount == 60:
                printer.printError("this does not work anymore - removing jobs")
                command[0] = "condor_rm"
                printer.printCommand(command)
                a = subprocess.Popen(command, 
                    stdout = subprocess.PIPE, stderr = subprocess.STDOUT, stdin = subprocess.PIPE)
                return
            continue

        errorcount = 0
        # sum all jobs that are still idle or running
        jobsRunning = 0
        jobsIdle        = 0
        jobsHeld        = 0
        for line in querylines:
            jobsRunning += int(re.findall(r'\ [0-9]+\ running', line)[0][1:-8])
            jobsIdle += int(re.findall(r'\ [0-9]+\ idle', line)[0][1:-5])
            jobsHeld += int(re.findall(r'\ [0-9]+\ held', line)[0][1:-5])

        nrunning += jobsRunning + jobsIdle + jobsHeld
        printLine = "\033[1;32m{:4d} running\033[0m | \033[1;33m{:4d} idling\033[0m | "
        printLine+= "\033[1;31m{:4d} held\033[0m |\t \033[1;34mtotal: {:4d}\033[0m"
        printLine = printLine.format(
                        jobsRunning, jobsIdle, jobsHeld, nrunning)
        if not nTotalJobs is None:
            printLine+= "/\033[1;34m{}\033[0m".format(nTotalJobs)
        print(printLine)

        if nrunning == 0:
            printer.printAction("waiting on no more jobs - exiting loop")
            allfinished=True

    printer.printInfo("all jobs are finished - exiting monitorJobStatus")
    return



if __name__ == "__main__":
    parser = optparse.OptionParser(usage="%prog [options] files")
    parser.add_option("-f","--folder", dest = "folder", default = None, metavar = "FOLDER",
        help = "Specify relative path to a folder from which all files are to be submitted.")

    parser.add_option("--file", dest = "file", default = None, metavar = "FILE",
        help = "Specify a .txt. file containing the paths to scripts.")
    
    parser.add_option("-p","--pattern", dest = "pattern", default = None, metavar = "'PATTERN'",
        help = "Specify a pattern to match files in FOLDER, e.g. '_test'.")

    parser.add_option("-m","--monitorStatus", action = "store_true", dest = "monitorStatus", default = False, metavar = "MONITORSTATUS",
        help = "Monitor the job status after submission with 'condor_q' until all jobs are done.")

    parser.add_option("-o","--outputdir", dest = "outputdir", 
        default = os.path.dirname(os.path.realpath(__file__))+"/../workdir", metavar = "OUTPUTDIR",
        help = "Path to output directory for log files and submit scripts (relative or absolute)."
               " Default=/workdir")
    
    parser.add_option("-M","--memory",type="string",default="2000",dest="memory",metavar = "MEMORY",
        help = "Amount of memory in MB which is requested for the machines")
    
    parser.add_option("-d","--disk",type="string",default="2000",dest="disk",metavar = "DISK",
        help = "Amount of disk space in MB which is requested for the machines")
    
    parser.add_option("-r","--runtime",type="string",default="1440",dest="runtime",metavar = "RUNTIME",
        help = "Amount of runtime in minutes which is requested for the machines")
    
    parser.add_option("-u","--useproxy",action="store_true",default=False,dest="useproxy",metavar = "USEPROXY",
        help = "Use voms proxy")
    
    parser.add_option("-v","--vomsproxy",type="string",default="",dest="vomsproxy",metavar = "VOMSPROXY",
        help = "Path to the VOMS proxy file")
    
    parser.add_option("-n","--name",type="string",default="",dest="name",metavar = "NAME",
        help = "Name for this submit job")

    (opts, args) = parser.parse_args()

    if opts.useproxy and not opts.vomsproxy:
        parser.error('If flag to use proxy is set, a path to the proxy file has to be provided')
    
    # get files to submit
    if opts.folder:
        filepath = opts.folder+"/*.sh"
        submit_files = glob.glob(filepath)
    elif opts.file:
        with open(opts.file) as f:
            files = list(f)
            submit_files = [f.replace("\n","") for f in files]
    else:
        submit_files = [f for f in args if f.endswith(".sh")]


    # check for naming pattern
    if opts.pattern:
        print(opts.pattern)
        submit_files = [f for f in submit_files if opts.pattern in f]

    # print list of files to submit
    print("-"*40)
    print("number of files to submit: {}".format(len(submit_files)))
    for f in submit_files: print("    {}".format(f))
    print("-"*40)

    opts.name = opts.name.replace(".txt","")
    # setup workdir
    workdir = opts.outputdir+"/"+opts.name
    if not os.path.exists(workdir):
        os.makedirs(workdir)
    print("output directory for logfiles, etc: {}".format(workdir))


    # submit to batch
    jobIDs = submitToBatch(workdir, submit_files, opts.memory, str(int(opts.disk)*1000), str(int(opts.runtime)*60), opts.useproxy, opts.vomsproxy, opts.name)
    print("submitted jobs with IDs: {}".format(jobIDs))
    
    # monitor job status
    if opts.monitorStatus:
        monitorJobStatus(jobIDs)

    print("done.")

