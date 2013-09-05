
import xml.etree.ElementTree as etree
import csv
import math

from colorschemes import colorschemes


DEFAULT_COLORSCHEME = 'RdBu(3)'

UNLABELED_COLOR = "rgb(220,220,220)"


# -------------- working with SVG image maps -------------------

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
    
    for g in findall(svg,'g'):
        fullname = g.get("id",None)
        if is_reaction(fullname):
            name = get_name(fullname)
            if name in valuemap:
                color = colormap.value_to_color(valuemap[name])
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


# -------------- working with data files -------------------

def csv_to_mappings(filename,header=False):
    # Returns a dict where each key is the column name
    # and each value is a dict of name:value pairs.
    # If no header is provided, the column names are
    # "1", "2", ... "n".
    mappings = []
    f = open(filename,"r")
    n = None
    names = None
    found_header = False
    for r in csv.reader(f):
        if header and not found_header:
            names = r[1:]
            found_header = True
            continue
        if n is None:
            n = len(r[1:])
            mappings = [dict() for i in range(n)]
        for i,mp in enumerate(mappings):
            mp[r[0]] = float(r[i+1])
    if names is None:
        names = [str(i+1) for i in range(n)]
    return dict(zip(names,mappings))

def get_range(data):
    # returns global (min,max) from a data file structure
    # returned by csv_to_mappings
    mins = [min(v.values()) for v in data.values()]
    maxs = [max(v.values()) for v in data.values()]
    return min(mins), max(maxs)


# -------------- colorscheme names & parsing -------------------

def get_colorscheme_names():
    def get_name(name):
        scheme = colorschemes[name]
        crange = min(scheme.keys()), max(scheme.keys())
        return "{name} ({min}..{max})".format(name=name,min=crange[0],max=crange[1])
    return sorted([get_name(name) for name in colorschemes.keys()])

def get_colorscheme(name):
    # examples of allowable names:
    #   RdBu
    #   RdBu(3)
    #   RdBu (3)

    # parse name
    name = name.rstrip()
    if '(' in name:
        name,_,divisions = name.partition('(')
        name = name.rstrip()
        divisions = int(divisions.rstrip()[:-1])
    else:
        divisions = None

    if name not in colorschemes:
        raise Exception('colorscheme not found')
    if divisions is None:
        divisions = min(colorschemes[name].keys())
    return colorschemes[name][divisions]


# -------------- Mapping colors to RGB values -------------------

class Colormapper(object):
    def __init__(self,colorscheme):
        self.colorscheme = colorscheme
        self.rgbs = get_colorscheme(colorscheme)
        self.ndiv = len(self.rgbs)
        self.min, self.max = (0,1)

    @property
    def range(self):
        return self.min, self.max
    @range.setter
    def range(self,value):
        self.min, self.max = value

    def value_to_rgb(self,value):
        width = self.max - self.min
        if abs(width) < 1e-10:
            # min == max; everything will scale to zero
            width = 1
        x = (value - self.min) / width * (self.ndiv - 1)  # rescale x to 0 .. n-1
        dist = x - math.floor(x)  # distance into the interval
        lower = self.rgbs[int(math.floor(x))]  # lower RGB bounds
        upper = self.rgbs[int(math.ceil(x))]   # upper RGB bounds
        return [int(l+dist*(u-l)) for l,u in zip(lower,upper)]

    def value_to_color(self,value):
        return "rgb({0},{1},{2})".format(*self.value_to_rgb(value))
