
from graphviz import *

maj_node_attrs = {'color':"orange", 'fixedsize':'true', 'style':'filled',
                  'shape':'circle', 'fillcolor':'orange',
                  'width':'0.50', 'fontsize':8.0}
min_node_attrs = {'color':"orange", 'fixedsize':'true', 'style':'filled',
                  'shape':'circle', 'fillcolor':'orange',
                  'width':'0.30', 'fontsize':8.0}
invis_node_attrs = {'style': 'invis', 'fontsize': '1.0', 'fixedsize' : 'true',
                    'width': '0.0', 'shape': 'circle', 'label': ''}
edge_attrs = {'penwidth':5.0, 'color': 'purple'}

invismajr = Node('invismajr', **invis_node_attrs)
invisminr = Node('invisminr', **invis_node_attrs)
invisminp = Node('invisminp', **invis_node_attrs)
invismajp = Node('invismajp', **invis_node_attrs)

def gen_sub_majr(rxn):
    sub_majr = Graph(name="majr", subgraph=True)
    sub_majr.add(AttrStmt('graph', **{'rank': 'min'}))
    sub_majr.add(AttrStmt('node', **maj_node_attrs))
    sub_majr.add(AttrStmt('edge', **edge_attrs))
    for i in range(0,len(rxn.major_reactants)):
        node = Node("%s" % rxn.major_reactants[i].id)
        sub_majr.add(node)
    return sub_majr

def gen_sub_minr(rxn):
    sub_minr = Graph(name="minr", subgraph=True)
    sub_minr.add(AttrStmt('graph', **{'rank': 'same'}))

    sub_minr.add(invismajr)
    sub_minr.add(AttrStmt('node', **min_node_attrs))
    sub_minr.add(AttrStmt('edge', **edge_attrs))
    nodes1 = []
    for i in range(0,(len(rxn.minor_reactants) / 2)):
        node1 = Node('%s' % rxn.minor_reactants[i].id)
        nodes1.append(node1)
    nodes2 = []
    for i in range((len(rxn.minor_reactants) /2), len(rxn.minor_reactants)):
        node2 = Node('%s' % rxn.minor_reactants[i].id)
        nodes2.append(node2)
    for i in range(0, len(nodes1) - 1):
            edge1 = Edge(nodes1[i], nodes1[i+1], **{'style' : 'invis'})
            sub_minr.add(edge1)
    if len(nodes1) > 0:
        last_node = nodes1[-1]
        last_edge = Edge(last_node, Node('invismajr'), **{'style' : 'invis'})
        last_edge2 = Edge(Node('invismajr'), nodes2[0], **{'style' : 'invis'})
        sub_minr.add(last_edge)
        sub_minr.add(last_edge2)
    elif len(nodes2) > 0:
        last_edge2 = Edge(Node('invismajr'), nodes2[0], **{'style' : 'invis'})
        sub_minr.add(last_edge2)
    for i in range(0, len(nodes2) - 1):
            edge2 = Edge(nodes2[i], nodes2[i+1], **{'style' : 'invis'})
            sub_minr.add(edge2)
    return sub_minr

def gen_sub_invis():
    sub_invis = Graph(name="invis", subgraph=True)
    sub_invis.add(invisminr)
    sub_invis.add(invisminp)
    return sub_invis

def gen_sub_minp(rxn):
    sub_minp = Graph(name="minp", subgraph=True)
    sub_minp.add(AttrStmt('graph', **{'rank': 'same'}))
    sub_minp.add(invismajp)
    sub_minp.add(AttrStmt('node', **min_node_attrs))
    sub_minp.add(AttrStmt('edge', **edge_attrs))
    nodes1 = []
    for i in range(0,(len(rxn.minor_products) / 2)):
        node1 = Node('%s' % rxn.minor_products[i].id)
        nodes1.append(node1)
    nodes2 = []
    for i in range((len(rxn.minor_products) /2), len(rxn.minor_products)):
        node2 = Node('%s' % rxn.minor_products[i].id)
        nodes2.append(node2)
    for i in range(0, len(nodes1) - 1):
            edge1 = Edge(nodes1[i], nodes1[i+1], **{'style' : 'invis'})
            sub_minp.add(edge1)
    if len(nodes1) > 0:
        last_node = nodes1[-1]
        last_edge = Edge(last_node, Node('invismajp'), **{'style' : 'invis'})
        last_edge2 = Edge(Node('invismajp'), nodes2[0], **{'style' : 'invis'})
        sub_minp.add(last_edge)
        sub_minp.add(last_edge2)
    elif len(nodes2) > 0:
        last_edge2 = Edge(Node('invismajp'), nodes2[0], **{'style' : 'invis'})
        sub_minp.add(last_edge2)
    for i in range(0, len(nodes2) - 1):
            edge2 = Edge(nodes2[i], nodes2[i+1], **{'style' : 'invis'})
            sub_minp.add(edge2)
    return sub_minp

def gen_sub_majp(rxn):
    sub_majp = Graph(name="majp", subgraph=True)
    sub_majp.add(AttrStmt('graph', **{'rank': 'max'}))
    sub_majp.add(AttrStmt('node', **maj_node_attrs))
    sub_majp.add(AttrStmt('edge', **edge_attrs))
    for i in range(0,len(rxn.major_products)):
        node = Node("%s" % rxn.major_products[i].id)
        sub_majp.add(node)
    return sub_majp

def gen_r_edges(rxn):
    edges = []
    for i in range(0, len(rxn.major_reactants)):
        edge = Edge(Node('%s' % rxn.major_reactants[i].id), Node('invismajr'))
        edges.append(edge)
    for i in range(0, len(rxn.minor_reactants)):
        edge = Edge(Node('%s' % rxn.minor_reactants[i].id), Node('invisminr'))
        edges.append(edge)
    return edges

def gen_p_edges(rxn):
    edges = []
    for i in range(0, len(rxn.major_products)):
        edge = Edge(Node('invismajp'), Node('%s' % rxn.major_products[i].id))
        edges.append(edge)
    for i in range(0, len(rxn.minor_products)):
        edge = Edge(Node('invisminp'), Node('%s' % rxn.minor_products[i].id))
        edges.append(edge)
    return edges

def gen_graph(rxn):
    weight = {'weight' : '10'}
    weight_mp = {'weight' : '10', 'id' : 'midpoint'}
    wdm = {'weight' : '10', 'dir' : 'forward','id' : 'midpoint'}
    invis = []
    if len(rxn.major_reactants) == 0:
        if len(rxn.minor_reactants) == 0:
            if len(rxn.minor_products) == 0:
                if len(rxn.major_products) == 0:
                    invis.append(Edge(invismajr, invismajp, **wdm))
                else:
                    invis.append(Edge(invismajr, invismajp, **weight_mp))
            elif len(rxn.major_products) == 0:
                invis.append(Edge(invismajr, invisminp, **weight_mp))
            else:
                invis.append(Edge(invismajr, invisminp, **weight_mp))
                invis.append(Edge(invisminp, invismajp, **weight))
        elif len(rxn.minor_products) == 0:
            if len(rxn.major_products) == 0:
                invis.append(Edge(invisminr, invismajp, **wdm))
            else:
                invis.append(Edge(invisminr, invismajp, **weight_mp))
        else:
            if len(rxn.major_products) == 0:
                invis.append(Edge(invisminr, invisminp, **weight_mp))
            else:
                invis.append(Edge(invisminr, invisminp, **weight_mp))
                invis.append(Edge(invisminp,invismajp, **weight))
    else:
        if len(rxn.minor_reactants) == 0:
            if len(rxn.minor_products) == 0:
                if len(rxn.major_products) == 0:
                    invis.append(Edge(invismajr, invismajp, **wdm))
                else:
                    invis.append(Edge(invismajr, invismajp, **weight_mp))
            elif len(rxn.major_products) == 0:
                invis.append(Edge(invismajr, invisminp, **weight_mp))
            else:
                invis.append(Edge(invismajr, invisminp, **weight_mp))
                invis.append(Edge(invisminp, invismajp, **weight))
        elif len(rxn.minor_products) == 0:
            if len(rxn.major_products) == 0:
                invis.append(Edge(invismajr, invisminr, **weight))
                invis.append(Edge(invisminr, invisminp, **wdm))
            else:
                invis.append(Edge(invismajr, invisminr, **weight))
                invis.append(Edge(invisminr, invismajp, **weight_mp))
        else:
            if len(rxn.major_products) == 0:
                invis.append(Edge(invismajr, invisminr, **weight))
                invis.append(Edge(invisminr, invisminp, **weight_mp))
            else:
                invis.append(Edge(invismajr, invisminr, **weight))
                invis.append(Edge(invisminr, invisminp, **weight_mp))
                invis.append(Edge(invisminp, invismajp, **weight))
    graph = Graph(name="graph")
    graph.add(AttrStmt('edge', **edge_attrs))
    graph.add(invismajr)
    graph.add(invisminr)
    graph.add(invisminp)
    graph.add(invismajp)
    for edge in invis:
        graph.add(edge)
    graph.add(AttrStmt('graph', **{'id': 'rxn'}))
    graph.add(gen_sub_majr(rxn))
    graph.add(gen_sub_minr(rxn))
    graph.add(gen_sub_invis())
    graph.add(gen_sub_minp(rxn))
    graph.add(gen_sub_majp(rxn))
    r_edges = gen_r_edges(rxn)
    for edge in r_edges:
        graph.add(edge)
    graph.add(AttrStmt('edge', **{'dir': 'forward'}))
    p_edges = gen_p_edges(rxn)
    for edge in p_edges:
        graph.add(edge)
    return graph





