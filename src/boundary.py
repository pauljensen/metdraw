
from xml.etree.ElementTree import *
from svg.path import Line, parse_path, Path
from packing import PolyPacker
from exchange_layout import gen_graph

def tagmatch(elem,tag):
    return elem.tag.endswith('}' + tag)

def findfirst(elem,tag):
    for e in elem.iter():
        if tagmatch(e,tag):
            return e

def findall(elem,tag):
    return [e for e in elem.iter() if tagmatch(e,tag)]

tag = 'ns0:'

#create a point
def gen_point(x, y):
    return x + y * 1j

#finds the size of the reaction from the halfway point of the midpoint segment
#  to the major/minor product arrows (currently not in use)
def rxn_size(svg_tree):
    mp = ""
    allG = findall(svg_tree, 'g')
    for g in allG:
        if g.get('id') == 'midpoint':
            mp = parse_path(findfirst(g,'path').get('d')).point(.5)
    points = []
    pathList = findall(svg_tree, 'path')
    pathList2 = []
    for path in pathList:
        pathList2.append(parse_path(path.get('d')))
    for path2 in pathList2:
        points.append(path2.point(1.0).imag)
    minimum = max(points)
    y = mp.imag
    pt1 = gen_point(0, y)
    pt2 = gen_point(0, minimum)
    line = Line(pt1, pt2)
    length = line.length()
    return length

#returns a list of box points given an inital path
def get_box_points(box_path):
    path1 = parse_path(box_path)
    point1 = path1.point(0)
    point3 = path1.point(0.5)
    y_length = point3.imag - point1.imag
    y_ratio = float(y_length / path1.length())
    point2 = path1.point(y_ratio)
    point4 = path1.point(0.5 + y_ratio)
    return [point1, point2, point3, point4]

#generates the exchange membrane path given a list of box points
def gen_membrane_path(boxPts):
    x1 = boxPts[0].real - 50 - 105 #default spacer for now
    y1 = boxPts[0].imag - 50 - 105
    x2 = boxPts[2].real + 50 + 105
    y2 = boxPts[2].imag + 50 + 105
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
            nodes.append(e)
    return nodes
#gets all g elements that are edges
def get_edges(lst):
    edges = []
    for e in lst:
        if e.get('class') == 'edge':
            edges.append(e)
    return edges

def get_id(rxn_metab):
    return rxn_metab.id

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
        name = findfirst(metab, 'title').text
        if name not in dct:
            x = float(findfirst(metab, 'ellipse').get('cx'))
            y = float(findfirst(metab, 'ellipse').get('cy'))
            dct[name] = gen_point(x,y)
    return dct

file2 = open("box.svg", "r")
file3 = open("output.svg", "w")
tree2 = ElementTree(file=file2)
graph2 = tree2.getroot()
glist2 = findall(graph2, 'g')

#create the new membrane box path
boxPath = findfirst(graph2, 'path').get('d')
boxStart = parse_path(boxPath)
boxPoints = get_box_points(boxPath)
newBoxPath = gen_membrane_path(boxPoints)
newBoxPts = get_box_points(newBoxPath)
memBoxStart = parse_path(newBoxPath)
pathElement = Element(tag + 'path',
                      attrib={'d': '' + gen_membrane_path(boxPoints)})
boxList = findall(graph2[0], 'g')
for g in boxList:
    if g.get('style') != None:
        g.append(pathElement) #writes the new box path in the file

#create PolyPacker object
pp = PolyPacker(newBoxPts)

#useful numbers when it comes to transforming
# the reactions to the correct place
memBoxStart_x = memBoxStart.point(0).real
memBoxStart_y = memBoxStart.point(0).imag

#create the metabolite dictionary from the main compartment
metabDict = metab_dict(graph2)

#rxnList is just a list of reactions to place
for rxn in rxnList:
    graphDot = gen_graph(rxn)
    graphDot.export_graphviz(output="svg", filename="dotprac2")
    file1 = open("dotprac2.svg", "r")
    tree = ElementTree(file=file1)

    graph1 = tree.getroot()[0]
    glist = findall(graph1, 'g')
    nodeList = get_nodes(glist)
    edgeList = get_edges(glist)

    for edge in edgeList:
        path = findfirst(edge, 'path')
        path.set('d', extend_edge(path).get('d')) #smooth out edges
        if edge.get('id') == "midpoint":
            path = findfirst(edge, 'path')
            d = path.get('d')
            x = parse_path(d).point(0.0).real
            path_end = parse_path(d).point(1.0)
            midpoint = parse_path(d).point(.5) #find midpoint,
                                               #   used for transforming
    path_x = path_end.real #poorly named variable that is necessary for
                           #   transforming; basically half-width of rxn

    #generates the lines that are used for transforming the rxns
    leftLine = Line(newBoxPts[0], newBoxPts[1]) #creates the line
    bottomLine = Line(newBoxPts[1], newBoxPts[2])
    rightLine = Line(newBoxPts[2], newBoxPts[3])
    topLine = Line(newBoxPts[3], newBoxPts[0])

    g = findfirst(graph1, 'polygon') #this solves the overlapping issue where
                                     # the box was covering the rxns
    g.set('fill', 'none')

    scale = "scale(1 1) "
    metabList = rxn.major_products
    if metab_overlap(metabList, metabDict):
        name = common_metab(metabList, metabDict)
        near = metabDict[name]
    else:
        near = gen_point(bottomLine.point(.5).real, leftLine.point(.5).imag)
    pack = pp.pack(path_x * 2.0 + 15.0, near=near)
    pack_mp = pack[0].point(.5)
    if pack[2] == 3:
        rotateTop = "rotate(%f %f %f) " % (0, memBoxStart_x, memBoxStart_y)
        translateTop = "translate(%f %f)" % (pack_mp.real - path_x,
                                             memBoxStart_y - midpoint.imag)
        transform = scale + rotateTop + translateTop
    if pack[2] == 0:
        rotateLeft = "rotate(%f %f %f) " % (270, memBoxStart_x, memBoxStart_y)
        translateLeft = "translate(%f %f)" % (memBoxStart_x + memBoxStart_y -
                                              path_x - pack_mp.imag,
                                              memBoxStart_y - midpoint.imag)
        transform = scale + rotateLeft + translateLeft
    if pack[2] == 1:
        rotateBott = "rotate(%f %f %f) " % (180, memBoxStart_x, memBoxStart_y)
        translateBott = "translate(%f %f)" % (memBoxStart_x + memBoxStart_x
                                                - path_x - pack_mp.real,
                                                memBoxStart_y - midpoint.imag
                                                - leftLine.length())
        transform = scale + rotateBott + translateBott
    if pack[2] == 2:
        rotateRight = "rotate(%f %f %f) " % (90, memBoxStart_x, memBoxStart_y)
        translateRight = "translate(%f %f)" % (memBoxStart_x - path_x +
                                               pack_mp.imag - memBoxStart_y,
                                               memBoxStart_y - midpoint.imag -
                                               topLine.length())
        transform = scale + rotateRight + translateRight

    for g in glist:
        if g.get('id') == 'rxn':
            g.set('transform', transform)

    graph2.append(graph1)

    tree2.write("output.svg")

file1.close()
file2.close()
file3.close()