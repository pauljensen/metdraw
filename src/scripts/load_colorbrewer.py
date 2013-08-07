
from collections import defaultdict
import pprint

colorschemes = defaultdict(dict)

def get_rgbs(cols):
    return [int(x) for x in cols[6:9]]

f = open('ColorBrewer_all_schemes_RGBonly3.csv')
f.readline()  # remove header
while True:
    cols = f.readline().split(',')
    if cols[0] == 'end':
        break
    n = int(cols[1])
    col_list = [cols]
    for i in range(n-1):
        col_list.append(f.readline().split(','))
    rgbs = [get_rgbs(x) for x in col_list]
    colorschemes[cols[0]][n] = rgbs

print "colorschemes = " + pprint.pformat(dict(colorschemes))