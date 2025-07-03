import awkward as ak
import pickle
import numpy as np
import sys, os
import pyarrow.parquet as pq

def help():
    print("usage:")
    print("\tpq [parquet/pickle files]")
    
def load_file(f):
    if f.endswith(".pickle"):
        with open(f, "rb") as pf:
            return pickle.load(pf)
    else:
        return ak.from_parquet(f)

def to_np(arr):
    if arr.ndim > 1:
        return ak.flatten(arr).to_numpy()
    else:
        return arr.to_numpy()

def count(arr, ret=False):
    c = np.unique(to_np(arr), return_counts=True)
    if ret:
        return c
    else:
        print("counts:")
        for a, b in zip(c[0].data, c[1]): 
            print(f"{a}: {b}")

def percentiles(arr, percentiles=[0, 5, 10, 25, 50, 75, 90, 95, 100], ret=False):
    x = np.percentile( to_np(arr), percentiles)
    if ret: 
        return x
    else:
        print("percentiles:")
        for a, b in zip(percentiles, x):
            print(f"{a}%: {b}")

def validate(f):
    try:
        if f.endswith(".parquet"):
            data = pq.ParquetFile(f)
        else:
            with open(f, "rb") as pf:
                pickle.load(pf)
            
    except:
        print(f"Broken file {f}")
        return False
    
    return True

if __name__ == "__main__":
    import optparse
    import glob
    parser = optparse.OptionParser()
    parser.add_option("-v", "--validate", dest="validate")
    parser.add_option("--del", dest="delete", action="store_true", default=False)
    parser.add_option("--del-matching", dest="delete_match", action="store_true", default=False)
    (opts, args) = parser.parse_args()
    
    infiles = []
    for f in args:
        if "*" in f:
            infiles += glob.glob(args)
        else:
            infiles.append(f)

    if opts.validate:
        print(f"validating {len(infiles)} pq files...")
        i = 0
        for f in infiles:
            if not validate(f):
                i += 1
                if opts.delete or opts.delete_match:
                    print(f"\t--> Removing file")
                    os.remove(f)
                    if opts.delete_match:
                        f_name = os.path.basename(f)
                        p_name = os.path.dirname(f)
                        f_id = f_name.split("_")[-1].split(".")[0]
                        f_ext = f_name.split(".")[-1]
                        matching_files = glob.glob(os.path.join(p_name, f"*_{f_id}.{f_ext}"))
                        for mf in matching_files:
                            print(f"\talso {mf}")
                            os.remove(f)

        print(f"\n--> {i}/{len(infiles)} broken")
                
        
    else:
        print("using pq.py")
        print("call 'help()' to show features")
        files = [
            load_file(f)
            for f in infiles
        ]
        data = files[0]


