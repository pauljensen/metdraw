#!/usr/bin/python

import argparse
import colormap
import copy

import gpr

desc = "Color maps of metabolic reactions."
parser = argparse.ArgumentParser(description=desc,prog="metcolor")
parser.add_argument('mapfile',
                    help="input SVG map file")
parser.add_argument('datafile',
                    help="input CSV data file")
parser.add_argument('--version',action="version",version="0.0.0",
                    help="show_version")
parser.add_argument('--header',action='store_true',dest="header",
                    help="datafile begins with column headings")
parser.add_argument('--colors',dest="colors",
                    help="list of color names, e.g. ['red','white','blue']")
parser.add_argument('--breaks',dest="breaks",
                    help="numeric breaks for each color")
parser.add_argument('--default_color',dest="default_color",
                    help="default color for values outside of colormap")
parser.add_argument('--gprfile',dest="gprfile",
                    help="gene/protein/reaction associations")
parser.add_argument('--test',action='store_true',dest='test',
                    help="run in testing mode")


def metcolor(mapfile=None, datafile=None, header=False,
             colors=colormap.DEFAULT_COLORSCHEME,gprfile=None):
    mappings = colormap.csv_to_mappings(datafile,header=header)
    if gprfile:
        gprmap = gpr.read_gpr_file(gprfile)
        mappings = {k : gprmap.score_reactions(v) for k,v in mappings.items()}
    mapper = colormap.Colormapper(colors)
    mapper.range = colormap.get_range(mappings)
    svg = colormap.load_svg_image(mapfile)
    for name,data in mappings.items():
        condsvg = copy.deepcopy(svg)
        colormap.scale_reactions(condsvg,data,mapper)
        colormap.write_svg_image(condsvg,filename=mapfile[:-4]+'__'+name+'.svg')


if __name__ == '__main__':
    args = parser.parse_args()

    if args.test:
        exit(0)  # do nothing in testing mode

    metcolor_args = {}
    if args.mapfile:
        metcolor_args['mapfile'] = args.mapfile
    if args.datafile:
        metcolor_args['datafile'] = args.datafile
    if args.header:
        metcolor_args['header'] = args.header
    if args.colors:
        metcolor_args['colors'] = args.colors
    if args.breaks:
        metcolor_args['breaks'] = args.breaks
    if args.default_color:
        metcolor_args['default_color'] = args.default_color
    if args.gprfile:
        metcolor_args['gprfile'] = args.gprfile
        
    metcolor(**metcolor_args)