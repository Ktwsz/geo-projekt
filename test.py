from kdtree import KDTree
from quadtree import QuadTree
import numpy as np
from time import process_time


TIME_DF_DIR = "./time.csv"


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


def add_time(time_df, func, row, *func_args):
    timer_start = process_time()
    res = func(*func_args)
    timer_stop = process_time()

    row["time"] = timer_stop - timer_start
    time_df.loc[len(time_df)] = row

    return res


def test(timer=False):
    time_df = None if not timer else pd.DataFrame(columns=["time", "tree", "n"])
    for _ in range(100):
        left_bound, right_bound = -1000, 1000
        n = 10000
        repeat = 100

        points = generate_points(left_bound, right_bound, n)

        kdtree = (
            KDTree(points)
            if not timer
            else add_time(time_df, KDTree, {"tree": "kd_tree", "n": n}, points)
        )

        qtree = (
            QuadTree.from_points(points)
            if not timer
            else add_time(
                time_df,
                QuadTree.from_points,
                {"tree": "qt_tree", "n": n},
                points,
            )
        )

        for _ in range(repeat):
            bounds = get_rand_bounds(left_bound, right_bound)

            solution = (
                brute(points, bounds)
                if not timer
                else add_time(
                    time_df,
                    brute,
                    {"tree": "brute", "func": "query", "n": n},
                    points,
                    bounds,
                )
            )

            kd = (
                kdtree.query(bounds)
                if not timer
                else add_time(
                    time_df,
                    kdtree.query,
                    {"tree": "kd_tree", "func": "query", "n": n},
                    bounds,
                )
            )

            qt = (
                qtree.query(bounds)
                if not timer
                else add_time(
                    time_df,
                    qtree.query,
                    {"tree": "qt_tree", "func": "query", "n": n},
                    bounds,
                )
            )

            if kd == solution:
                print("KD OK")
            else:
                print("KD ERR", kd, solution)
                return
            if qt == solution:
                print("QT OK")
            else:
                print("QT ERR")
                return

    time_df.to_csv(TIME_DF_DIR, index=False)


if __name__ == "__main__":
    import pandas as pd

    test(timer=True)
