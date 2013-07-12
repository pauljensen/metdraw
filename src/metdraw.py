#!/usr/bin/python

import model as Model
import minors as Minors
import sbml, layout

import argparse, os

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

defaults = dict(
    COMPARTMENT_FONTSIZE = 128,
    SUBSYSTEM_FONTSIZE = 64,
    CLUSTER_SUBSYSTEMS = False,
    SUBSYSTEM_BORDER_STYLE = 'solid',
    CLONE_LEVEL = 8,
    LINK_CLONES = False,
    CLONE_LINK_ATTRS = dict(weight=0.000001,
                            color="lightcoral",
                            style="dashed",
                            penwidth=1,
                            len=1.0),

    INVISIBLE_NODE_ATTRS = dict(label="",
                                shape="point",
                                width=0,
                                color="transparent"),

    EDGE_ATTRS = dict(color="purple",
                      fontcolor="grey",
                      fontsize=12,
                      penwidth=8),

    MET_ATTRS = dict(color="darkorange4",
                     style="filled",
                     fillcolor="orange",
                     fontsize=12,
                     width=0.35,
                     fixedsize="true",
                     shape="circle"),
    
    MINOR_MET_ATTRS = dict(color="darkorange4",
                          style="filled",
                          fillcolor="orange",
                          fontsize=10,
                          width=0.2,
                          fixedsize="true",
                          shape="circle"),
                
    CLUSTER_MINORS = False,
    #ADD_MINOR_LINKS = False,
    #ADD_MAJOR_LINKS = False,
    SHOW_MINORS = True,
    SHOW_EXCHANGES = False,
    MAX_MINORS = 1000,
    COMPACT = False,
    #FORCE_LABELS = True,
    
    METABOLITE_LABEL_TRANSFORM = lambda x: x,
    REACTION_LABEL_TRANSFORM = lambda x: x
)

def metdraw(filename,count_mets=None,met_file=None,show=False,
            engine='fdp',output='pdf',quiet=False,q='1',Ln='1000',
            defaults=defaults):
    if not quiet:
        print 'Loading model file', filename
    model = Model.build_model(*sbml.parse_sbml_file(file=filename))
    model.name = filename
    model.set_param(**defaults)
    
    if count_mets:
        if not quiet:
            print 'Writing metabolite counts to file', filename+'.mets'
        Minors.write_met_file(Minors.count_species(model),
                              filename=filename+'.mets')
    
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
        
    if args.param:
        params = eval('dict({0})'.format(args.param))
        update_defaults(params)
        
        
    metdraw(**metdraw_args)
