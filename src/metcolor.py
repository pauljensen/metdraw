#!/usr/bin/python

import argparse
import colormap

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

def metcolor(mapfile=None,datafile=None,header=False,
             colors=colormap.DEFAULT_MAP):
    mappings = colormap.csv_to_mappings(datafile,header=header)
    mappings,bounds = colormap.rescale_mappings(mappings)
    mapper = colormap.create_colormap(colors)
    n_cond = len(mappings[mappings.keys()[0]])
    for i in range(n_cond):
        value_map = colormap.mapping_from_mappings(mappings,i)
        svg = colormap.load_svg_image(mapfile)
        colormap.scale_reactions(svg,value_map,mapper)
        colormap.write_svg_image(svg,filename=str(i+1)+'_'+mapfile)

if __name__ == '__main__':
    args = parser.parse_args()
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
        
    metcolor(**metcolor_args)