print("using pq.py")
import awkward as ak
import pickle
import numpy as np
import sys, os

print("call 'help()' to show features")
def help():
    print("usage:")
    print("\tpq [parquet/pickle files]")
    
def load_file(f):
    if f.endswith(".pickle"):
        with open(f, "rb") as pf:
            return pickle.load(pf)
    else:
        return ak.from_parquet(f)

infiles = sys.argv[1:]
files = [
    load_file(f)
    for f in infiles
]
data = files[0]


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
