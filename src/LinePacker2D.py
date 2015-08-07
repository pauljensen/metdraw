

from svg.path import Line
from LinePacker import LinePacker


class LinePacker2D(object):

    def __init__(self, point1, point2):
        self.point1 = point1
        self.point2 = point2
        self.x1 = point1.real
        self.y1 = point1.imag
        self.x2 = point2.real
        self.y2 = point2.imag
        self.t_line = LinePacker(1.0)
        self.orig_line = Line(point1, point2)
        self.length = self.orig_line.length()

    def canfit(self, line_len):
        return self.t_line.canfit(line_len/self.length)

    def get_t(self, point):
        a = point.real
        b = point.imag
        dx = self.x2 - self.x1
        dy = self.y2 - self.y1
        t = ((dx * (a - self.x1)) + (dy * (b - self.y1))) / \
            ((dx**2) + (dy**2))
        if t > 1.0:
            return 1.0
        elif t < 0.0:
            return 0.0
        else:
            return t

    def get_gaps(self):
        gap_list = []
        for gap in self.t_line.get_gaps():
            gap_list.append(Line(self.orig_line.point(gap[0]),
                                 self.orig_line.point(gap[1])))
        return gap_list

    def get_segments(self):
        seg_list = []
        for seg in self.t_line.get_segments():
            seg_list.append(Line(self.orig_line.point(seg[0]),
                                 self.orig_line.point(seg[1])))
        return seg_list

    def pack(self, line_len, near=0+0j, check=False):
        width = line_len / self.length
        t = self.get_t(near)
        ts = self.t_line.pack(width, t, check=check)
        pt1 = self.orig_line.point(ts[0][0])
        pt2 = self.orig_line.point(ts[0][1])
        new_seg = Line(pt1, pt2)
        dist = Line(new_seg.point(.5), near).length()
        return new_seg, dist

    def __str__(self):
        return ("Gaps: " + str(self.get_gaps()) + ', ' +
                "Segments: " + str(self.get_segments()))

if __name__ == "__main__":
    lp2D = LinePacker2D(100+10j, 150+25j)
    lp2D.pack(10.0, 100+10j)
    print lp2D
    lp2D.pack(15.0, 100+10j)
    print lp2D
    lp2D.pack(25.0, 150+25j)
    print lp2D



