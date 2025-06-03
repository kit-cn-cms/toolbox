import subprocess
import optparse
import json
import os

parser = optparse.OptionParser()
parser.add_option("--get-parent", dest="get_parent", action="store_true", default=False)
parser.add_option("--get-files", dest="get_files", action="store_true", default=False)
parser.add_option("--get-meta", dest="get_meta", action="store_true", default=False)
parser.add_option("--get-cmsdb", dest="get_cmsdb", action="store_true", default=False)
parser.add_option("--get-xs", dest="get_xs", action="store_true", default=False)
(opts, args) = parser.parse_args()

def call(cmd, das=True, xsana=False):
    print("=="*20)
    print(cmd)
    subp = subprocess.run(cmd, 
        shell=True, text=True, capture_output=True,
    )
    if das:
        return json.loads(subp.stdout)
    elif xsana:
        return subp.stderr

def get_parent( dataset ):
    cmd = f"dasgoclient -query='parent dataset={dataset}' -json"
    infos = call(cmd)
    return infos[0]["parent"][0]["name"]
    
def get_files( dataset ):
    cmd = f"dasgoclient -query='file dataset={dataset}' -json"
    infos = call(cmd)
    return [ infos[i]["file"][0]["name"] for i in range(len(infos)) ]

def get_xs( dataset, nf=1 ):
    if "NanoAOD" in dataset:
        dataset = get_parent( dataset )
    files = get_files( dataset )
    cmssw = os.environ["CMSSW_BASE"]
    file_str = ",".join( [f"root://xrootd-cms.infn.it///{f}" for f in files[:nf] ] )
    cmd = f"cmsRun {cmssw}/src/ana.py inputFiles='{file_str}' maxEvents=-1"
    out = call(cmd, das=False, xsana=True)

    xs_line = [l for l in out.split("\n") if "After filter: final cross section" in l][0]
    print("-->")
    print(xs_line)
    xs_val = float(xs_line.split(" = ")[1].split(" +- ")[0])
    xs_unit = xs_line.split(" ")[-1]

    return xs_val, xs_unit

def get_meta( dataset ):
    # first get datasset info and id
    cmd = f"dasgoclient -query='dataset={dataset}' -json"
    infos = call(cmd)
    
    dataset_id = infos[0]["dataset"][0].get("dataset_id", -1)
    dataset_name = infos[0]["dataset"][0]["name"]
    dataset_era = infos[0]["dataset"][0].get("acquisition_era_name", " ")[-1]
    is_data = infos[0]["dataset"][0].get("datatype", "") == "data"
    era_aux = ""
    procs = ""
    if is_data: 
        era_aux = {"era": dataset_era}
        procs = "procs.data"


    # then get number of files
    cmd = f"dasgoclient -query='summary dataset={dataset}' -json"
    infos = call(cmd)

    nfiles = infos[0]["summary"][0]["nfiles"]
    nevents = infos[0]["summary"][0]["nevents"]

    return {"id": dataset_id, "name": dataset_name, "nfiles": nfiles, "nevents": nevents, "is_data": is_data, "aux": era_aux, "procs": procs}
    
    
def format_cmsdb( dataset ):
    template = """
cpn.add_dataset(
    name="",
    id={id},
    is_data={is_data},
    processes=[{procs}],
    keys=[
        "{name}",
    ],
    n_files={nfiles},
    n_events={nevents},
    aux={aux}
)
"""
    return template.format( **get_meta(dataset) )

    
    
# loop over all arguments
out_dict = {}
for das_string in args:
    wildcard = "*" in das_string
    datasets = []
    if not wildcard:
        # keep consisting structure
        datasets.append(das_string)
    else:
        # using a wildcard leads to a different structer in json format
        cmd = f"dasgoclient -query='dataset={das_string}' -json"
        print("Resolving wildcard...")
        infos = call(cmd)
        for info in infos:
            dataset_name = info.get("dataset", [])[0].get("name", "")
            datasets.append(dataset_name)

        print(f"\n... found {len(datasets)} datasets matching the wildcards")

    for dataset in datasets:
        print("__"*30)
        print("\nAccessing single dataset")
        print(dataset)
        if opts.get_files:
            ret = get_files(dataset)
        elif opts.get_parent:
            ret = get_parent(dataset)
        elif opts.get_xs:
            ret = get_xs(dataset)
        elif opts.get_meta:
            ret = get_meta(dataset)
        elif opts.get_cmsdb:
            ret = format_cmsdb(dataset)
        else:
            # call dasgoclient command
            cmd = f"dasgoclient -query='dataset={dataset}' -json"
            ret = call(cmd)

        out_dict[dataset] = ret

print("\n\nSummary:\n")
for key in out_dict:
    print(key, out_dict[key])

        
