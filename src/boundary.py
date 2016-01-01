
from xml.etree.ElementTree import *
from svg.path import Line, parse_path, Path
from sbml import findfirst


tag = 'ns0:'

#create a point
def gen_point(x, y):
    return x + y * 1j

def remove_pt(numb):
    new_numb = numb.replace("pt", '')
    return float(new_numb)

#updated version compatible with metdraw svg output
def get_box_points_new(compartment_element):
    ptList = []
    ptFinal = []
    raw_list = findfirst(compartment_element, 'polygon').get('points').replace(' ',',').split(',')
    for i in xrange(0,8,2):
        pt = gen_point(float(raw_list[i]),float(raw_list[i+1]))
        ptList.append(pt)
    pt1 = ptList[1]
    pt2 = ptList[0]
    pt3 = ptList[3]
    pt4 = ptList[2]
    ptFinal.append(pt1)
    ptFinal.append(pt2)
    ptFinal.append(pt3)
    ptFinal.append(pt4)
    return ptFinal

#generates the exchange membrane path given a list of box points
def gen_membrane_path(boxPts):
    x1 = boxPts[0].real #- 50 - 105 #default spacer for now
    y1 = boxPts[0].imag #- 50 - 105
    x2 = boxPts[2].real #+ 50 + 105
    y2 = boxPts[2].imag #+ 50 + 105
    point1 = gen_point(x1, y1)
    point2 = gen_point(x1, y2)
    point3 = gen_point(x2, y2)
    point4 = gen_point(x2, y1)
    line1 = Line(point1, point2)
    line2 = Line(point2, point3)
    line3 = Line(point3, point4)
    line4 = Line(point4, point1)
    path = Path(line1, line2, line3, line4)
    return path.d()

#smoothes the reaction edges to look like a continuous line instead of blocked
def extend_edge(pathElem):
    tag = 'ns0:'
    path = parse_path(pathElem.get('d'))
    pt1 = path.point(0.0)
    pt2 = path.point(1.0)
    newPt1 = pt1.real + (pt1.imag - 1.25) * 1j
    newPt2 = pt2.real + (pt2.imag + 1.25) * 1j
    line = Line(newPt1, newPt2)
    newPath = Path(line)
    pathDef = newPath.d()
    newPathElem = Element(tag + 'path', attrib={'d': '%s' % pathDef})
    return newPathElem

#gets all g elements that are nodes
def get_nodes(lst):
    nodes = []
    for e in lst:
        if e.get('class') == 'node':
            if findfirst(e, 'ellipse').get('rx') == 0:
                pass
            else:
                nodes.append(e)
    return nodes
#gets all g elements that are edges
def get_edges(lst):
    edges = []
    for e in lst:
        if e.get('class') == 'edge':
            edges.append(e)
    return edges

def metab_overlap(a, b):
    for i in a:
        metab = i.id
        if metab in b:
            return True
    return False

def common_metab(a,b):
    for i in a:
        metab = i.id
        if metab in b:
            return metab
    return None

#creates a dictionary metabolite to its x and y values
#ex: {'G6P': 500+350j, 'Glu': 900+740j}
#these values act as 'near' in PolyPacker
def metab_dict(glist):
    nodes = get_nodes(glist)
    dct = {}
    for metab in nodes:
        if findfirst(metab, 'ellipse').get('rx') != '0':
            name = findfirst(metab, 'text').text
            if name not in dct:
                x = float(findfirst(metab, 'ellipse').get('cx'))
                y = float(findfirst(metab, 'ellipse').get('cy'))
                dct[name] = gen_point(x,y)
    return dct

def trans_parse(trans_str):
    trans = trans_str.split('translate')[1]
    trans = trans.replace('(', '').replace(')', '')
    trans = trans.split(' ')
    for i in range(0, len(trans)):
        trans[i] = float(trans[i]) + 150.0
    return trans

def remove_clustertag(s):
    s = s.replace('cluster_', '')
    return s[0]

def get_compPts(glist):
    pts_dict = {}
    for g in glist:
        if g.get('class') == 'cluster':
            comp = remove_clustertag(findfirst(g, 'title').text)
            pts_dict[comp] = get_box_points_new(g)
    return pts_dict
