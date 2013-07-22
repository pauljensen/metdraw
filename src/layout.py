
import copy

from graphviz import AttrStmt,Node,Edge,Graph
from model import Model
import minors

def reaction_to_dot(rxn):
    INVISIBLE_NODE_ATTRS = rxn.get_param('INVISIBLE_NODE_ATTRS')
    EDGE_ATTRS = rxn.get_param('EDGE_ATTRS')
    MET_ATTRS = rxn.get_param('MET_ATTRS')
    COMPACT = rxn.get_param('COMPACT')
    SHOW_MINORS = rxn.get_param('SHOW_MINORS')
    MAX_MINORS = rxn.get_param('MAX_MINORS')
    MINOR_MET_ATTRS = rxn.get_param('MINOR_MET_ATTRS')
    
    METABOLITE_LABEL_TRANSFORM = rxn.get_param('METABOLITE_LABEL_TRANSFORM')
    
    REACTION_LABEL_TRANSFORM = rxn.get_param('REACTION_LABEL_TRANSFORM')
    label_id = REACTION_LABEL_TRANSFORM(rxn.id)
    
    statements = []
    statements.append(AttrStmt('edge',**EDGE_ATTRS))
    statements.append(AttrStmt('node',**MET_ATTRS))
    
    n_major_react = len(rxn.major_reactants)
    n_major_prod = len(rxn.major_products)
    n_minor_react = len(rxn.minor_reactants)
    n_minor_prod = len(rxn.minor_products)
    
    react_dir = "back" if rxn.reversible else "none"
    
    def edge_id():
        curr = 0
        while True:
            yield "$" + rxn.id + "::" + str(curr)
            curr += 1
    ids = edge_id()
    
    render_minors = SHOW_MINORS and n_minor_react + n_minor_prod > 0
    if render_minors:
        if (len(rxn.minor_reactants) > MAX_MINORS 
                or len(rxn.minor_products) > MAX_MINORS):
            # prevent this change from effecting the original rxn
            rxn = copy.deepcopy(rxn)
            rxn.consolidate_minors(MAX_MINORS)
        
        if COMPACT:
            rmnode = pmnode = "mnode::" + rxn.id
            statements.append(Node(rmnode,**INVISIBLE_NODE_ATTRS))
        else:    
            rmnode = "rmnode::" + rxn.id
            pmnode = "pmnode::" + rxn.id
            statements.append(Node(rmnode,**INVISIBLE_NODE_ATTRS))
            statements.append(Node(pmnode,**INVISIBLE_NODE_ATTRS))

        def minor_id(s):
            return s + "::" + rxn.id
        
        for r in rxn.minor_reactants:
            met_label = METABOLITE_LABEL_TRANSFORM(r.label_id)
            statements.append(Node(minor_id(r.id),label=met_label,
                                                  **MINOR_MET_ATTRS))
            statements.append(Edge(minor_id(r.id),rmnode,
                                   dir=react_dir,id=ids.next()))
        for p in rxn.minor_products:
            met_label = METABOLITE_LABEL_TRANSFORM(p.label_id)
            statements.append(Node(minor_id(p.id),label=met_label,
                                                  **MINOR_MET_ATTRS))
            statements.append(Edge(pmnode,minor_id(p.id),
                                   dir="forward",id=ids.next()))
            
        if not COMPACT:
            # connect the rm and pm nodes
            statements.append(Edge(rmnode,pmnode,dir="none",id=ids.next()))
        
    # make sure there is at least a "dummy" node on each side
    # create the nodes for major species
    if n_major_react == 0 and n_minor_react == 0:
        reactants = ["r_dummy::"+rxn.id]
        statements.append(Node(reactants[0],**INVISIBLE_NODE_ATTRS))
    else:
        reactants = [x.id for x in rxn.major_reactants]
        for r in rxn.major_reactants:
            met_label = METABOLITE_LABEL_TRANSFORM(r.label_id)
            statements.append(Node(r.id,label=met_label))
    if n_major_prod == 0 and n_minor_prod == 0:
        products = ["p_dummy::"+rxn.id]
        statements.append(Node(products[0],**INVISIBLE_NODE_ATTRS))
    else:
        products = [x.id for x in rxn.major_products]
        for p in rxn.major_products:
            met_label = METABOLITE_LABEL_TRANSFORM(p.label_id)
            statements.append(Node(p.id,label=met_label))
    
    rnode = "rnode::" + rxn.id
    pnode = "pnode::" + rxn.id
    if n_major_react > 0:
        statements.append(Node(rnode,**INVISIBLE_NODE_ATTRS))
    if n_major_prod > 0:
        statements.append(Node(pnode,**INVISIBLE_NODE_ATTRS))
    
    for r in rxn.major_reactants:
        statements.append(Edge(r.id,rnode,dir=react_dir,id=ids.next()))
    for p in rxn.major_products:
        statements.append(Edge(pnode,p.id,dir="forward",id=ids.next()))
    
    if render_minors:
        statements.append(Edge(rnode,rmnode,dir="none",id=ids.next()))
        statements.append(Edge(pmnode,pnode,dir="none",id=ids.next(),
                                            label=label_id))
    else:
        statements.append(Edge(rnode,pnode,dir="none",id=ids.next(),
                                           label=label_id))
        
    return statements


    
def unused_reaction_to_dot(rxn):    
    if len(reactants) == len(products) == 1:
        direction = "both" if rxn.reversible else "forward"
        statements.append(Edge(reactants[0],products[0],
                               dir=direction,label=rxn.id,**EDGE_ATTRS))
    elif len(reactants) == 1:
        center = "center::" + rxn.id
        statements.append(Node(center,**INVISIBLE_NODE_ATTRS))
        direction = "back" if rxn.reversible else "none"
        statements.append(Edge(reactants[0],center,
                               dir=direction,label=rxn.id,**EDGE_ATTRS))
        for p in products:
            statements.append(Edge(center,p,dir="forward",**EDGE_ATTRS))
    elif len(products) == 1:
        center = "center::" + rxn.id
        statements.append(Node(center,**INVISIBLE_NODE_ATTRS))
        direction = "back" if rxn.reversible else "none"
        for r in reactants:
            statements.append(Edge(r,center,dir=direction,**EDGE_ATTRS))
        statements.append(Edge(center,products[0],
                               dir="forward",label=rxn.id,**EDGE_ATTRS))
    else:
        r_center = "rcenter::" + rxn.id
        p_center = "pcenter::" + rxn.id
        if compact:
            r_center = "center" + rxn.id
            p_center = "center" + rxn.id
        statements.append(Node(r_center,**INVISIBLE_NODE_ATTRS))
        if p_center != r_center:
            statements.append(Node(p_center,**INVISIBLE_NODE_ATTRS))
            statements.append(Edge(r_center,p_center,
                                   dir="none",label=rxn.id,**EDGE_ATTRS))
        else:
            statements.append(Edge(r_center,p_center,
                                   label=rxn.id,style="invisible",))
            
        direction = "back" if rxn.reversible else "none"
        for r in reactants:
            statements.append(Edge(r,r_center,dir=direction,**EDGE_ATTRS))
        for p in products:
            statements.append(Edge(p_center,p,dir="forward",**EDGE_ATTRS))
            
    return statements
        

def old_reaction_to_dot(rxn):
    if not rxn.get_param('SHOW_MINORS') or rxn.get_param('MAX_MINORS') == 0:
        return reaction_to_dot_simple(rxn)
    
    INVISIBLE_NODE_ATTRS = rxn.get_param('INVISIBLE_NODE_ATTRS')
    EDGE_ATTRS = rxn.get_param('EDGE_ATTRS')
    MET_ATTRS = rxn.get_param('MET_ATTRS')
    CURR_MET_ATTRS = rxn.get_param('CURR_MET_ATTRS')
    
    ADD_MAJOR_LINKS = rxn.get_param('ADD_MAJOR_LINKS')
    
    if rxn.has_param("MAX_MINORS"):
        max_minors = rxn.get_param("MAX_MINORS")
        if (len(rxn.minor_reactants) > max_minors 
                or len(rxn.minor_products) > max_minors):
            # prevent this change from existing effecting the original rxn
            rxn = copy.deepcopy(rxn)
            rxn.consolidate_minors(max_minors)
    
    def make_id():
        curr = 0
        while True:
            yield "$" + rxn.id + "::" + str(curr)
            curr += 1
    ids = make_id()
    
    LINK_EDGE_ATTRS = dict(len=0.5,weight=2.0,style="invisible")
    MINOR_EDGE_ATTRS = dict(len=0.5,weight=2.0)
    PULL_EDGE_ATTRS = dict(len=0.5,weight=0.1,style="invisible")
    
    n_major_react = len(rxn.major_reactants)
    n_minor_react = len(rxn.minor_reactants)
    n_major_prod = len(rxn.major_products)
    n_minor_prod = len(rxn.minor_products)
    
    compact = rxn.get_param("COMPACT")
    
    statements = []
    statements.append(AttrStmt("edge",**EDGE_ATTRS))
    
    if (n_major_react == n_major_prod == 1
            and n_minor_react == n_minor_prod == 0):
        statements.append(AttrStmt("node",**MET_ATTRS))
        statements.append(Edge(rxn.major_reactants[0].id,
                               rxn.major_products[0].id,
                               dir="forward",id=ids.next()))
        return statements
    
    out_r_cent,r_cent,p_cent,out_p_cent = ["${0}::{1}".format(x,rxn.id) 
                                           for x in ("or","r","p","op")]
    if n_major_react + n_minor_react == 1:
        out_r_cent = r_cent = p_cent
    if n_major_prod + n_minor_prod == 1:
        out_p_cent = p_cent = r_cent
    if compact or (n_major_react + n_minor_react <= 2):
        out_r_cent = r_cent
    if compact or (n_major_prod + n_minor_prod <= 2):
        out_p_cent = p_cent
    
    curr_name = lambda name: name + "@" + rxn.id
    cluster = Graph(name="cluster_"+rxn.id,subgraph=True)
    cluster.add(AttrStmt("graph",color="transparent",ordering="in"))
    cluster.add(AttrStmt("node",**INVISIBLE_NODE_ATTRS))
    for center in set((out_r_cent,r_cent,p_cent,out_p_cent)):
        cluster.add(Node(center,**INVISIBLE_NODE_ATTRS))
    cluster.add(AttrStmt("node",**CURR_MET_ATTRS))
    
    for minor in rxn.minor_reactants:
        cluster.add(Edge(curr_name(minor.id),r_cent,
                         id=ids.next(),**MINOR_EDGE_ATTRS))
        if ADD_MAJOR_LINKS and out_r_cent != r_cent:
            # pin the node
            cluster.add(Edge(curr_name(minor.id),out_r_cent,
                             **LINK_EDGE_ATTRS))
    if out_r_cent != r_cent:
        cluster.add(Edge(out_r_cent,r_cent,len=0.5,id=ids.next()))
    for minor in rxn.minor_products:
        cluster.add(Edge(p_cent,curr_name(minor.id),dir="forward",
                         id=ids.next(),**MINOR_EDGE_ATTRS))
        if ADD_MAJOR_LINKS and out_p_cent != r_cent:
            cluster.add(Edge(out_p_cent,curr_name(minor.id),
                             id=ids.next(),**LINK_EDGE_ATTRS))
    if out_p_cent != p_cent:
        cluster.add(Edge(p_cent,out_p_cent,len=0.5,id=ids.next()))
    if p_cent != r_cent:
        cluster.add(Edge(p_cent,r_cent,len=0.5,id=ids.next()))
        
    statements.append(cluster)
    
    statements.append(AttrStmt("node",**MET_ATTRS))
    for major in rxn.major_reactants:
        statements.append(Edge(major.id,out_r_cent,id=ids.next()))
    for major in rxn.major_products:
        statements.append(Edge(out_p_cent,major.id,
                               dir="forward",id=ids.next()))
    
    if ADD_MAJOR_LINKS:    
        # pull the products and reactants closer together
        for l,r in zip(rxn.major_reactants[0:-1],rxn.major_reactants[1:]):
            statements.append(Edge(l.id,r.id,**PULL_EDGE_ATTRS))
        for l,r in zip(rxn.major_products[0:-1],rxn.major_products[1:]):
            statements.append(Edge(l.id,r.id,**PULL_EDGE_ATTRS))
        
    return statements

def clone_mets(subsystem):
    link_edges = []
    CLONE_LEVEL = subsystem.get_param('CLONE_LEVEL')
    LINK_CLONES = subsystem.get_param('LINK_CLONES')
    CLONE_LINK_ATTRS = subsystem.get_param('CLONE_LINK_ATTRS')
    def clone_out(sid):
        current = [0]
        def clone_aux(s):
            if s.major and s.id == sid:
                current[0] += 1
                s.id += '#' + str(current[0])
                if LINK_CLONES:
                    link_edges.append(Edge(s.id,s.label_id,
                                           dir="none",**CLONE_LINK_ATTRS))
        for rxn in subsystem.reactions:
            for r in rxn.reactants:
                clone_aux(r)
            for p in rxn.products:
                clone_aux(p)
        if current[0] > 0:
            link_edges.append(Node(sid,label=sid))
    
    counts = minors.count_species(subsystem)
    for count in counts:
        if count.count >= CLONE_LEVEL:
            clone_out(count.sid)
    return link_edges

def subsystem_to_dot(subsystem):
    clone_links = clone_mets(subsystem)
    g = Graph(name=subsystem.id)
    if subsystem.get_param('CLUSTER_SUBSYSTEMS'):
        g.cluster = True
        style = subsystem.get_param('SUBSYSTEM_BORDER_STYLE')
        g.add(AttrStmt('graph',style=style))
    for rxn in subsystem.reactions:
        g.add(reaction_to_dot(rxn))
    g.add(AttrStmt('graph',label=subsystem.name,
                   fontsize=subsystem.get_param('SUBSYSTEM_FONTSIZE')))
    if clone_links:
        g.add(clone_links)
    return g

def exchange_to_dot(ex):
    # append the compartment id to each species and make everything a minor
    for sp in ex.major_species:
        sp.id += " [{0}]".format(sp.compartment)
        sp.label_id = sp.id
        sp.minor = True
        
    return reaction_to_dot(ex)

def compartment_to_dot(compartment):
    g = Graph(name=compartment.id,cluster=True,subgraph=True)
    for subsystem in compartment.subsystems:
        gsub = subsystem_to_dot(subsystem)
        gsub.subgraph = True
        gsub.tag('::'+subsystem.id)
        g.add(gsub)
    for comp in compartment.compartments:
        gcomp = compartment_to_dot(comp)
        gcomp.subgraph = True
        gcomp.tag('::'+comp.id)
        g.add(gcomp)
    label = AttrStmt('graph',label=compartment.name,
                     fontsize=compartment.get_param('COMPARTMENT_FONTSIZE'))
    g.add(label)
    
    SHOW_EXCHANGES = compartment.get_param('SHOW_EXCHANGES')
    if SHOW_EXCHANGES and compartment.local_exchanges:
        gex = Graph(name=compartment.id+"::EX",cluster=True)
        gex.add(g)
        gex.add(AttrStmt('graph',style="dotted"))
        for ex in compartment.local_exchanges:
            gex.add(exchange_to_dot(ex)) 
        return gex
    else:
        return g

def model_to_dot(model):
    g = Graph(name=model.name)
    for comp in model.compartments:
        gcomp = compartment_to_dot(comp)
        gcomp.subgraph = True
        gcomp.tag('::'+comp.id)
        g.add(gcomp)
    if model.get_param('FORCE_LABELS'):
        g.add(AttrStmt('graph',forcelabels="true"))

    return g
