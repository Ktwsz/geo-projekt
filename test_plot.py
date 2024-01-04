import matplotlib.pyplot as plt
import pandas as pd
from numpy import isnan


def draw(df_dir, out_dir, func_name, title=None):
    fig, ax = plt.subplots()

    time_df = pd.read_csv(df_dir)

    brute_plot = [[], []]
    kd_plot = [[], []]
    qt_plot = [[], []]

    for n in time_df["n"].unique():
        query_samples = time_df[(time_df["n"] == n) & (time_df["func"] == func_name)]

        brute_samples = query_samples[query_samples["tree"] == "brute"]
        kd_tree_samples = query_samples[query_samples["tree"] == "kd_tree"]
        qt_tree_samples = query_samples[query_samples["tree"] == "qt_tree"]

        brute_y = brute_samples["time"].mean()
        kd_y = kd_tree_samples["time"].mean()
        qt_y = qt_tree_samples["time"].mean()

        if not isnan(brute_y):
            brute_plot[0].append(n)
            brute_plot[1].append(brute_y)

        kd_plot[0].append(n)
        kd_plot[1].append(kd_y)
        qt_plot[0].append(n)
        qt_plot[1].append(qt_y)

    if brute_plot[0]:
        ax.plot(*brute_plot, "r.", label="brute")

    ax.plot(*kd_plot, "b.", label="kd tree")
    ax.plot(*qt_plot, "g.", label="quad tree")

    ax.legend()
    ax.set_xlabel("N")
    ax.set_ylabel("t [s]")
    if title:
        ax.set_title(title)
    fig.savefig(out_dir)
    plt.close()


def draw_points(points, out_dir, title=None):
    fig, ax = plt.subplots()

    ax.plot([x for x, y in points], [y for x, y in points], ".")

    ax.axis("equal")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    if title:
        ax.set_title(title)
    fig.savefig(out_dir)


def show_points_single_test(df_dir):
    time_df = pd.read_csv(df_dir)

    brute_samples = time_df[time_df["tree"] == "brute"]
    kd_tree_samples = time_df[time_df["tree"] == "kd_tree"]
    qt_tree_samples = time_df[time_df["tree"] == "qt_tree"]

    kd_tree_setup = kd_tree_samples[kd_tree_samples["func"] == "setup"]["time"].sum()
    kd_tree_query = kd_tree_samples[kd_tree_samples["func"] == "query"]["time"].sum()

    qt_tree_setup = qt_tree_samples[qt_tree_samples["func"] == "setup"]["time"].sum()
    qt_tree_query = qt_tree_samples[qt_tree_samples["func"] == "query"]["time"].sum()

    brute_query = brute_samples[brute_samples["func"] == "query"]["time"].sum()

    print("setup kd-tree: ", kd_tree_setup)
    print("query kd-tree: ", kd_tree_query)

    print("setup quadtree: ", qt_tree_setup)
    print("query quadtree: ", qt_tree_query)

    print("query brute: ", brute_query)


if __name__ == "__main__":
    draw()
