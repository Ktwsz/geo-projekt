from kdtree import find_points as kd_solve
import numpy as np


def generate_points(left_bound, right_bound, n):
    return np.random(low  = left_bound,
                     high = right_bound,
                     size = (n, 2))


def get_rand_bounds(left, right):
    x1, x2, y1, y2 = np.random(left, right, 4)

    if x1 > x2:
        x1, x2 = x2, x1

    if y1 > y2:
        y1, y2 = y2, y1

    return x1, x2, y1, y2


def brute(points, x1, x2, y1, y2):
    return {ix
            for ix, p in enumerate(points)
            if p[0] <= x2 and p[0] >= x1 and p[1] <= y2 and p[1] >= y1
            }


def test():
    for _ in range(100):
        left_bound, right_bound = -1000, 1000
        n = 10000
        repeat = 10

        points = generate_points(left_bound, right_bound, n)
        for rep in range(repeat):
            bounds = get_rand_bounds(left_bound, right_bound)

            solution = brute(points, *bounds)
            kd = kd_solve(points, *bounds)

            if kd == solution:
                print("OK")
            else:
                print("ERR")
                return


if __name__ == "__main__":
    test()
