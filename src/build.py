import model as Model
import minors as Minors
import sbml, layout, util, model_json, gpr
import boundary as Bnd
from xml.etree.ElementTree import *
from packing import *
import exchange_layout as Ex
import svg.path as Path

import argparse, os

DEFAULTS_JSON_FILENAME = os.path.dirname(os.path.realpath(__file__)) + "/metdraw_defaults.json"

desc = "Draw maps of metabolic reactions."
parser = argparse.ArgumentParser(description=desc,prog="metdraw")
parser.add_argument('file',
                    help="input reaction file")
parser.add_argument('--version',action="version",version="0.0.0",
                    help="show version")
parser.add_argument('--count_mets',action='store_true',dest="count_mets",
                    help="create a metabolite count file")
parser.add_argument('-M','--mets',dest="met_file",
                    help="use a metabolite count file to set minors")
parser.add_argument('--show',action='store_true',dest="show",
                    help="show model structure")
parser.add_argument('-q',dest='q',
                    help="graphviz output suppression level")
parser.add_argument('--Ln',dest='Ln',
                    help="graphviz iteration limit")
parser.add_argument('-o','--output',dest="output",
                    help="output file format")
parser.add_argument('-p','--param',dest='param',
                    help="layout parameters")
parser.add_argument('--json',action='store_true',dest='json',
                    help="output JSON objects")
parser.add_argument('--engine',dest='engine',
                    help="rendering engine used by Graphviz (fdp or sfdp)")
parser.add_argument('--norun',action='store_true',dest='norun',
                    help="do not run Graphviz")
parser.add_argument('-c','--config',dest='config',
                    help='JSON configuration file for default parameters')
parser.add_argument('--status',action='store_true',dest='status',
                    help="record status in temp file")
parser.add_argument('--dotcmd',dest='dotcmd',
                    help="DOT command")
parser.add_argument('--no_gpr',action='store_true',dest='no_gpr',
                    help="do not save gene/protein/reaction annotations")
parser.add_argument('--test',action='store_true',dest='test',
                    help="run in testing mode")


defaults = {}

def read_json_config_file(filename):
    defaults.clear()
    defaults.update(util.parse_json_file(filename))
    def to_fn(key):
        # convert a string to a lambda expression in defaults
        if key in defaults:
            defaults[key] = eval(defaults[key])
    # these two parameters are stored as strings in JSON, but should really be lambdas
    to_fn("METABOLITE_LABEL_TRANSFORM")
    to_fn("REACTION_LABEL_TRANSFORM")

# load the default configuration parameters
read_json_config_file(DEFAULTS_JSON_FILENAME)

def display_parameters(params):
    print "MetDraw Parameters:"
    for k,v in params.iteritems():
        print "   ", k, ":", str(v)

def makeModel(filename,count_mets=None,met_file=None,show=False,
              quiet=False,json=False,no_gpr=False,defaults=defaults):
    sbml_filename = filename
    if filename.endswith('.xml'):
        filename = filename[:-4]
    mets_filename = filename + '.mets'
    gpr_filename = filename + '.gpr'
    print filename

    if not quiet:
        print 'Loading model file', sbml_filename
    if filename.endswith('.json'):
        model = Model.build_model(*model_json.parse_json_file(file=sbml_filename))
    else:
        pieces = sbml.parse_sbml_file(file=sbml_filename)
        model = Model.build_model(**pieces)
        if not no_gpr:
            gpr.write_gpr_file(gpr.Gpr(pieces['reactions']),gpr_filename)
            if not quiet:
                print 'GPR written to file', gpr_filename
    model.name = filename
    model.set_param(**defaults)

    if count_mets:
        if not quiet:
            print 'Writing metabolite counts to file', filename+'.mets'
        Minors.write_met_file(Minors.count_species(model),
                              filename=mets_filename,
                              json=json)
        return

    if met_file:
        minors = Minors.read_met_file(filename=met_file)
        if not quiet:
            print len(minors), "minors loaded from file '{0}'".format(met_file)
    else:
        # find the minors in the model; for now, we create a temporary mets
        # file that is deleted after loading the minors
        temp_filename = mets_filename + '.TEMP'
        Minors.write_met_file(Minors.count_species(model),filename=temp_filename)
        minors = Minors.read_met_file(temp_filename)
        os.remove(temp_filename)
        if not quiet:
            print len(minors), "minors found in model"
    model.set_param(name="minors",value=minors)
    return model

def drawCompartment(filename, comp, show=False,engine='fdp',output='svg',
             quiet=False,q='1',Ln='1000',norun=False,dotcmd='dot',
             defaults=defaults):

    if filename.endswith('.xml'):
        filename = filename[:-4]
    dot_filename = filename + '.dot'
    output_filename = filename + '.' + output
    if show:
        comp.display()
        display_parameters(defaults)

    SHOW_EXCHANGES = comp.get_param('SHOW_EXCHANGES')

    if not quiet:
        print 'Creating reaction layout'
    g = layout.model_to_dot2(comp)

    if not quiet:
        print 'Creating DOT file', dot_filename
    g.to_file(dot_filename)

    output_filename = comp.id + output_filename

    # run graphviz
    if not quiet:
        print 'Preparing Graphviz call:'
    cmdstr = '{dot} -q{q} -Ln{Ln} -K{engine} -T{fmt} -o {outfile} {file}'
    cmd = cmdstr.format(dot=dotcmd,
                        q=q,Ln=Ln,
                        engine=engine,
                        fmt=output,
                        outfile=output_filename,
                        file=dot_filename)
    if not quiet:
        print '   ' + cmd
    if not norun:
        print 'Running Graphviz'
        error = os.system(cmd)
        if error:
            print "Error running dot:", error
    else:
        print 'ok'

    if SHOW_EXCHANGES:
        main_file = open(output_filename, "r")
        main_tree = ElementTree(file=main_file)
        main_graph = main_tree.getroot()
        main_glist = sbml.findall(main_graph, 'g')
        comps_pts = Bnd.get_compPts(main_glist)
        metabDict = Bnd.metab_dict(main_glist)
        comp_pts = comps_pts[comp.id]

        newBoxPath = Bnd.gen_membrane_path(comp_pts)
        memBoxStart = Bnd.parse_path(newBoxPath)

        pp = PolyPacker(comp_pts)
        line_len = Line(0+0j, 0+150j).length() # default 150 buffer

        pp.pack(line_len, near=comp_pts[0])
        pp.pack(line_len, near=comp_pts[1])
        pp.pack(line_len, near=comp_pts[2])
        pp.pack(line_len, near=comp_pts[3])

        leftLine = Line(comp_pts[0], comp_pts[1]) # creates the line
        bottomLine = Line(comp_pts[1], comp_pts[2])
        rightLine = Line(comp_pts[2], comp_pts[3])
        topLine = Line(comp_pts[3], comp_pts[0])

        top_mid = topLine.point(.5)
        # pp.pack(700.0, near=top_mid) # to avoid packing over compartment label

        memBoxStart_x = memBoxStart.point(0).real
        memBoxStart_y = memBoxStart.point(0).imag

        for rxn in comp.exchanges:
            if (len(rxn.reactants) + len(rxn.products)) > 20:
                continue # to avoid placing biomass reactions
            graphDot = Ex.gen_graph(rxn)
            graphDot.export_graphviz(output="svg", filename="ex", warnings=False)
            ex_file = open("ex.svg", "r")
            ex_tree = ElementTree(file=ex_file)
            graph_root = ex_tree.getroot()
            ex_graph = graph_root[0]
            width = Bnd.remove_pt(sbml.findfirst(ex_tree, 'svg').get('width'))
            ex_glist = sbml.findall(ex_graph, 'g')
            edgeList = Bnd.get_edges(ex_glist)

            for edge in edgeList:
                path = sbml.findfirst(edge, 'path')
                path.set('d', Bnd.extend_edge(path).get('d')) # smooth out edges
                if edge.get('id') == "midpoint":
                    path = sbml.findfirst(edge, 'path')
                    d = path.get('d')
                    path_end = Path.parse_path(d).point(1.0)
                    midpoint = Path.parse_path(d).point(.5)
                    path_x = path_end.real

            # solves overlapping issue where box was covering the rxns
            g = sbml.findfirst(ex_graph, 'polygon')
            g.set('fill', 'none')

            scale = "scale(1 1) "
            metabList = rxn.major_products
            if Bnd.metab_overlap(metabList, metabDict):
                name = Bnd.common_metab(metabList, metabDict)
                near = metabDict[name]
            else:
                near = Bnd.gen_point(bottomLine.point(.5).real, leftLine.point(.5).imag)

            # if Unpackable, print the comp id, then quit the loop
            try:
                pack = pp.pack(width + 8.0, near=near)
                pack_mp = pack[0].point(.5)
            except Unpackable:
                print "Unable to pack more rxns for comp " + comp.id
                break

            # Calculations for rxn translation to main graph
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

            for g in ex_glist:
                if g.get('id') == 'rxn':
                    g.set('transform', transform)

            # add rxn to main graph
            main_graph[0].append(ex_graph)
            os.remove('ex.svg')
        main_tree.write(output_filename)

    # translate the graph down and right for bounding_box()
    main_tree = ElementTree(file=output_filename)
    main_graph = main_tree.getroot()
    dimens = main_graph.attrib

    # also extend the image to make proportional
    dimens['width'] = (str(int(Bnd.remove_pt(dimens['width'])) + 600)) + 'pt'
    dimens['height'] = (str(int(Bnd.remove_pt(dimens['height'])) + 600)) + 'pt'

    n = main_graph[0]
    translate = sbml.findfirst(n,'g')
    t = translate.get('transform')
    tNums = t.split("translate(")[1].replace(')', '').split(" ")
    t1 = float(tNums[0]) + 300
    t2 = float(tNums[1]) + 300
    t = Bnd.newTransform(t1, t2)
    translate.set('transform', t)

    # change the viewbox for bounding_box()
    ptList = dimens['viewBox'].split(" ")
    ptList[2] = float(ptList[2]) + 600.0
    ptList[3] = float(ptList[3]) + 600.0

    dimens['height'] = str(ptList[3])
    dimens['viewBox'] = Bnd.newVB(ptList)
    main_graph.set('viewBox', dimens['viewBox'])
    main_graph.set('height', dimens['height'])
    main_graph.set('width', dimens['width'])

    main_tree.write(output_filename)
    return output_filename


def update_defaults(params):
    for k,v in params.iteritems():
        if k in defaults:
            if isinstance(defaults[k],dict):
                defaults[k].update(v)
            else:
                defaults[k] = v

if __name__ == '__main__':
    args = parser.parse_args()

    if args.test:
        exit(0)  # do nothing in testing mode

    metdraw_args = {}

    if args.config:
        read_json_config_file(args.config)

    if args.file:
        metdraw_args['filename'] = args.file
    if args.count_mets:
        metdraw_args['count_mets'] = args.count_mets
    if args.met_file:
        metdraw_args['met_file'] = args.met_file
    if args.show:
        metdraw_args['show'] = args.show
    if args.q:
        metdraw_args['q'] = args.q
    if args.Ln:
        metdraw_args['Ln'] = args.Ln
    if args.output:
        metdraw_args['output'] = args.output
    if args.json:
        metdraw_args['json'] = args.json
    if args.engine:
        metdraw_args['engine'] = args.engine
    if args.norun:
        metdraw_args['norun'] = args.norun
    if args.status:
        metdraw_args['status'] = args.status
    if args.dotcmd:
        metdraw_args['dotcmd'] = args.dotcmd
    if args.no_gpr:
        metdraw_args['no_gpr'] = args.gpr

    if args.param:
        params = eval('dict({0})'.format(args.param))
        update_defaults(params)

    drawCompartment(**metdraw_args)



