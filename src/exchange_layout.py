
from graphviz import *


def gen_sub_majr(rxn):
    EDGE_ATTRS = rxn.get_param('EDGE_ATTRS')
    MET_ATTRS = rxn.get_param('MET_ATTRS')
    sub_majr = Graph(name="majr", subgraph=True)
    sub_majr.add(AttrStmt('graph', **{'rank': 'min'}))
    sub_majr.add(AttrStmt('node', **MET_ATTRS))
    sub_majr.add(AttrStmt('edge', **EDGE_ATTRS))
    for i in range(0,len(rxn.major_reactants)):
        node = Node(rxn.major_reactants[i].id)
        sub_majr.add(node)
    return sub_majr

def gen_sub_minr(rxn):
    INVISIBLE_NODE_ATTRS = rxn.get_param('INVISIBLE_NODE_ATTRS')
    EDGE_ATTRS = rxn.get_param('EDGE_ATTRS')
    MINOR_MET_ATTRS = rxn.get_param('MINOR_MET_ATTRS')
    sub_minr = Graph(name="minr", subgraph=True)
    sub_minr.add(AttrStmt('graph', **{'rank': 'same'}))

    sub_minr.add(Node('invismajr', **INVISIBLE_NODE_ATTRS))
    sub_minr.add(AttrStmt('node', **MINOR_MET_ATTRS))
    sub_minr.add(AttrStmt('edge', **EDGE_ATTRS))
    nodes1 = []
    for i in range(0,(len(rxn.minor_reactants) / 2)):
        node1 = Node(rxn.minor_reactants[i].id)
        nodes1.append(node1)
    nodes2 = []
    for i in range((len(rxn.minor_reactants) /2), len(rxn.minor_reactants)):
        node2 = Node(rxn.minor_reactants[i].id)
        nodes2.append(node2)
    for i in range(0, len(nodes1) - 1):
            edge1 = Edge(nodes1[i].name, nodes1[i+1].name, **{'style' : 'invis'})
            sub_minr.add(edge1)
    if len(nodes1) > 0:
        last_node = nodes1[-1]
        last_edge = Edge(last_node.name, 'invismajr', **{'style' : 'invis'})
        last_edge2 = Edge('invismajr', nodes2[0].name, **{'style' : 'invis'})
        sub_minr.add(last_edge)
        sub_minr.add(last_edge2)
    elif len(nodes2) > 0:
        last_edge2 = Edge('invismajr', nodes2[0].name, **{'style' : 'invis'})
        sub_minr.add(last_edge2)
    for i in range(0, len(nodes2) - 1):
            edge2 = Edge(nodes2[i].name, nodes2[i+1].name, **{'style' : 'invis'})
            sub_minr.add(edge2)
    return sub_minr

def gen_sub_invis(rxn):
    INVISIBLE_NODE_ATTRS = rxn.get_param('INVISIBLE_NODE_ATTRS')
    sub_invis = Graph(name="invis", subgraph=True)
    sub_invis.add(Node('invisminr', **INVISIBLE_NODE_ATTRS))
    sub_invis.add(Node('invisminp', **INVISIBLE_NODE_ATTRS))
    return sub_invis

def gen_sub_minp(rxn):
    INVISIBLE_NODE_ATTRS = rxn.get_param('INVISIBLE_NODE_ATTRS')
    EDGE_ATTRS = rxn.get_param('EDGE_ATTRS')
    MINOR_MET_ATTRS = rxn.get_param('MINOR_MET_ATTRS')
    sub_minp = Graph(name="minp", subgraph=True)
    sub_minp.add(AttrStmt('graph', **{'rank': 'same'}))
    sub_minp.add(Node('invismajp', **INVISIBLE_NODE_ATTRS))
    sub_minp.add(AttrStmt('node', **MINOR_MET_ATTRS))
    sub_minp.add(AttrStmt('edge', **EDGE_ATTRS))
    nodes1 = []
    for i in range(0,(len(rxn.minor_products) / 2)):
        node1 = Node(rxn.minor_products[i].id)
        nodes1.append(node1)
    nodes2 = []
    for i in range((len(rxn.minor_products) /2), len(rxn.minor_products)):
        node2 = Node(rxn.minor_products[i].id)
        nodes2.append(node2)
    for i in range(0, len(nodes1) - 1):
            edge1 = Edge(nodes1[i].name, nodes1[i+1].name, **{'style' : 'invis'})
            sub_minp.add(edge1)
    if len(nodes1) > 0:
        last_node = nodes1[-1]
        last_edge = Edge(last_node.name, 'invismajp', **{'style' : 'invis'})
        last_edge2 = Edge('invismajp', nodes2[0].name, **{'style' : 'invis'})
        sub_minp.add(last_edge)
        sub_minp.add(last_edge2)
    elif len(nodes2) > 0:
        last_edge2 = Edge('invismajp', nodes2[0].name, **{'style' : 'invis'})
        sub_minp.add(last_edge2)
    for i in range(0, len(nodes2) - 1):
            edge2 = Edge(nodes2[i].name, nodes2[i+1].name, **{'style' : 'invis'})
            sub_minp.add(edge2)
    return sub_minp

def gen_sub_majp(rxn):
    EDGE_ATTRS = rxn.get_param('EDGE_ATTRS')
    MET_ATTRS = rxn.get_param('MET_ATTRS')
    sub_majp = Graph(name="majp", subgraph=True)
    sub_majp.add(AttrStmt('graph', **{'rank': 'max'}))
    sub_majp.add(AttrStmt('node', **MET_ATTRS))
    sub_majp.add(AttrStmt('edge', **EDGE_ATTRS))
    for i in range(0,len(rxn.major_products)):
        node = Node(rxn.major_products[i].id)
        sub_majp.add(node)
    return sub_majp

def gen_r_edges(rxn):
    react_dir = "back" if rxn.reversible else "none"
    edges = []
    for i in range(0, len(rxn.major_reactants)):
        edge = Edge(rxn.major_reactants[i].id, 'invismajr', dir=react_dir)
        edges.append(edge)
    for i in range(0, len(rxn.minor_reactants)):
        edge = Edge(rxn.minor_reactants[i].id, 'invisminr', dir=react_dir)
        edges.append(edge)
    return edges

def gen_p_edges(rxn):
    edges = []
    for i in range(0, len(rxn.major_products)):
        edge = Edge('invismajp', rxn.major_products[i].id)
        edges.append(edge)
    for i in range(0, len(rxn.minor_products)):
        edge = Edge('invisminp', rxn.minor_products[i].id)
        edges.append(edge)
    return edges

def gen_graph(rxn):
    INVISIBLE_NODE_ATTRS = rxn.get_param('INVISIBLE_NODE_ATTRS')
    EDGE_ATTRS = rxn.get_param('EDGE_ATTRS')
    weight = {'weight' : '10'}
    weight_mp = {'weight' : '10', 'id' : 'midpoint'}
    wdm = {'weight' : '10', 'dir' : 'forward','id' : 'midpoint'}
    invis = []
    if len(rxn.major_reactants) == 0:
        if len(rxn.minor_reactants) == 0:
            if len(rxn.minor_products) == 0:
                if len(rxn.major_products) == 0:
                    invis.append(Edge('invismajr', 'invismajp', **wdm))
                else:
                    invis.append(Edge('invismajr', 'invismajp', **weight_mp))
            elif len(rxn.major_products) == 0:
                invis.append(Edge('invismajr', 'invisminp', **weight_mp))
            else:
                invis.append(Edge('invismajr', 'invisminp', **weight_mp))
                invis.append(Edge('invisminp', 'invismajp', **weight))
        elif len(rxn.minor_products) == 0:
            if len(rxn.major_products) == 0:
                invis.append(Edge('invisminr', 'invismajp', **wdm))
            else:
                invis.append(Edge('invisminr', 'invismajp', **weight_mp))
        else:
            if len(rxn.major_products) == 0:
                invis.append(Edge('invisminr', 'invisminp', **weight_mp))
            else:
                invis.append(Edge('invisminr', 'invisminp', **weight_mp))
                invis.append(Edge('invisminp','invismajp', **weight))
    else:
        if len(rxn.minor_reactants) == 0:
            if len(rxn.minor_products) == 0:
                if len(rxn.major_products) == 0:
                    invis.append(Edge('invismajr', 'invismajp', **wdm))
                else:
                    invis.append(Edge('invismajr', 'invismajp', **weight_mp))
            elif len(rxn.major_products) == 0:
                invis.append(Edge('invismajr', 'invisminp', **weight_mp))
            else:
                invis.append(Edge('invismajr', 'invisminp', **weight_mp))
                invis.append(Edge('invisminp', 'invismajp', **weight))
        elif len(rxn.minor_products) == 0:
            if len(rxn.major_products) == 0:
                invis.append(Edge('invismajr', 'invisminr', **weight))
                invis.append(Edge('invisminr', 'invisminp', **wdm))
            else:
                invis.append(Edge('invismajr', 'invisminr', **weight))
                invis.append(Edge('invisminr', 'invismajp', **weight_mp))
        else:
            if len(rxn.major_products) == 0:
                invis.append(Edge('invismajr', 'invisminr', **weight))
                invis.append(Edge('invisminr', 'invisminp', **weight_mp))
            else:
                invis.append(Edge('invismajr', 'invisminr', **weight))
                invis.append(Edge('invisminr', 'invisminp', **weight_mp))
                invis.append(Edge('invisminp', 'invismajp', **weight))
    graph = Graph(name="graph")
    if rxn.get_param('FORCE_LABELS'):
        graph.add(AttrStmt('graph',forcelabels="true"))
    graph.add(AttrStmt('edge', **EDGE_ATTRS))
    graph.add(Node('invismajr', **INVISIBLE_NODE_ATTRS))
    graph.add(Node('invisminr', **INVISIBLE_NODE_ATTRS))
    graph.add(Node('invisminp', **INVISIBLE_NODE_ATTRS))
    graph.add(Node('invismajp', **INVISIBLE_NODE_ATTRS))
    for edge in invis:
        graph.add(edge)
    graph.add(AttrStmt('graph', **{'id': 'rxn'}))
    graph.add(gen_sub_majr(rxn))
    graph.add(gen_sub_minr(rxn))
    graph.add(gen_sub_invis(rxn))
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

