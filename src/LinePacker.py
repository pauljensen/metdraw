
class Unpackable(Exception):
    pass


class LinePacker(object):
    def __init__(self, length):
        # creates an object that packs segments into a line of a given length
        self.length = length
        self._segments = []
        self._gaps = []
        self._gaps.append((0.0,length))

    def canfit(self, width):
        # determines if a segment of width will fit into the line (given all
        # previously placed segments)
        if width > self.length:
            return False
        else:
            return any((gap[1] - gap[0]) >= width for gap in self._gaps)

    def pack(self, width, near=0.0):
        # Determines the optimal position of a segment to be closest to a point.
        #   "width" and "near" are both floats in (0, length).
        # Returns a 2-tuple with the segment (start, end) and the
        #   distance from the segment center to "near".
        # Raises Unpackable if segment does not fit anywhere on line.

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
        del self._gaps[arg_best_fit]
        segment, distance, gaps = placed[arg_best_fit]
        self._gaps += gaps
        self._segments.append(segment)
        return segment, distance
  
    def __str__(self):
        return ('Gaps: ' + str(sorted(self._gaps, key=lambda x: x[0])) + ', ' +
                'Segments: ' + str(sorted(self._segments, key=lambda x: x[1])))


if __name__ == "__main__":
    lp = LinePacker(100)
    lp.pack(10, 50)
    print str(lp)
    lp.pack(10, 50)
    print str(lp)
    lp.pack(10, 50)
    print str(lp)
