
from warnings import warn
import re, copy

from model import Species, Reaction

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

def tagmatch(elem,tag):
    return elem.tag.endswith('}' + tag)

def findfirst(elem,tag):
    for e in elem.getiterator():
        if tagmatch(e,tag):
            return e

def findall(elem,tag):
    return [e for e in elem.getiterator() if tagmatch(e,tag)]

def parse_sbml_file(file, subsystem_pattern='SUBSYSTEM: *(?P<value>.*\S+.*) *\</',
                    gpr_pattern='GENE_ASSOCIATION: *(?P<value>.*\S+.*) *\</',
                    gene_split_pattern=' or | and |[() ]'):
    # returns a dict:
    #   species:  { 'id' : Species(...) }
    #   reactions:  { 'id' : Reaction(...) }
    #   compartments { 'id' : ('name','outside') }

    tree = ET.ElementTree(file=file)
    model = tree.getroot()[0]
    
    listOfCompartments = findfirst(model,'listOfCompartments')
    listOfSpecies = findfirst(model,'listOfSpecies')
    listOfReactions = findfirst(model,'listOfReactions')
    
    compartments = {}
    for elem in findall(listOfCompartments,'compartment'):
        compartments[elem.get('id')] = (elem.get('name'),elem.get('outside'))
    
    def parse_species(sp):
        return Species(sp.get('id'),
                       name=sp.get('name'),
                       compartment=sp.get('compartment'))
    
    species = {}
    for sp in findall(listOfSpecies,'species'):
        parsed = parse_species(sp)
        species[parsed.id] = parsed
    
    def parse_reaction(rxn):
        rid = rxn.get('id')
        name = rxn.get('name')
        reversible = rxn.get('reversible') == "true"
        
        reactants = findfirst(rxn,'listOfReactants')
        products = findfirst(rxn,'listOfProducts')
        def parse_speciesrefs(listof):
            parsed = [ref.get('species')
                      for ref in findall(listof,'speciesReference')]
            if parsed:
                final = []
                for x in parsed:
                    if x not in species:
                        warning = 'Reaction {0} species {1} not found.'
                        warn(warning.format(rid,x))
                    else:
                        final.append(copy.deepcopy(species[x]))
            return final
        if reactants:
            reactants = parse_speciesrefs(reactants)
        if products:
            products = parse_speciesrefs(products)
            
        # parse the subsystem, if available
        notes = findfirst(rxn,'notes')
        notetext = ET.tostring(notes)
        def parse_notes(pattern):
            patt = re.compile(pattern)
            results = patt.search(notetext)
            if results:
                return results.group("value")
            else:
                return None
        subsystem = parse_notes(subsystem_pattern)
        gpr = parse_notes(gpr_pattern)
        if gpr:
            genes = set([x for x in re.split(gene_split_pattern,gpr) if x])
        else:
            genes = None
        
        return Reaction(rid,
                        name=name,
                        reversible=reversible,
                        reactants=reactants,
                        products=products,
                        subsystem=subsystem,
                        gpr=gpr,
                        genes=genes)
    
    reactions = {}
    for rxn in findall(listOfReactions,'reaction'):
        parsed = parse_reaction(rxn)
        reactions[parsed.id] = parsed

    return dict(species=species, reactions=reactions, compartments=compartments)


if __name__ == '__main__':
    species,reactions,compartments = parse_sbml_file(file="../test/ecoli2011.xml")
    
    print "found", len(species), "species"
    print "found", len(reactions), "reactions"
    print "found", len(compartments), "compartments"
    
    print compartments
