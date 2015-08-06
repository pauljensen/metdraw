

from LinePacker import LinePacker, Unpackable
from LinePacker2D import LinePacker2D

class PolyPacker(object):

    def __init__(self, points):
        self.points = points
        self.n_points = len(points)
        self.lines = []
        for i in range(0, self.n_points-1):
            self.lines.append(LinePacker2D(
                self.points[i], self.points[i+1]))
        self.lines.append(LinePacker2D(
            self.points[self.n_points-1], self.points[0]))

    def canfit(self, line_len):
        return any(lp2D.canfit(line_len) for lp2D in self.lines)

    def pack(self, line_len, near=0+0j):

        dists = []
        i = 0
        for lp2D in self.lines:
            try:
                pack = lp2D.pack(line_len, near)
            except Unpackable:
                i = i + 1
                pass
            else:
                dists.append((pack[1],i))
                i = i + 1
        min_index = sorted(dists, key=lambda x: x[0])[0][1]
        #the index in the self.lines list that has the desired LP2D object
        pass



poly = PolyPacker([0+0j, 0+10j, 10+10j, 10+0j])
print poly.pack(4, 3+8j)
