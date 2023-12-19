class QTPoint:
    def __init__(self, x, y, data=None) -> None:
        self.x = x
        self.y = y
        self.data = data

    def _in_bounds(self, bounds):
        leftbound = bounds[0][0]
        rightbound = bounds[0][1]
        botbound = bounds[1][0]
        topbound = bounds[1][1]

        return (
            self.x >= leftbound
            and self.x <= rightbound
            and self.y <= topbound
            and self.y >= botbound
        )


class QuadTree:
    def __init__(self, centerx, centery, radius):
        self.centerx = centerx
        self.centery = centery
        self.radius = radius

        self.capacity = 4
        self.points: list[QTPoint] = []

        self.topleft = None
        self.topright = None
        self.botleft = None
        self.botright = None

        self.subtrees = []

        self.divided = False

        self.drawn_objects = []

    def _divide(self):
        newrad = self.radius / 2
        x = self.centerx
        y = self.centery

        self.topleft = QuadTree(x - newrad, y + newrad, newrad)
        self.topright = QuadTree(x + newrad, y + newrad, newrad)
        self.botleft = QuadTree(x - newrad, y - newrad, newrad)
        self.botright = QuadTree(x + newrad, y - newrad, newrad)

        self.divided = True

    def _contains(self, point: QTPoint):
        leftside = point.x >= self.centerx - self.radius
        rightside = point.x <= self.centerx + self.radius
        topside = point.y <= self.centery + self.radius
        botside = point.y >= self.centery - self.radius

        return leftside and rightside and topside and botside

    def _get_subtrees(self):
        return [self.topleft, self.topright, self.botleft, self.botright]

    def insert(self, point: QTPoint):
        if not self._contains(point):
            return False

        if len(self.points) < self.capacity:
            self.points.append(point)
            return True

        if not self.divided:
            self._divide()

        for subtree in self._get_subtrees():
            if subtree.insert(point):  # type: ignore
                return True

        return False

    def _overlaps(self, bounds):
        leftbound = bounds[0][0]
        rightbound = bounds[0][1]
        botbound = bounds[1][0]
        topbound = bounds[1][1]

        x = self.centerx
        y = self.centery
        r = self.radius

        not_overlaps = (
            leftbound > x + r
            or rightbound < x - r
            or botbound > y + r
            or topbound < y - r
        )

        return not not_overlaps

    def query(self, bounds):
        if not self._overlaps(bounds):
            return set()

        result = filter(lambda p: p._in_bounds(bounds), self.points)
        result = set(map(lambda p: p.data, result))

        if self.divided:
            for subtree in self._get_subtrees():
                result |= subtree.query(bounds)  # type: ignore

        return result

    def _draw_segment(self, ax, p1, p2):
        xs = [p1[0], p2[0]]
        ys = [p1[1], p2[1]]
        return [ax.plot(xs, ys, color="black")[0]]

    def _draw(self, ax):
        x = self.centerx
        y = self.centery
        r = self.radius
        c = [x, y]
        p1 = [x, y + r]
        p2 = [x, y - r]
        p3 = [x + r, y]
        p4 = [x - r, y]

        ds = []

        if self.divided:
            ds += self._draw_segment(ax, c, p1)
            ds += self._draw_segment(ax, c, p2)
            ds += self._draw_segment(ax, c, p3)
            ds += self._draw_segment(ax, c, p4)

            for subtree in self._get_subtrees():
                ds += subtree._draw(ax)  # type: ignore
        return ds

    def draw(self, ax):
        x = self.centerx
        y = self.centery
        r = self.radius
        p1 = [x - r, y + r]
        p2 = [x + r, y + r]
        p3 = [x + r, y - r]
        p4 = [x - r, y - r]

        ds = []

        ds += self._draw_segment(ax, p1, p2)
        ds += self._draw_segment(ax, p2, p3)
        ds += self._draw_segment(ax, p3, p4)
        ds += self._draw_segment(ax, p4, p1)

        return self._draw(ax) + ds

    @staticmethod
    def from_points(points):
        maxx = max(map(lambda p: p[0], points))
        minx = min(map(lambda p: p[0], points))
        maxy = max(map(lambda p: p[1], points))
        miny = min(map(lambda p: p[1], points))

        centerx = (minx + maxx) / 2
        centery = (miny + maxy) / 2
        radius = max(maxx - centerx, maxy - centery) + 10**-12

        tree = QuadTree(centerx, centery, radius)
        for i, (x, y) in enumerate(points):
            tree.insert(QTPoint(x, y, i))

        return tree
