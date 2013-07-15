#!/usr/bin/python

import model as Model
import minors as Minors
import sbml, layout

import argparse, os
import json as JSON

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

def json_unicode_to_str(obj):
    # replace all unicode strings in a JSON object with str objects
    new = {}
    for k,v in obj.items():
        new_k = str(k) if isinstance(k,unicode) else k
        if isinstance(v,unicode):
            new_v = str(v)
        elif isinstance(v,dict):
            new_v = json_unicode_to_str(v)
        else:
            new_v = v
        new[new_k] = new_v
    return new
# load the default configuration parameters
defaults = json_unicode_to_str(JSON.load(open(DEFAULTS_JSON_FILENAME)))

def to_fn(key):
    # convert a string to a lambda expression in defaults
    if key in defaults:
        defaults[key] = eval(defaults[key])
# these two parameters are stored as strings in JSON, but should really be lambdas
to_fn("METABOLITE_LABEL_TRANSFORM")
to_fn("REACTION_LABEL_TRANSFORM")


def metdraw(filename,count_mets=None,met_file=None,show=False,
            engine='fdp',output='pdf',quiet=False,q='1',Ln='1000',
            json=False,defaults=defaults):
    if not quiet:
        print 'Loading model file', filename
    model = Model.build_model(*sbml.parse_sbml_file(file=filename))
    model.name = filename
    model.set_param(**defaults)
    
    if count_mets:
        if not quiet:
            print 'Writing metabolite counts to file', filename+'.mets'
        Minors.write_met_file(Minors.count_species(model),
                              filename=filename+'.mets',
                              json=json)
        return
    
    if met_file:
        minors = Minors.read_met_file(filename=met_file)
        if not quiet:
            print len(minors), "minors loaded from file", met_file
        model.set_param(name="minors",value=minors)
        
    if show:
        model.display()
    
    if not quiet:
        print 'Creating reaction layout'
    g = layout.model_to_dot(model)
    
    if not quiet:
        print 'Creating DOT file', filename+'.dot'
    g.to_file(filename+'.dot')
    
    # run graphviz
    if not quiet:
        print 'Running GRAPHVIZ:'
    cmdstr = 'dot -q{q} -Ln{Ln} -K{engine} -T{fmt} -O {file}'
    cmd = cmdstr.format(q=q,Ln=Ln,
                        engine=engine,
                        fmt=output,
                        file=filename+'.dot')
    if not quiet:
        print '   ' + cmd
    error = os.system(cmd)
    if error:
        print "Error running dot:", error

def update_defaults(params):
    for k,v in params.iteritems():
        if k in defaults:
            if isinstance(defaults[k],dict):
                defaults[k].update(v)
            else:
                defaults[k] = v

if __name__ == '__main__':
    args = parser.parse_args()
    metdraw_args = {}
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
        
    if args.param:
        params = eval('dict({0})'.format(args.param))
        update_defaults(params)
        
        
    metdraw(**metdraw_args)
