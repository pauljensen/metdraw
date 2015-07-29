
class LinePacker(object):

    def __init__(self, length):
        # creates an object that packs segments into a line of a given length
        self.length = length
        self.segments = []
        self.gaps = []
        self.gaps.append((0.0,length))

    def canfit(self, width):
        # determines if a segment of width will fit into the line (given all previously placed segments)
        if width > self.length:
            return False
        else:
            return any((gap[1] - gap[0]) >= width for gap in self.gaps)

    def gap_dist(self, poss_gaps, near):
        gap_dist = []
        for poss_gap in poss_gaps:
            if abs(poss_gap[0] - near) > abs(poss_gap[1] - near):
                gap_dist.append(poss_gap + (abs(poss_gap[1] - near),))
            else:
                gap_dist.append(poss_gap + (abs(poss_gap[0] - near),))
        return gap_dist

    def pack(self, width, near):
        # determines the optimal position of a segment to be closest to a point.
        # "width" and "near" are both floats in (0, length).
        # returns a 3-tuple with the segment start-point, endpoint, and the distance from the segment center to "near".
        # "near" should be optional with a sensible default
        #
        # I suggest you do most of the work with two properties, a list of tuples representing the "segments" and "gaps".
        # To place a segment, find the minimum distance that can be achieved by placing the segments into each gap (in
        # which it fits).  After finding the minimum distance, add the segment to the list of segments and split the gap
        # to two smaller gaps (on the left and right sides).  Initialize the object by creating an empty list of segments
        # and a single gap spanning the entire line.
        #
        # I also suggest starting the pack method by checking with canfit, which simply checks whether the segment fits
        # anywhere, regardless of the distance to "near".  This will simplify your assumptions.
        if self.canfit(width):
            half_width = width/2.0
            poss_gaps = []
            for gap in self.gaps:
                if gap[1] - gap[0] > width:
                    poss_gaps.append(gap)
            for poss_gap in poss_gaps:
                if poss_gap[0] <= near <= poss_gap[1]:
                    if near - half_width >= poss_gap[0] and near + half_width <= poss_gap[1]:
                        seg_start = near - half_width
                        seg_end = near + half_width
                        seg = (seg_start, seg_end)
                    else:
                        if near - half_width < poss_gap[0]:
                            len_move = poss_gap[0] - near + half_width
                            seg = (near - half_width + len_move, near + half_width + len_move)
                        elif near + half_width > poss_gap[1]:
                            len_move = near + half_width - poss_gap[1]
                            seg = (near - half_width - len_move, near + half_width - len_move)
                    self.segments.append(seg)
                    self.gaps.remove(poss_gap)
                    if not poss_gap[0] == seg[0]:
                        left_gap = (poss_gap[0], seg[0])
                        self.gaps.append(left_gap)
                    if not seg[1] == poss_gap[1]:
                        right_gap = (seg[1], poss_gap[1])
                        self.gaps.append(right_gap)
                    return seg + (abs(near-((seg[0] + seg[1]) /2.0)),)
                else:
                    new_poss_gaps = sorted(self.gap_dist(poss_gaps, near), key=lambda x: x[2])
                    len_move = new_poss_gaps[0][2]
                    best_gap = new_poss_gaps[0][0:2]
                    if abs(near - best_gap[0]) > abs(near - best_gap[1]):
                        seg = (best_gap[1] - width, best_gap[1])
                    else:
                        seg = (best_gap[0], best_gap[0] + width)
                    self.segments.append(seg)
                    self.gaps.remove(best_gap)
                    if not best_gap[0] == seg[0]:
                        left_gap = (best_gap[0], seg[0])
                        self.gaps.append(left_gap)
                    if not seg[1] == best_gap[1]:
                        right_gap = (seg[1], best_gap[1])
                        self.gaps.append(right_gap)
                    return seg + (abs(near-((seg[0] + seg[1]) / 2.0)),)
        else:
            return "This segment doesn't fit"
  
    def __str__(self):
        # a helpful string representation that lists the packed segments
        return 'Gaps: ' + str(sorted(self.gaps, key=lambda x: x[0])) + ', ' + 'Segments: ' + str(sorted(self.segments, key=lambda x: x[1]))



