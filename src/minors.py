
from __future__ import print_function

class SpeciesCounter(object):
    def __init__(self):
        self.counts = {}
        
    def count_single(self,species):
        self.counts[species.id] = self.counts.get(species.id,0) + 1
        
    def count(self,species):
        for sp in species:
            self.count_single(sp)
            
def count_species(model):
    counter = SpeciesCounter()
    def count(rxn):
        counter.count(rxn.species)
    model.apply_to_reactions(count)
    return counter.counts

def to_sorted_pairs(counts):
    return sorted([(cnt,sid) for sid,cnt in counts.items()],
                  key=lambda x: x[0],reverse=True)

def display_counts(counts):
    for cnt,sid in to_sorted_pairs(counts):
        print(cnt,sid)
    
def write_met_file(counts,filename="out.mets"):
    with open(filename,'w') as outfile:
        for cnt,sid in to_sorted_pairs(counts):
            print(cnt,sid,sep="\t",file=outfile)

def read_met_file(filename):
    minors = []
    with open(filename) as infile:
        for line in iter(infile):
            _,_,name = line.partition("\t")
            if name[0] == '*':
                minors.append(name.rstrip()[1:])
    return minors