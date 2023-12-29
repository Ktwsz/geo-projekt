from test_plot import draw, draw_points, show_points_single_test
from test_utils import test, points_generate_circle, points_generate_uniform


def test_same_size(state, points_gen, bounds_gen, df_dir):
    test_repeat = 100
    query_repeat = 100

    test(test_repeat, query_repeat, points_gen, bounds_gen, state, timer=True, time_df_name=df_dir)


def test_asymptotic(state, points_gen, bounds_gen, df_dir):
    test_repeat = 1
    query_repeat = 100

    for n in range(10000, 100001, 1000):
        state["n"] = n
        test(test_repeat, query_repeat, points_gen, bounds_gen, state, timer=True, time_df_name=df_dir)


if __name__ == "__main__":
    state = {"left_bound": -1000, "right_bound": 1000, "n": 10000, "center": (0, 0), "radius": 100}

    draw_points(points_generate_uniform(state), "data/img/punkty_uniform.png", "Przykładowa dystrybucja punktów")
    draw_points(points_generate_circle(state), "data/img/punkty_circle.png", "Przykładowa dystrybucja punktów")
    print("--- rysowanie punktów done ---")

    test_same_size(state, "uniform", "random", "data/csv/ss_u_r.csv")
    print("--- testy uniform done ---")
    show_points_single_test("data/csv/ss_u_r.csv")

    test_same_size(state, "circle", "random", "data/csv/ss_c_r.csv")
    print("--- testy circle done ---")
    show_points_single_test("data/csv/ss_c_r.csv")

    test_asymptotic(state, "uniform", "random", "data/csv/as_u_r.csv")
    test_asymptotic(state, "circle", "random", "data/csv/as_c_r.csv")
    test_asymptotic(state, "uniform", "small", "data/csv/as_u_s.csv")
    test_asymptotic(state, "uniform", "big", "data/csv/as_u_b.csv")
    test_asymptotic(state, "circle", "small", "data/csv/as_c_s.csv")
    test_asymptotic(state, "circle", "big", "data/csv/as_c_b.csv")
    print("--- testy asymptotyczne done ---")

    draw("data/csv/as_u_r.csv", 'data/img/as_u_r.png', "Porównanie czasowe dla punktów na płaszczyźnie i losowych przedziałów")
    draw("data/csv/as_c_r.csv", 'data/img/as_c_r.png', "Porównanie czasowe dla punktów na okręgu i losowych przedziałów")
    draw("data/csv/as_u_s.csv", 'data/img/as_u_s.png', "Porównanie czasowe dla punktów na płaszczyźnie i małych przedziałów")
    draw("data/csv/as_u_b.csv", 'data/img/as_u_b.png', "Porównanie czasowe dla punktów na płaszczyźnie i dużych przedziałów")
    draw("data/csv/as_c_s.csv", 'data/img/as_c_s.png', "Porównanie czasowe dla punktów na okręgu i małych przedziałów")
    draw("data/csv/as_c_b.csv", 'data/img/as_c_b.png', "Porównanie czasowe dla punktów na okręgu i dużych przedziałów")
    print("--- rysowanie wykresów done ---")
