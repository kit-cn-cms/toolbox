import os
import glob
import optparse

import toolbox

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

    parser.add_option("-o","--outputdir", dest = "outputdir", default = os.path.dirname(os.path.realpath(__file__))+"/../workdir", metavar = "OUTPUTDIR",
        help = "Path to output directory for log files and submit scripts (relative or absolute). Default=/workdir")
    
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
    jobIDs = toolbox.submitToBatch(workdir, submit_files, opts.memory, str(int(opts.disk)*1000), str(int(opts.runtime)*60), opts.useproxy, opts.vomsproxy, opts.name)
    print("submitted jobs with IDs: {}".format(jobIDs))
    
    # monitor job status
    if opts.monitorStatus:
        toolbox.monitorJobStatus(jobIDs)

    print("done.")

