
from __future__ import print_function

class SpeciesCounter(object):
    def __init__(self):
        self.counts = {}
        
    def count_single(self,species):
        self.counts[species.id] = self.counts.get(species.id,0) + 1
        
    def count(self,species):
        for sp in species:
            self.count_single(sp)

    def get_sorted_metcounts(self):
        metcounts = [MetCount(sid,count) for sid,count in self.counts.items()]
        return sorted(metcounts, key=lambda x: x.count, reverse=True)

class MetCount(object):
    def __init__(self,sid,count):
        self.count = count
        self.sid = sid
        self.is_minor = False

    def to_metfile_string(self):
        if self.minor:
            return str(self.count) + "\t*" + self.sid
        else:
            return str(self.count) + "\t" + self.sid

    def to_json_object(self):
        s = '{"name" : "' + self.sid + '", "count" : ' + str(self.count)
        s += ', "minor" : ' + ("true" if self.minor else "false") + '}'
        return s

def count_species(model):
    counter = SpeciesCounter()
    def count(rxn):
        counter.count(rxn.species)
    model.apply_to_reactions(count)
    metcounts = counter.get_sorted_metcounts()

    # set each as minor or major
    frac = model.get_param("MINOR_MET_FRACTION")
    nrxns = float(model.number_of_reactions)
    for m in metcounts:
        m.minor = m.count / nrxns > frac
    return metcounts

def display_counts(metcounts):
    for m in metcounts:
        print(m.to_metfile_string())
    
def write_met_file(metcounts,filename="out.mets",json=False):
    if json:
        with open(filename + ".json",'w') as outfile:
            print('{\n  "minor_counts" : [', file=outfile)
            objs = ['    ' + m.to_json_object() for m in metcounts]
            print(',\n'.join(objs), file=outfile)
            print('  ]\n}\n', file=outfile)
    else:
        with open(filename,'w') as outfile:
            for m in metcounts:
                print(m.to_metfile_string())

def read_met_file(filename):
    minors = []
    with open(filename) as infile:
        for line in iter(infile):
            _,_,name = line.partition("\t")
            if name[0] == '*':
                minors.append(name.rstrip()[1:])
    return minors