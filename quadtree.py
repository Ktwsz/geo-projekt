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


from vis import Eraser, Point, Segment, Rect


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

        for point in self.points:
            for subtree in self._get_subtrees():
                if subtree._insert(point)[0]:  # type: ignore
                    break
        self.points = []

        self.divided = True

    def _contains(self, point: QTPoint):
        leftside = point.x >= self.centerx - self.radius
        rightside = point.x <= self.centerx + self.radius
        topside = point.y <= self.centery + self.radius
        botside = point.y >= self.centery - self.radius

        return leftside and rightside and topside and botside

    def _get_subtrees(self):
        return [self.topleft, self.topright, self.botleft, self.botright]

    def _insert(self, point: QTPoint, vis=False):
        if not self._contains(point):
            return False, []

        if not self.divided and len(self.points) < self.capacity:
            self.points.append(point)
            return True, [[Point(point.x, point.y, color="green")]]
        steps = []
        if not self.divided:
            self._divide()
            steps.append(self._get_lines())

        for subtree in self._get_subtrees():
            ok, s = subtree._insert(point, vis)  # type: ignore
            if ok:
                steps += s
                return True, steps

        return False, []

    def insert(self, x, y, ix):
        return self._insert(QTPoint(x, y, ix))

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

        if self.divided:
            result = set()
            for subtree in self._get_subtrees():
                result |= subtree.query(bounds)  # type: ignore
        else:
            result = filter(lambda p: p._in_bounds(bounds), self.points)
            result = set(map(lambda p: p.data, result))

        return result

    def visualized_query(self, bounds):
        rc = Rect(self.centerx, self.centery, self.radius, "yellow")
        steps = [[rc], [Eraser(rc)]]
        if not self._overlaps(bounds):
            return set(), steps + [
                [Rect(self.centerx, self.centery, self.radius, "red")]
            ]

        if self.divided:
            result = set()
            for subtree in self._get_subtrees():
                r, s = subtree.visualized_query(bounds)  # type: ignore
                result |= r
                steps += s
        else:
            steps += [[Rect(self.centerx, self.centery, self.radius, "green")]]
            ps = []
            for p in self.points:
                ps.append(Point(p.x, p.y, "yellow"))
            steps.append(ps)
            ps = []
            for p in self.points:
                if p._in_bounds(bounds):
                    ps.append(Point(p.x, p.y, "green"))
                else:
                    ps.append(Point(p.x, p.y, "blue"))
            steps.append(ps)
            result = filter(lambda p: p._in_bounds(bounds), self.points)
            result = set(map(lambda p: p.data, result))

        return result, steps

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

    def _get_lines(self):
        x = self.centerx
        y = self.centery
        r = self.radius
        c = [x, y]
        p1 = [x, y + r]
        p2 = [x, y - r]
        p3 = [x + r, y]
        p4 = [x - r, y]

        return [Segment(c, p1), Segment(c, p2), Segment(c, p3), Segment(c, p4)]

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
    def from_points(points, vis=False):
        maxx = max(map(lambda p: p[0], points))
        minx = min(map(lambda p: p[0], points))
        maxy = max(map(lambda p: p[1], points))
        miny = min(map(lambda p: p[1], points))

        centerx = (minx + maxx) / 2
        centery = (miny + maxy) / 2
        radius = max(abs(maxx - centerx), abs(maxy - centery)) + 10**-12

        x, y, r = centerx, centery, radius

        steps = []
        p1 = [x - r, y + r]
        p2 = [x + r, y + r]
        p3 = [x + r, y - r]
        p4 = [x - r, y - r]
        steps: list = [
            [Segment(p1, p2), Segment(p2, p3), Segment(p3, p4), Segment(p4, p1)]
        ]

        tree = QuadTree(centerx, centery, radius)
        for i, (x, y) in enumerate(points):
            steps.append([Point(x, y, "red")])
            steps += tree._insert(QTPoint(x, y, i), vis)[1]
        if not vis:
            return tree, []
        return tree, steps

    @staticmethod
    def fixed_size(points, minx, maxx, miny, maxy):
        centerx = (minx + maxx) / 2
        centery = (miny + maxy) / 2
        radius = max(abs(maxx - centerx), abs(maxy - centery))

        tree = QuadTree(centerx, centery, radius)
        for i, (x, y) in enumerate(points):
            tree._insert(QTPoint(x, y, i))

        return tree
