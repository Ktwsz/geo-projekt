from math import log
from kdtree import KDTree
from quadtree import QuadTree
import numpy as np
from time import process_time
import os.path
import pandas as pd
from random import randrange


def points_generate_uniform(state):
    left_bound = state["left_bound"]
    right_bound = state["right_bound"]
    n = state["n"]

    return [
        (x, y)
        for x, y in np.random.uniform(low=left_bound, high=right_bound, size=(n, 2))
    ]


def points_generate_circle(state):
    center = state["center"]
    radius = state["radius"]
    n = state["n"]

    rs = np.random.uniform(low=0, high=radius, size=n)
    thetas = np.random.uniform(low=0, high=2 * np.pi, size=n)

    return [
        (center[0] + r * np.cos(theta), center[1] + r * np.sin(theta))
        for r, theta in zip(rs, thetas)
    ]


def bounds_generate_random(state):
    left, right = state["left_bound"], state["right_bound"]

    x1, x2, y1, y2 = np.random.uniform(left, right, 4)

    if x1 > x2:
        x1, x2 = x2, x1

    if y1 > y2:
        y1, y2 = y2, y1

    return ((x1, x2), (y1, y2))


def bounds_generate_small(state):
    points = state["points"]
    ix = randrange(0, len(points))

    return (
        (points[ix][0] - 10, points[ix][0] + 10),
        (points[ix][1] - 10, points[ix][1] + 10),
    )


def bounds_generate_big(state):
    left, right = state["left_bound"], state["right_bound"]
    bound_size = (right - left) / 4

    x, y = np.random.uniform(low=left, high=right, size=2)
    return ((x, x + bound_size), (y, y + bound_size))


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


def generate_eq(state):
    left, right = state["left_bound"], state["right_bound"]
    n = state["n"]

    from math import isqrt

    s = isqrt(n)

    step = (right - left) / n

    points = []

    for row in range(s):
        for col in range(s):
            points.append((left + col * step, left + row * step))

    return points


from bisect import bisect_left
from math import log


def bis(num):
    n = bisect_left(
        list(range(0, num)), num, lo=0, hi=num, key=lambda x: x * log(x) / log(4)
    )
    return n


def generate_grid(state):
    x, y = state["center"]
    r = state["radius"]
    k = state["n"]

    n = bis(k)

    def _gen_seg(p1, p2, n):
        a, b = p1
        c, d = p2
        stepx = (c - a) / n
        stepy = (d - b) / n
        return [(a + stepx * i, b + stepy * i) for i in range(n + 1)]

    def _gen(x, y, r, n):
        n //= 2
        if not n:
            return []
        return _gen_seg((x - r, y), (x + r, y), n) + _gen_seg((x, y + r), (x, y - r), n)

    def _gen_sq(x, y, r, n, depth):
        if n <= 0:
            return []
        sr = r / 2
        return (
            _gen(x, y, r, n)
            + _gen_sq(x - sr, y + sr, sr, n // 4, depth + 1)
            + _gen_sq(x + sr, y + sr, sr, n // 4, depth + 1)
            + _gen_sq(x - sr, y - sr, sr, n // 4, depth + 1)
            + _gen_sq(x + sr, y - sr, sr, n // 4, depth + 1)
        )

    return _gen_sq(x, y, r, n, 0)


def generate_one_far(state):
    a = 1000
    r = 100
    n = state["n"]
    return points_generate_uniform(
        {"left_bound": -a, "right_bound": -a + r, "n": n}
    ) + [(a, a)]


POINTS_GEN_FUNCS = {
    "uniform": points_generate_uniform,
    "circle": points_generate_circle,
    "grid": generate_grid,
    "one_far": generate_one_far,
}

BOUNDS_GEN_FUNCS = {
    "random": bounds_generate_random,
    "small": bounds_generate_small,
    "big": bounds_generate_big,
}


def test(
    test_repeat,
    query_repeat,
    points_gen_key,
    bounds_gen_key,
    state={},
    timer=False,
    time_df_name=None,
):
    if timer:
        if os.path.isfile(time_df_name):
            time_df = pd.read_csv(time_df_name)
        else:
            time_df = pd.DataFrame(columns=["time", "tree", "func", "n"])
    else:
        time_df = None

    generate_points = POINTS_GEN_FUNCS[points_gen_key]
    generate_bounds = BOUNDS_GEN_FUNCS[bounds_gen_key]

    n = state["n"]

    for _ in range(test_repeat):
        points = generate_points(state)
        state["points"] = points

        kdtree = (
            KDTree(points)
            if not timer
            else add_time(
                time_df, KDTree, {"tree": "kd_tree", "func": "setup", "n": n}, points
            )
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
            bounds = generate_bounds(state)

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
                print("KD ERR", len(kd), len(solution))
                return
            if qt != solution:
                print("QT ERR")
                return

    if timer:
        time_df.to_csv(time_df_name, index=False)
