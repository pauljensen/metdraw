from __future__ import division

import xml.etree.ElementTree as etree
import csv


def floordiv(num,by):
    return (int(num // by), num % by)

# TODO:  change to dict
Black   = (0,0,0)
White   = (1,1,1)
Red     = (1,0,0)
Green   = (0,1,0)
Blue    = (0,0,1)
Yellow  = (1,1,0)
Cyan    = (0,1,1)
Magenta = (1,0,1)

DEFAULT_MAP = (Blue,White,Red)

UNLABELED_COLOR = "rgb(220,220,220)"

def create_colormap(colors):
    n_colors = len(colors)
    interval_width = 1.0 / (n_colors - 1)
    
    def to_rgb_str(normval):
        # find which interval normval is in
        n,rem = floordiv(normval,interval_width)
        left = colors[n]
        if rem > 1e-5:
            right = colors[n+1]
        else:
            right = colors[n]
        diff = [r - l for l,r in zip(left,right)]
        rgbs = tuple([int(255*(l + rem*d)) for l,d in zip(left,diff)])
        return "rgb({0},{1},{2})".format(rgbs[0],rgbs[1],rgbs[2])
    return to_rgb_str

def load_svg_image(filename):
    return etree.ElementTree(file=filename)

def is_reaction(fullname):
    return len(fullname) >= 1 and fullname[0] == "$"

def get_name(fullname):
    name,_,_ = fullname[1:].partition("::")
    return name

def scale_reactions(svg,valuemap,colormap):
    def tagmatch(elem,tag):
        return elem.tag.endswith('}' + tag)

    def findall(elem,tag):
        return [e for e in elem.getiterator() if tagmatch(e,tag)]
    
    def findfirst(elem,tag):
        alltags = findall(elem,tag)
        if alltags:
            return alltags[0]
        else:
            return None
    
    #for g in svg.findall('ns0:g'):
    for g in findall(svg,'g'):
        fullname = g.get("id",None)
        if is_reaction(fullname):
            name = get_name(fullname)
            if name in valuemap:
                color = colormap(valuemap[name])
            else:
                color = UNLABELED_COLOR
            path = findfirst(g,"path")
            path.set("stroke",color)
            path.set("style","fill:none;stroke-width:8")
            for node in findall(g,"polygon"):
                node.set("stroke",color)
                node.set("fill",color)
                node.set("style","")
            
def write_svg_image(svg,filename):
    svg.write(filename)

def csv_to_mappings(filename,header=False):
    mappings = {}
    f = open(filename,"r")
    if header:
        f.next()
    for r in csv.reader(f):
        mappings[r[0]] = [float(i) for i in r[1:]]
    return mappings

def rescale_mappings(mappings):
    gmax = max([max(x) for x in mappings.values()])
    gmin = min([min(x) for x in mappings.values()])
    for k,v in mappings.iteritems():
        mappings[k] = [(x - gmin) / (gmax - gmin) for x in v]
    return mappings,(gmin,gmax)

def mapping_from_mappings(mappings,i):
    mapping = {}
    for k,v in mappings.iteritems():
        mapping[k] = v[i]
    return mapping

if __name__ == '__main__':
    mappings = csv_to_mappings("../../../work/bsu/becky/normalized_rxn_expression.csv")
    mapper = create_colormap([Blue,White,Red])
    for i in range(24):
        value_map = mapping_from_mappings(mappings,i)
        svg = load_svg_image("../../../work/bsu/test/neato (copy)/STRIPPED.svg")
        scale_reactions(svg,value_map,mapper)
        write_svg_image(svg,filename="../../../work/bsu/test/neato (copy)/condition{0}.svg".format(i+1))
        print i
    
    
