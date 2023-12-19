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
    def __init__(self, centerx, centery, radius) -> None:
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

    def insert(self, point: QTPoint):
        if not self._contains(point):
            return False

        if len(self.points) < self.capacity:
            self.points.append(point)
            return True

        if not self.divided:
            self._divide()

        subtrees = [self.topleft, self.topright, self.botleft, self.botright]
        for subtree in subtrees:
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
            return []

        result = list(filter(lambda p: p._in_bounds(bounds), self.points))

        if self.divided:
            subtrees = [self.topleft, self.topright, self.botleft, self.botright]
            for subtree in subtrees:
                result += subtree.query(bounds)  # type: ignore

        return result


def setup(points):
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


def find_points(tree, bounds):
    return set(map(lambda qtp: qtp.data, tree.query(bounds)))
