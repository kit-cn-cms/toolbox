

import os
import sys
import optparse
import re
parser = optparse.OptionParser()
parser.add_option("-l","--last",dest="last",default=False,action="store_true",help="show last query")
parser.add_option("-s","--save",dest="save",default=False,action="store_true",help="save query")
parser.add_option("-d","--diff",dest="diff",default=False,action="store_true",help="diff current query to last")
(opts, args) = parser.parse_args()

path = os.path.abspath(os.path.join(os.environ["TOOLBOX"], ".condor_q"))
last_q = os.path.join(path, "last_q")
tmp_q = os.path.join(path, "tmp_q")

class Q:
    def __init__(self, query, parse=False):
        with open(query, "r") as f:
            self.lines = f.readlines()
        with open(f"{query}.up", "r") as f:
            self.priolines = f.readlines()

        if parse:
            self.parse()

    def parse(self):
        self.jobs = {}
        self.ids = {}
        self.subtimes = {}
        header = False
        any_jobs = False
        for l in self.lines:
            if l.startswith("-- Schedd:"):
                split = l.split(" ")
                split = [s for s in split if not s==""]
                self.date = f"{split[-2]} {split[-1].strip()}"
            if l.startswith("OWNER"):
                self.status = l.split("SUBMITTED")[1].split("JOB_IDS")[0].split(" ")
                self.status = [s for s in self.status if not s==""]
                n = len(self.status)
                self._regex = "(\S+)\s+(\S+)\s+(\S+\s+\S+)"
                for i in range(n): self._regex += "\s+(_|\d+)"
                self._regex += "\s+(.*)"
                header = True
                break
        if not header:
            print("ERROR parsing query")
            self.show()
            exit()

        for l in self.lines:
            match = re.match(self._regex, l)
            if not match: continue
            owner = match.group(1)
            batch = match.group(2)
            subtime = match.group(3)
            ID = match.group(4+n)
            stats = {s: match.group(4+i) for i, s in enumerate(self.status)}
            self.jobs[batch] = stats
            self.ids[batch] = ID
            any_jobs = True

        # also get userprio of owner
        self.userprio = None
        self.hours = None
        if any_jobs:
            for l in self.priolines:
                if l.startswith(owner):
                    data = [e for e in l.split(" ") if not e==""]
                    self.userprio = int(float(data[1])/1e3)
                    self.hours = int(float(data[4]))
                    break

    def print(self):
        max_l = max([len(j) for j in self.jobs])
        fmt = "{:"+str(max_l)+"} "
        fmt2 = "{:>5s} "
        # header
        p = fmt.format("BATCH_NAME")
        for s in self.status:
            p += fmt2.format(s)
        length = len(p)
        date = f" Status of: {self.date} "
        header = "-"*5+date+"-"*(length-len(date)-5)
        print(header)
        print(p)
    
        # job lines
        for j in self.jobs:
            stats = self.jobs[j]
            p = fmt.format(j)
            for s in self.status:
                p += fmt2.format(stats[s])
            print(p)

        # userprio line
        if self.userprio and self.hours:
            p = f"\n USERPRIO: {str(self.userprio)}"
            p+= f"\n HOURS:    {str(self.hours)} ({self.hours/24/365.25:.0f} years)"
            p+= f"\n CO2:      {self.hours/72.17:.1f} kg ({self.hours/72.17/850:.1f} flights)"
            print(p)
        print("-"*length)
            
    def diff(self, q2):
        # get all batches
        batches = [j for j in self.jobs]
        for j in q2.jobs:
            if not j in batches: batches.append(j)
        available_stages = list(set(self.status + q2.status))
        stages = ["DONE", "RUN", "IDLE", "HOLD"]
        stages = [s for s in stages if s in available_stages]

        max_l = max([len(b) for b in batches])
        fmt = "{:"+str(max_l)+"} "
        fmt2 = "\033[1;31m{:>5s}\033[0m(\033[1;32m{:>4s}\033[0m) "
        # header
        p = fmt.format("BATCH_NAME")
        for s in stages:
            p += fmt2.format(s,"DIFF")
        length = len(p)-22*len(stages)
        title = f" Diff between \033[1;31m{self.date}\033[0m and \033[1;32m{q2.date}\033[0m "
        header = "-"*10+title+"-"*(length-len(title)-10+22)
        print(header)
        print(p)

        # loop over all batches and print status diff
        for b in batches:
            s1 = {}
            s2 = {}
            if b in self.jobs:
                s1 = self.jobs[b]
            if b in q2.jobs:
                s2 = q2.jobs[b]

            p = fmt.format(b)
            for stage in stages:
                if not stage in s1: 
                    s1[stage] = "_"
                if not stage in s2: 
                    s2[stage] = "_"
                v1 = s1[stage].replace("_","0")
                v2 = s2[stage].replace("_","0")
                d = int(v2) - int(v1)
                if d > 0: d=f"+{d}"
                # for jobs that are finished
                if not "TOTAL" in s2:
                    p += fmt2.format(v1, "DONE")
                # for jobs that are new
                elif not "TOTAL" in s1:
                    p += fmt2.format("NEW", v2)
                # for jobs that are still in progress
                else:
                    p += fmt2.format(v1, str(d))
            print(p)

        # userprio line
        if self.userprio and self.hours and q2.userprio and q2.hours:
            updiff = q2.userprio - self.userprio
            if updiff > 0: updiff = f"+{updiff}"
            hdiff = q2.hours - self.hours
            if hdiff > 0: hdiff = f"+{hdiff}"
            prio = f"\033[1;31m{str(self.userprio)}\033[0m(\033[1;32m{str(updiff)}\033[0m)"
            hour = f"\033[1;31m{str(self.hours)}\033[0m(\033[1;32m{str(hdiff)}\033[0m)"
            p = f"\n USERPRIO: {prio}"
            p+= f"\n HOURS:    {hour}"
            print(p)

        print("-"*length)
               
            
                    
                    
        
    def show(self):
        print("".join(self.lines))
        

def new_query(dest=tmp_q):
    os.system(f"condor_q > {dest}")
    os.system(f"condor_userprio > {dest}.up")

def print_q(x):
    q = Q(x, parse=True)
    q.print()

def last():
    print_q(last_q)

def diff():
    new_query(tmp_q)
    q1 = Q(last_q, parse=True)
    q2 = Q(tmp_q, parse=True)
    q1.diff(q2)

if opts.last:
    last()
elif opts.diff:
    diff()
elif opts.save:
    new_query(last_q)
    print_q(last_q)
else:
    new_query(tmp_q)
    print_q(tmp_q)
