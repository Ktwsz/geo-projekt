from kdtree import KDTree
from quadtree import QuadTree
import numpy as np


def generate_points(left_bound, right_bound, n):
    return [
        (x, y)
        for x, y in np.random.uniform(low=left_bound, high=right_bound, size=(n, 2))
    ]


def get_rand_bounds(left, right):
    x1, x2, y1, y2 = np.random.uniform(left, right, 4)

    if x1 > x2:
        x1, x2 = x2, x1

    if y1 > y2:
        y1, y2 = y2, y1

    return ((x1, x2), (y1, y2))


def brute(points, bounds):
    ((x1, x2), (y1, y2)) = bounds

    return {
        ix
        for ix, p in enumerate(points)
        if p[0] <= x2 and p[0] >= x1 and p[1] <= y2 and p[1] >= y1
    }


def test():
    for _ in range(100):
        left_bound, right_bound = -1000, 1000
        n = 1000
        repeat = 1000

        points = generate_points(left_bound, right_bound, n)
        kdtree = KDTree(points)
        qtree = QuadTree.from_points(points)

        for _ in range(repeat):
            bounds = get_rand_bounds(left_bound, right_bound)

            solution = brute(points, bounds)
            kd = kdtree.query(bounds)
            qt = qtree.query(bounds)

            if kd == solution:
                print("KD OK")
            else:
                print("KD ERR")
                return
            if qt == solution:
                print("QT OK")
            else:
                print("QT ERR")
                return


if __name__ == "__main__":
    test()
