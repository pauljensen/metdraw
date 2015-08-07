

from LinePacker import Unpackable
from LinePacker2D import LinePacker2D


class PolyPacker(object):
    def __init__(self, points):
        self.points = points
        self.n_points = len(points)
        self.lines = []
        for i in range(0, self.n_points-1):
            self.lines.append(LinePacker2D(self.points[i],
                                           self.points[i+1]))
        self.lines.append(LinePacker2D(self.points[self.n_points-1],
                                       self.points[0]))

    def canfit(self, line_len):
        return any(lp2D.canfit(line_len) for lp2D in self.lines)

    def pack(self, line_len, near=0+0j):
        if not self.canfit(line_len):
            raise Unpackable
        dists = []
        for i, lp2D in enumerate(self.lines):
            try:
                pack = lp2D.pack(line_len, near, check=True)
            except Unpackable:
                pass
            else:
                dists.append((pack[1], i))
        min_index = sorted(dists, key=lambda x: x[0])[0][1]
        # the index in the self.lines list that has the desired LP2D object
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
