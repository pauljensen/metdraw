#!/usr/bin/python

import model as Model
import minors as Minors
import sbml, layout, util, model_json, gpr

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

def metdraw(filename,count_mets=None,met_file=None,show=False,
            engine='fdp',output='svg',quiet=False,q='1',Ln='1000',
            json=False,norun=False,status=False,dotcmd='dot',no_gpr=False,
            defaults=defaults):

    sbml_filename = filename
    if filename.endswith('.xml'):
        filename = filename[:-4]
    dot_filename = filename + '.dot'
    mets_filename = filename + '.mets'
    gpr_filename = filename + '.gpr'
    output_filename = filename + '.' + output

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
        
    if show:
        model.display()
        display_parameters(defaults)
    
    if not quiet:
        print 'Creating reaction layout'
    g = layout.model_to_dot(model)
    
    if not quiet:
        print 'Creating DOT file', dot_filename
    g.to_file(dot_filename)
    
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

    # clean up intermediate DOT file
    os.remove(dot_filename)


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

    metdraw(**metdraw_args)
