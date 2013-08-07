
import json as JSON
import copy
import util
from model import Species, Reaction


# JSON model description structure
#
#   {
#       'compartments' : [
#           { 'id': ..., 'name': ..., 'outside': ... }, ...
#       ],
#
#       'species' : [
#           { 'id': ..., 'name': ..., 'compartment': ... }, ...
#       ],
#
#       'reactions' : [
#           {
#               'id': ...,
#               'reversible': true,
#               'reactants': ['id1', 'id2', ...],
#               'products': ['id1', 'id2', ...],
#               'subsystem': ...
#           }
#       ]
#   }

def parse_json_file(file):
    # returns a tuple:  (species,reactions,compartments)
    #   species:  { 'id' : Species(...) }
    #   reactions:  { 'id' : Reaction(...) }
    #   compartments { 'id' : ('name','outside') }

    model = util.parse_json_file(file)

    compartments = {}
    for compartment in model['compartments']:
        compartments[compartment['id']] = (compartment['name'],compartment['outside'])

    species = {}
    for sp in model['species']:
        species[sp['id']] = Species(sp['id'],name=sp['name'],compartment=sp['compartment'])

    reactions = {}
    for reaction in model['reactions']:
        reactants = [copy.deepcopy(species[s]) for s in reaction['reactants']]
        products = [copy.deepcopy(species[s]) for s in reaction['products']]
        reactions[reaction['id']] = Reaction(reaction['id'],
                                             reactants=reactants,
                                             products=products,
                                             reversible=reaction['reversible'],
                                             subsystem=reaction['subsystem'])

    return species,reactions,compartments