

class Parameterized(object):
    def __init__(self,param=None,**KWARGS):
        if param is None:
            self._param = {}
        else:
            self._param = param
        self._param.update(**KWARGS)
        self._parent = None
    
    def has_param(self,name):
        return (name in self._param) or self.has_default(name)
    
    def has_default(self,name):
        if self._parent is None:
            return False
        else:
            return self._parent.has_param(name)
    
    def get_param(self,name):
        if name in self._param:
            return self._param[name]
        else:
            return self.get_default(name)
    
    def get_default(self,name):
        if self._parent is None:
            return None
        else:
            return self._parent.get_param(name)
    
    def set_param(self,name=None,value=None,**KWARGS):
        if name is not None:
            self._param[name] = value
        self._param.update(**KWARGS)
        
    def add_child(self,child):
        child._parent = self
        
    def set_parent(self,parent):
        self._parent = parent
     
     
class Species(Parameterized):
    def __init__(self,sid,name,compartment,minor=None):
        Parameterized.__init__(self)
        self.id = sid
        self.label_id = self.id
        self.name = name
        self.compartment = compartment
        if minor is not None:
            self.minor = minor
    
    @property
    def minor(self):
        if self.has_param("minors"):
            return self.id in self.get_param("minors")
        else:
            return False
    @minor.setter
    def minor(self,value):
        if value:
            self.set_param(minors=[self.id])
        else:
            self.set_param(minors=[])
    @property
    def major(self):
        return not self.minor
    @major.setter
    def major(self,value):
        self.minor = not value
    
    
class Reaction(Parameterized):
    def __init__(self,rid,name="",reactants=None,products=None,subsystem=None,
                      reversible=True,compact=False):
        Parameterized.__init__(self)
        self.id = rid
        self.reactants = reactants if reactants else []
        self.products = products if products else []
        self.reversible = reversible
        self.name = name
        self.subsystem = subsystem if subsystem else []
        
        for species in self.reactants:
            species.set_parent(self)
        for species in self.products:
            species.set_parent(self)
        
    @property
    def major_reactants(self):
        return [r for r in self.reactants if r.major]
    @property
    def minor_reactants(self):
        return [r for r in self.reactants if r.minor]
    @property
    def major_products(self):
        return [p for p in self.products if p.major]
    @property
    def minor_products(self):
        return [p for p in self.products if p.minor]
    @property
    def major_species(self):
        return self.major_reactants + self.major_products
    @property
    def minor_species(self):
        return self.minor_reactants + self.minor_products
    @property
    def species(self):
        return self.major_species + self.minor_species
    
    @property
    def compartment(self):
        comps = sorted([y for y in set([x.compartment for x in self.species])])
        return tuple(comps)
    @property
    def is_exchange(self):
        return (len(self.compartment) > 1
                    or len(self.reactants) == 0
                    or len(self.products) == 0)

    def consolidate_minors(self,n,sep=", "):
        def cycle_index(n):
            i = 0
            while True:
                yield i
                i += 1
                if i >= n:
                    i = 0
        def consolidate(minors):
            extra = minors[n:]
            minors = minors[0:n]
            indexer = cycle_index(n)
            for m in extra:
                minors[indexer.next()].name += sep + m.name
            return minors
        self.reactants = (self.major_reactants 
                          + consolidate(self.minor_reactants))
        self.products = (self.major_products
                          + consolidate(self.minor_products))


class Subsystem(Parameterized):
    def __init__(self,sid,name,reactions=None):
        Parameterized.__init__(self)
        self.id = sid
        self.name = name
        if reactions is None:
            self.reactions = []
        else:
            self.reactions = reactions
        
    def add_reaction(self,reaction):
        reaction.set_parent(self)
        self.reactions.append(reaction)
    
    @property
    def species(self):
        species = set()
        for rxn in self.reactions:
            species |= set(rxn.species)
        return species
    
    def apply_to_reactions(self,f,**kwargs):
        for rxn in self.reactions:
            f(rxn,**kwargs)

    @property
    def number_of_reactions(self):
        n = [0]
        def counter(rxn):
            n[0] += 1
        self.apply_to_reactions(counter)
        return n[0]
    
    def display(self,indent=''):
        print indent+str(len(self.reactions)),self.name
        
    
class Compartment(Parameterized):
    def __init__(self,cid,name,outside=None):
        Parameterized.__init__(self)
        self.id = cid
        self.name = name
        self.outside = outside
        self.compartments = []
        self.subsystems = []
        self.exchanges = []
        
    def add_exchange(self,rxn):
        rxn.set_parent(self)
        self.exchanges.append(rxn)
        
    def add_subsystem(self,sub):
        sub.set_parent(self)
        self.subsystems.append(sub)
        
    def add_compartment(self,comp):
        comp.set_parent(self)
        self.compartments.append(comp)
    
    @property
    def species(self):
        species = set()
        for comp in self.compartments:
            species |= comp.species
        for sub in self.subsystems:
            species |= sub.species
        for rxn in self.exchanges:
            species |= set(rxn.species)
        return species
    
    @property
    def local_exchanges(self):
        return [e for e in self.exchanges if e.compartment[0] == self.id]
    
    @property
    def exchange_names(self):
        names = [(e.id,e.compartment) for e in self.exchanges]
        for comp in self.compartments:
            names.extend(comp.exchange_names)
        return list(set(names))
    
    def apply_to_reactions(self,f,local=True,**kwargs):
        for comp in self.compartments:
            comp.apply_to_reactions(f,**kwargs)
        for sub in self.subsystems:
            sub.apply_to_reactions(f,**kwargs)
        if local:
            for rxn in self.local_exchanges:
                f(rxn,**kwargs)
        else:
            for rxn in self.exchanges:
                f(rxn,**kwargs)

    @property
    def number_of_reactions(self):
        n = [0]
        def counter(rxn):
            n[0] += 1
        self.apply_to_reactions(counter)
        return n[0]
    
    def display(self,indent=''):
        new_indent = indent + '   '
        print (indent + 
               "Compartment [{id}] {name}".format(id=self.id,name=self.name))
        print new_indent+str(len(self.local_exchanges)),"EXCHANGE REACTIONS"
        for sub in self.subsystems:
            sub.display(indent=new_indent)
        for comp in self.compartments:
            comp.display(indent=new_indent)
        

class Model(Parameterized):
    def __init__(self):
        Parameterized.__init__(self)
        self.name = None
        self.compartments = []
    
    def add_compartment(self,comp):
        comp.set_parent(self)
        self.compartments.append(comp)
    
    @property
    def species(self):
        species = set()
        for comp in self.compartments:
            species |= comp.species
        return species
    
    @property
    def exchange_names(self):
        names = []
        for comp in self.compartments:
            names.extend(comp.exchange_names)
        return list(set(names))
    
    def apply_to_reactions(self,f,**kwargs):
        for comp in self.compartments:
            comp.apply_to_reactions(f,**kwargs)

    @property
    def number_of_reactions(self):
        n = [0]
        def counter(rxn):
            n[0] += 1
        self.apply_to_reactions(counter)
        return n[0]
    
    def display(self):
        print "Model",self.name
        for comp in self.compartments:
            comp.display(indent='   ')
        

def nest_compartments(compartments):
    n_comps = len(compartments)
    n_prev = n_comps + 1
    while n_comps < n_prev:
        outside_ids = [c.outside for c in compartments.values()]
        insides = [c for c in compartments.values()
                     if c.id not in outside_ids and c.outside]
        for comp in insides:
            del compartments[comp.id]
            compartments[comp.outside].add_compartment(comp)
        n_prev = n_comps
        n_comps = len(compartments)
    return compartments

def build_model(species,reactions,compartments):
    # create the compartments
    for comp in compartments:
        name,outside = compartments[comp]
        compartments[comp] = Compartment(comp,name,outside=outside)
    
    # create the subsystems
    subnames = set([x.subsystem for x in reactions.values() if x.subsystem])
    subsystems = {}
    for i,name in enumerate(subnames):
        subsystems[name] = Subsystem(sid='SUBSYSTEM__'+str(i),
                                     name=name)
    
    # create orphan subsystem for each compartment
    orphans = {}
    for comp in compartments:
        orphan_name = 'UNASSIGNED[{name}]'.format(name=comp)
        orphans[comp] = Subsystem(sid=orphan_name,
                                  name=orphan_name)
    
    # assign the reactions
    for rxn in reactions.values():
        if rxn.is_exchange:
            for comp in rxn.compartment:
                compartments[comp].add_exchange(rxn)
        else:
            if rxn.subsystem:
                subsystems[rxn.subsystem].add_reaction(rxn)
            else:
                comp = rxn.compartment[0]
                orphans[comp].add_reaction(rxn)
    
    # assign subsystems to compartments
    for sub in subsystems.values():
        if sub.reactions:
            comp = sub.reactions[0].compartment[0]
            compartments[comp].add_subsystem(sub)
    for comp in compartments:
        if orphans[comp].reactions:
            compartments[comp].add_subsystem(orphans[comp])

    # build a model
    model = Model()
    compartments = nest_compartments(compartments)
    for comp in compartments.values():
        model.add_compartment(comp)
        
    return model

    
    