__author__ = 'william'

from path import *
from LinePacker import *


class Unpackable(Exception):
    pass


class LinePacker2D(object):

    def __init__(self, point1, point2):
        self.point1 = point1
        self.point2 = point2
        self.x1 = point1.real
        self.y1 = point1.imag
        self.x2 = point2.real
        self.y2 = point2.imag
        self.t_line = LinePacker(1.0)
        self.segments = []
        self.gaps = []
        self.orig_line = Line(point1, point2)
        self.length = self.orig_line.length()
        self.gaps.append(self.orig_line)

    def canfit(self, line_len):
        if line_len > self.length:
            return False
        else:
            return any((gap.length() >= line_len for gap in self.gaps))

    def get_t(self, point):
        a = point.real
        b = point.imag
        dx = self.x2 - self.x1
        dy = self.y2 - self.y1
        t = ((dx * (a - self.x1)) + (dy * (b - self.y1))) / ((dx**2) + (dy**2))
        if t > 1.0:
            return 1.0
        elif t < 0.0:
            return 0.0
        else:
            return t

    def bad_gaps(self, tgaps):
        self.gaps = []
        for gap in tgaps:
            first = gap[0]
            sec = gap[1]
            pt1 = self.orig_line.point(first)
            pt2 = self.orig_line.point(sec)
            line = Line(pt1, pt2)
            self.gaps.append(line)
        return self.gaps

    def pack(self, line_len, near):
        if not self.canfit(line_len):
            raise Unpackable
        else:
            width = line_len / self.length
            t = self.get_t(near)
            ts = self.t_line.pack(width, t)[0]
            pt1 = self.orig_line.point(ts[0])
            pt2 = self.orig_line.point(ts[1])
            new_seg = Line(pt1, pt2)
            self.segments.append(new_seg)
            self.bad_gaps(self.t_line.gaps)
            return new_seg

    def __str__(self):
        return "Gaps: " + str(self.gaps) + ',' + "Segments: " + str(self.segments)

line = LinePacker2D(100+10j, 150+25j)
print line.gaps
print line.pack(10.0, 115.0+10j)
print line.pack(2.0, 125+17.5j)
print line



