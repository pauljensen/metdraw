from svg.path import Line

class Unpackable(Exception):
    pass


class LinePacker(object):
    def __init__(self, length):
        # creates an object that packs segments into a line of a given length
        self.length = length
        self._segments = []
        self._gaps = []
        self._gaps.append((0.0, length))

    # read-only accessors for protected properties
    def get_gaps(self):
        return self._gaps

    def get_segments(self):
        return self._segments

    def canfit(self, width):
        # determines if a segment of width will fit into the line (given all
        # previously placed segments)
        if width > self.length:
            return False
        else:
            return any((gap[1] - gap[0]) >= width for gap in self._gaps)

    def pack(self, width, near=0.0, check=False):
        # Determines the optimal position of a segment to be closest to a point.
        #   "width" and "near" are both floats in (0, length).
        # Returns a 2-tuple with the segment (start, end) and the
        #   distance from the segment center to "near".
        # Raises Unpackable if segment does not fit anywhere on line.
        # If check=True it will find the best place for the
        #   segment but not actually pack it

        if not self.canfit(width):
            raise Unpackable

        half_width = width / 2.0

        # mamimum distance that could be found
        max_dist = max(abs(self.length - near), abs(near))

        def place_in_gap(gap):
            # Optimally place segment in a gap.
            # Return a 3-tuple with the segment (start, end), the distance
            #   between the segment midpoint and near, and the new gaps
            #   created by placing the segment.  If the segment doesn't fit
            #   in the gap, the first and third return values are None, and
            #   the distance is 10*max_dist.
            if gap[1] - gap[0] < width:
                # segment doesn't fit; return enormous distance
                return None, 10*max_dist, None

            if gap[0] <= near <= gap[1]:
                # near is in the segment
                if near - gap[0] <= half_width:
                    # too close to left end
                    seg = (gap[0], gap[0]+width)
                    new_gaps = [(seg[1], gap[1])]
                elif gap[1] - near <= half_width:
                    # too close to right end
                    seg = (gap[1]-width, gap[1])
                    new_gaps = [(gap[0], seg[0])]
                else:
                    seg = (near-half_width, near+half_width)
                    new_gaps = [(gap[0], seg[0]), (seg[1], gap[1])]
            elif near < gap[0]:
                # near is to the left
                seg = (gap[0], gap[0]+width)
                new_gaps = [(seg[1], gap[1])]
            else:
                # near is to the right
                seg = (gap[1]-width, gap[1])
                new_gaps = [(gap[0], seg[0])]

            dist = abs(sum(seg)/2.0 - near)
            return seg, dist, new_gaps
        placed = map(place_in_gap, self._gaps)
        arg_best_fit = min(enumerate(placed), key=lambda x: x[1][1])[0]
        if check:
            return placed[arg_best_fit][0:2]
        else:
            del self._gaps[arg_best_fit]
            segment, distance, gaps = placed[arg_best_fit]
            self._gaps += gaps
            self._segments.append(segment)
            return segment, distance

    def __str__(self):
        return ('Gaps: ' + str(sorted(self._gaps, key=lambda x: x[0])) + ', ' +
                'Segments: ' + str(sorted(self._segments, key=lambda x: x[1])))

class LinePacker2D(object):

    def __init__(self, point1, point2):
        # creates an object that packs segments
        #   into a 2D-line between two points
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
        # determines if a segment of a given length can fit
        #   given previously placed segments
        return self.t_line.canfit(line_len/self.length)

    def get_t(self, point):
        # convert a point from x,y to its nearest position on the unit line
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

    # return the list of gaps/segments
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
        #Packs a segment of a given length closest to a point on a 2D line.
        #   Returns a 2-tuple with the new segment's start and end points and
        #   the distance from "near" to the midpoint.

        # corresponding width on unit line
        width = line_len / self.length
        t = self.get_t(near)
        ts = self.t_line.pack(width, t, check=check)
        # Use unit line points (start,end) to find the corresponding
        #   points on the 2D-line, then generate the Line segment to pack
        pt1 = self.orig_line.point(ts[0][0])
        pt2 = self.orig_line.point(ts[0][1])
        new_seg = Line(pt1, pt2)
        # Generate a new line segment from the midpoint of the packed
        #   segment to "near", calculate the length to find the distance
        dist = Line(new_seg.point(.5), near).length()
        return new_seg, dist

    def __str__(self):
        return ("Gaps: " + str(self.get_gaps()) + ', ' +
                "Segments: " + str(self.get_segments()))

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
        return line, dist, min_index

    def __str__(self):
        pack_str = ""
        for line in self.lines:
            skeleton = ("From %s " % str(line.orig_line.point(0.0)) +
                        "to %s: " % str(line.orig_line.point(1.0)))
            pack_str = pack_str + skeleton + str(line) + "| "
        return pack_str

