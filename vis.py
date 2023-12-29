from matplotlib.patches import Rectangle


class Point:
    def __init__(self, x, y, color="blue"):
        self.x = x
        self.y = y
        self.color = color

    def draw(self, ax):
        return ax.plot(
            [self.x], [self.y], marker="o", markersize=5, color=self.color, zorder=1
        )[0]


class Segment:
    def __init__(self, p1, p2, color="black"):
        self.p1 = p1
        self.p2 = p2
        self.color = color

    def draw(self, ax):
        xs = [self.p1[0], self.p2[0]]
        ys = [self.p1[1], self.p2[1]]
        return ax.plot(xs, ys, color=self.color)[0]


class Rect:
    def __init__(self, x, y, r, color) -> None:
        self.p = (x - r, y - r)
        self.s = 2 * r
        self.color = color

    def draw(self, ax):
        self.obj = ax.add_patch(
            Rectangle(self.p, self.s, self.s, color=self.color, alpha=0.5)
        )
        return self.obj

    def remove(self):
        self.obj.remove()


class Eraser:
    def __init__(self, obj):
        self.obj = obj

    def draw(self, ax):
        self.obj.remove()
        return None
