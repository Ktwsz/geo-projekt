import matplotlib.pyplot as plt
import pandas as pd


def draw(df_dir, out_dir, title):
    fig, ax = plt.subplots()

    time_df = pd.read_csv(df_dir)

    brute_plot = [[], []]
    kd_plot = [[], []]
    qt_plot = [[], []]

    for n in time_df["n"].unique():
        query_samples = time_df[(time_df["n"] == n) & (time_df["func"] == "query")]

        brute_samples = query_samples[query_samples["tree"] == "brute"]
        kd_tree_samples = query_samples[query_samples["tree"] == "kd_tree"]
        qt_tree_samples = query_samples[query_samples["tree"] == "qt_tree"]

        brute_y = brute_samples["time"].mean()
        kd_y = kd_tree_samples["time"].mean()
        qt_y = qt_tree_samples["time"].mean()

        brute_plot[0].append(n)
        brute_plot[1].append(brute_y)
        kd_plot[0].append(n)
        kd_plot[1].append(kd_y)
        qt_plot[0].append(n)
        qt_plot[1].append(qt_y)

    ax.plot(*brute_plot, 'r.', label="brute")
    ax.plot(*kd_plot, 'b.', label="kd tree")
    ax.plot(*qt_plot, 'g.', label="quad tree")

    ax.legend()
    ax.set_xlabel("N")
    ax.set_ylabel("t [s]")
    ax.set_title(title)
    fig.savefig(out_dir)


def draw_points(points, out_dir, title):
    fig, ax = plt.subplots()

    ax.plot([x for x, y in points], [y for x, y in points], '.')

    ax.axis("equal")
    ax.set_xlim(left=-1000, right=1000)
    ax.set_ylim(bottom=-1000, top=1000)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title(title)
    fig.savefig(out_dir)


if __name__ == "__main__":
    draw()
