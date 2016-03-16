
import os

class Attr(object):
    def __init__(self,attr={},**kwargs):
        self.attr = attr.copy()
        self.attr.update(kwargs)
        
    @staticmethod
    def make_keyval_str(keyvals,sep=";",braces=False):
        if len(keyvals) > 0:
            pairs = [key+'="'+str(val)+'"' for key,val in keyvals.items()]                             
            if braces:
                return "[{0}]".format(sep.join(pairs))
            else:
                return sep.join(pairs)
        else:
            return ""
    
    def set_attr(self,**kwargs):
        self.attr.update(kwargs)
        
    def get_attr(self,attr):
        return self.attr.get(attr,None)
    
    def has_attr(self,attr):
        return attr in self.attr
    
    def remove_attr(self,attr):
        if attr in self.attr:
            del self.attr[attr]
        
    @property
    def attr_str(self):
        return Attr.make_keyval_str(self.attr,sep=",",braces=True)
    
    def __str__(self):
        return Attr.make_keyval_str(self.attr)


class AttrStmt(Attr):
    def __init__(self,kind,**kwargs):
        Attr.__init__(self,**kwargs)
        self.kind = kind
    
    def tag(self,value):
        pass
    
    def __str__(self):
        attr_str = self.attr_str
        if attr_str == "":
            return ""
        else:
            return "{0} {1}".format(self.kind,self.attr_str)
        
    def to_string(self,indent=''):
        return indent + str(self)


class Node(Attr):
    def __init__(self,name,taggable=True,**kwargs):
        Attr.__init__(self,**kwargs)
        self.name = name
        self.taggable = taggable
    
    def tag(self,value):
        if self.taggable:
            self.name += value
    
    def __str__(self):
        return '"{0}" {1}'.format(self.name,self.attr_str)
    
    def to_string(self,indent=''):
        return indent + str(self)

  
class Edge(Attr):
    def __init__(self,tail,head,directed=False,taggable=True,**kwargs):
        Attr.__init__(self,**kwargs)
        self.tail = tail
        self.head = head
        self.directed = directed
        self.taggable = taggable
        
    @property
    def name(self):
        self.get_attr("name")

    @name.setter
    def name(self,value):
        self.set_attr(name=value)
    
    def tag(self,value):
        if self.taggable:
            self.tail += value
            self.head += value
    
    def __str__(self):
        sep = "->" if self.directed else "--"
        return '"{0}" {1} "{2}" {3}'.format(self.tail,
                                            sep,
                                            self.head,
                                            self.attr_str)
        
    def to_string(self,indent=''):
        return indent + str(self)

class Graph(object):
    def __init__(self,name=None,directed=False,subgraph=False,
                      strict=False,statements=[],cluster=False):
        self.strict = strict
        self.directed = directed
        self.subgraph = subgraph
        self.cluster = cluster
        self.name = name
        self.statements = []
        self.statements.extend(statements)
        
    def add(self,statements):
        if type(statements) is list:
            self.statements.extend(statements)
        else:
            self.statements.append(statements)
    
    def tag(self,value):
        self.name += value
        for statement in self.statements:
            statement.tag(value)
    
    def __str__(self):
        return self.to_string()

    def to_string(self,indent=''):
        if self.subgraph:
            fmt = 'subgraph "{name}" {{'
        elif self.directed:
            fmt = 'digraph "{name}" {{'
        else:
            fmt = 'graph "{name}" {{'
        if self.strict:
            fmt += 'strict '
        name = self.name if not self.cluster else ('cluster_' + self.name)
        strings = [indent + fmt.format(name=name)]
        for stmt in self.statements:
            strings.append(stmt.to_string(indent+'   '))
        strings.append(indent+"}\n")
        return "\n".join(strings)

    def to_file(self,filename):
        f = open(filename,'w')
        f.write(self.to_string())
    
    def export_graphviz(self,engine="dot",output="dot",filename=None,
                             clean=True,options=""):
        if filename is None:
            if self.name is None:
                filename = "out.dot"
            else:
                filename = self.name + ".dot"
        self.to_file(filename)
        
        if output == "dot":
            dot_cmd_str = 'dot {0} -K{1} -T{2} "{3}" > "{3}.TEMP"'
            dot_cmd = dot_cmd_str.format(options,engine,output,filename)
            dot_error = os.system(dot_cmd)
            sed_cmd_str = 'sed \':a;N;$!ba;s/\\\\\\n//g\' < "{0}.TEMP" > "{0}"'
            sed_cmd = sed_cmd_str.format(filename)
            sed_error = os.system(sed_cmd)
        else:
            dot_cmd_str = 'dot {0} -K{1} -T{2} -O "{3}"'
            dot_cmd = dot_cmd_str.format(options,engine,output,filename)
            dot_error = os.system(dot_cmd)
            sed_error = None
        
        if dot_error or sed_error:
            print dot_error, sed_error
            
        if clean:
            os.remove(filename)
            if output == "dot":
                os.remove(filename+".TEMP")
    
    def route_edges(self,**kwargs):
        return self.run_graphviz(engine="neato",options="-s -n2",**kwargs)


if __name__ == '__main__':
    g = Graph(name='g')
    g.add(Edge('a','b'))
    g.add(AttrStmt('edge',orange="true"))
    print str(g)
    g.tag('::1')
    print str(g)
    
    

