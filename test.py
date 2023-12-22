from kdtree import KDTree
from quadtree import QuadTree
import numpy as np
from time import process_time
import os.path
from random import randrange


TIME_DF_DIR = "./time.csv"
ASYMPTOTIC_TIME_DF_DIR = "./as_time.csv"


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


def get_rand_bounds_small(points):
    ix = randrange(0, len(points))

    return ((points[ix][0] - 10, points[ix][0] + 10), (points[ix][1] - 10, points[ix][1] + 10))


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


def test(left_bound, right_bound, test_repeat, query_repeat, n, small=False, timer=False, time_df_name=None):

    if timer:
        if os.path.isfile(time_df_name):
            time_df = pd.read_csv(time_df_name)
        else:
            time_df = pd.DataFrame(columns=["time", "tree", "func", "n"])
    else:
        time_df = None

    for _ in range(test_repeat):
        points = generate_points(left_bound, right_bound, n)

        kdtree = (
            KDTree(points)
            if not timer
            else add_time(time_df, KDTree, {"tree": "kd_tree", "func": "setup", "n": n}, points)
        )

        qtree = (
            QuadTree.from_points(points)
            if not timer
            else add_time(
                time_df,
                QuadTree.from_points,
                {"tree": "qt_tree", "func": "setup", "n": n},
                points,
            )
        )

        for _ in range(query_repeat):
            bounds = (
                    get_rand_bounds(left_bound, right_bound) if not small
                    else get_rand_bounds_small(points)
                    )

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

            if kd != solution:
                print("KD ERR", kd, solution)
                return
            if qt != solution:
                print("QT ERR")
                return

    if timer:
        time_df.to_csv(time_df_name, index=False)


def test_same_size():
    left_bound, right_bound = -1000, 1000
    n = 10000
    test_repeat = 100
    query_repeat = 100

    test(left_bound, right_bound, test_repeat, query_repeat, n, timer=True, time_df_name=TIME_DF_DIR)


def test_asymptotic():
    left_bound, right_bound = -1000, 1000
    test_repeat = 1
    query_repeat = 100

    for n in range(10000, 100001, 1000):
        test(left_bound, right_bound, test_repeat, query_repeat, n, small=True, timer=True, time_df_name=ASYMPTOTIC_TIME_DF_DIR)


def draw_asymptots():
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()

    time_df = pd.read_csv(ASYMPTOTIC_TIME_DF_DIR)

    for n in time_df["n"].unique():
        query_samples = time_df[(time_df["n"] == n) & (time_df["func"] == "query")]

        brute_samples = query_samples[query_samples["tree"] == "brute"]
        kd_tree_samples = query_samples[query_samples["tree"] == "kd_tree"]
        qt_tree_samples = query_samples[query_samples["tree"] == "qt_tree"]

        brute_y = brute_samples["time"].mean()
        kd_y = kd_tree_samples["time"].mean()
        qt_y = qt_tree_samples["time"].mean()

        ax.plot([n], [brute_y], 'r.')
        ax.plot([n], [kd_y], 'b.')
        ax.plot([n], [qt_y], 'g.')

    fig.savefig('asymptoty.png')


if __name__ == "__main__":
    import pandas as pd


    #test_same_size(timer=True)
    test_asymptotic()
    draw_asymptots()
