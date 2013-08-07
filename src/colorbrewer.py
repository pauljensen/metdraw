
from colorschemes import colorschemes

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


if __name__ == '__main__':
    print get_colorscheme_names()