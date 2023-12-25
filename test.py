from test_plot import draw
from test_utils import test


TIME_DF_DIR = "./time.csv"
ASYMPTOTIC_TIME_DF_DIR = "./as_time.csv"


def test_same_size():
    state = {"left_bound": -1000, "right_bound": 1000, "n": 10000}
    test_repeat = 100
    query_repeat = 100

    test(test_repeat, query_repeat, "uniform", "random", state, timer=True, time_df_name=TIME_DF_DIR)


def test_asymptotic_small():
    state = {"left_bound": -1000, "right_bound": 1000}
    test_repeat = 1
    query_repeat = 100

    for n in range(10000, 100001, 1000):
        state["n"] = n
        test(test_repeat, query_repeat, "uniform", "small", state, timer=True, time_df_name=ASYMPTOTIC_TIME_DF_DIR)


def test_asymptotic_big():
    state = {"left_bound": -1000, "right_bound": 1000, "center": (0, 0), "radius": 100}
    test_repeat = 1
    query_repeat = 100

    for n in range(10000, 100001, 1000):
        state["n"] = n
        test(test_repeat, query_repeat, "uniform", "small", state, timer=True, time_df_name="test_big.csv")


if __name__ == "__main__":
    #test_same_size()
    #test_asymptotic_small()
    test_asymptotic_big()
    draw("test_big.csv", 'asymptoty_big.png', "")
