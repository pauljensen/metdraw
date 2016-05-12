from xml.etree.ElementTree import *
from svg.path import Line, parse_path, Path
from sbml import findfirst

tag = 'ns0:'

# create a point
def gen_point(x, y):
    return x + y * 1j

# remove 'pt' tag from height/width attribute
def remove_pt(numb):
    new_numb = numb.replace("pt", '')
    return float(new_numb)

# return new transform string given an x,y
def newTransform(x,y):
    s = "scale(1 1) "
    r = "rotate(0) "
    t = "translate(%f %f)" % (x, y)
    return s + r + t

# return string of points used for box around compartments
def polyPts(pts):
    pt1 = str(pts[0]) + "," + str(pts[3])
    pt2 = str(pts[0]) + "," + str(pts[1])
    pt3 = str(pts[2]) + "," + str(pts[1])
    pt4 = str(pts[2]) + "," + str(pts[3])
    pt5 = str(pts[0]) + "," + str(pts[3])
    p = pt1 + ' ' + pt2 + ' ' + pt3 + ' ' + pt4 + ' ' + pt5
    return p

# return new viewBox
def newVB(pts):
    if len(pts) == 1:
        return str(pts[0])
    else:
        p = pts.pop()
        return newVB(pts) + " " + str(p)

# updated version compatible with metdraw svg output
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

# generates line objects for exchange membrane path from list of box points
def gen_membrane_path(boxPts):
    x1 = boxPts[0].real
    y1 = boxPts[0].imag
    x2 = boxPts[2].real
    y2 = boxPts[2].imag
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

# smoothes the reaction edges to look continuous instead of blocked
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

# gets all g elements that are nodes
def get_nodes(lst):
    nodes = []
    for e in lst:
        if e.get('class') == 'node':
            if findfirst(e, 'ellipse').get('rx') == 0:
                pass
            else:
                nodes.append(e)
    return nodes

# gets all g elements that are edges
def get_edges(lst):
    edges = []
    for e in lst:
        if e.get('class') == 'edge':
            edges.append(e)
    return edges

# see if any rxn metabs are in dict of all metabs in graph
def metab_overlap(a, b):
    for i in a:
        metab = i.id
        if metab in b:
            return True
    return False

# return the common metab
def common_metab(a,b):
    for i in a:
        metab = i.id
        if metab in b:
            return metab
    return None

# creates a dictionary metabolite to its x and y values
# example: {'G6P': 500+350j, 'Glu': 900+740j}
# these values act as 'near' in PolyPacker
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

def remove_clustertag(s):
    s = s.replace('cluster_', '')
    return s.split('::')[0]

# return list of points where compartment line is drawn
def get_compPts(glist):
    pts_dict = {}
    for g in glist:
        if g.get('class') == 'cluster':
            comp = remove_clustertag(findfirst(g, 'title').text)
            pts_dict[comp] = get_box_points_new(g)
    return pts_dict

# draw a box enclosing the image
# the coordinates are the size of the file from the viewBox attribute
def bounding_box(filename):
    ofile = open((filename), "r+")
    main_tree = ElementTree(file=ofile)
    main_graph = main_tree.getroot()
    dimens = main_graph.attrib
    ptList = dimens['viewBox'].split(" ")
    points = polyPts(ptList)

    g_attribs = {'class': "graph", 'id': 'comp1'}
    boxGraph = Element(tag + 'g', **g_attribs)
    poly_attribs = {'fill': 'none', 'points': points, 'stroke': 'black'}
    SubElement(boxGraph, tag + 'polygon', **poly_attribs)

    main_graph.append(boxGraph)
    main_tree.write(filename)
    ofile.close()
    return filename

# combine two SVG compartment files into one
# if align is true, the image is translated horizontally only
def combineSVGs(mainfile, compfile, align=False):
    mfile = open((mainfile), "r+")
    main_tree = ElementTree(file=mfile)
    main_graph = main_tree.getroot()
    cfile = open((compfile), "r+")
    comp_tree = ElementTree(file=cfile)
    comp_graph = comp_tree.getroot()

    dimens = main_graph.attrib
    main_points = dimens['viewBox'].split(" ")
    main_width = main_points[2]
    dimens2 = comp_graph.attrib
    comp_points = dimens2['viewBox'].split(" ")
    comp_width = comp_points[2]
    trans_width = float(main_width) + 600
    new_width = trans_width + float(comp_width)
    main_points[2] = str(new_width)
    dimens['width'] = (str(new_width))
    if float(main_points[3]) > float(comp_points[3]):
        if align:
            dimens['height'] = (str(float(main_points[3])))
            main_points[3] = str(float(main_points[3]))
        else:
            dimens['height'] = (str(float(main_points[3]) + 600))
            main_points[3] = str(float(main_points[3]) + 600)
    else:
        if align:
            main_points[3] = str(float(comp_points[3]))
            dimens['height'] = (str(float(comp_points[3])))
        else:
            main_points[3] = str(float(comp_points[3]) + 600)
            dimens['height'] = (str(float(comp_points[3]) + 600))

    ptsString = ''
    for p in main_points:
        ptsString += p + ' '
    ptsString = ptsString[:-1]

    if align:
        transform = "scale(1 1) rotate(0) " + "translate(%s %s)" % (trans_width-600, 0)
    else:
        dimens['width'] = (str(int(remove_pt(dimens['width'])) + 600)) + 'pt'
        dimens['height'] = (str(int(remove_pt(dimens['height'])) + 600)) + 'pt'
        transform = "scale(1 1) rotate(0) " + "translate(%s %s)" % (trans_width-450, 300)
    dimens['viewBox'] = ptsString
    main_graph.set('viewBox', dimens['viewBox'])
    main_graph.set('height', dimens['height'])
    main_graph.set('width', dimens['width'])

    # Wrap all elements in main graph in Element called 'boxGraph',
    # then translate boxGraph to proper location
    g_attribs = {'class': "graph", 'id': 'trans1', 'transform': transform}
    boxGraph = Element(tag + 'g', **g_attribs)
    for e in comp_graph:
        boxGraph.append(e)

    comp_tree.write(compfile)
    main_graph.append(boxGraph)
    main_tree.write(mainfile)
    mfile.close()
    cfile.close()
    return mainfile