
import pickle

def score_average_value(rule,genes,values):
    if not genes:
        return None
    else:
        return sum(values.values()) / float(len(genes))

class Gpr(object):
    def __init__(self,rxns):
        self.rules = {}
        self.gene_sets = {}
        self.genes = set()

        for name,rxn in rxns.items():
            self.rules[name] = rxn.gpr
            self.gene_sets[name] = rxn.genes
            self.genes.update(rxn.genes)

    def score_reaction(self,rxn_name,values,scorer=score_average_value):
        genes = self.gene_sets[rxn_name]
        values = {k: v for k,v in values.items() if k in genes}
        return scorer(self.rules[rxn_name],genes,values)

    def score_reactions(self,values,scorer=score_average_value):
        score = lambda r: self.score_reaction(r,values,scorer=scorer)
        scores = {r: score(r) for r in self.rules.keys()}
        return {r: score for r,score in scores.items() if score is not None}


def write_gpr_file(gpr,filename):
    f = open(filename,'w')
    pickle.dump(gpr,f)
    f.close()

def read_gpr_file(filename):
    f = open(filename)
    gpr = pickle.load(f)
    f.close()
    return gpr



