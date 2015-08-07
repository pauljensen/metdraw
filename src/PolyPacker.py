

from LinePacker import Unpackable
from LinePacker2D import LinePacker2D


class PolyPacker(object):
    def __init__(self, points):
        #creates multiple LinePacker2D objects from the list of points
        self.points = points
        self.n_points = len(points)
        self.lines = []
        for i in range(0, self.n_points-1):
            self.lines.append(LinePacker2D(self.points[i],
                                           self.points[i+1]))
        self.lines.append(LinePacker2D(self.points[self.n_points-1],
                                       self.points[0]))
    #Determines if a segment of a given length can fit
    #   in any of the sides of the polygon
    def canfit(self, line_len):
        return any(lp2D.canfit(line_len) for lp2D in self.lines)

    def pack(self, line_len, near=0+0j):
        if not self.canfit(line_len):
            raise Unpackable
        dists = []
        for i, lp2D in enumerate(self.lines):
            try:
                # see if the segment is packable
                pack = lp2D.pack(line_len, near, check=True)
            except Unpackable:
                pass
            else:
                # Add segment,dist to list of possible sides
                #   with corresponding index
                dists.append((pack[1], i))
        # the index in the self.lines list that has the minimum distance 
        min_index = sorted(dists, key=lambda x: x[0])[0][1]
        line, dist = self.lines[min_index].pack(line_len, near)
        return line, dist

    def __str__(self):
        pack_str = ""
        for line in self.lines:
            skeleton = ("From %s " % str(line.orig_line.point(0.0)) +
                        "to %s: " % str(line.orig_line.point(1.0)))
            pack_str = pack_str + skeleton + str(line) + "| "
        return pack_str


if __name__ == "__main__":
    poly = PolyPacker([0+0j, 0+10j, 10+10j, 10+0j])
    print poly.pack(4, 9+8j)
    print poly.pack(4, 9+8j)
    print poly.pack(4, 9+8j)
    print poly
