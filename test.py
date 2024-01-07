from test_plot import draw, draw_points, show_points_single_test
from test_utils import (
    generate_eq,
    generate_grid,
    generate_one_far,
    test,
    points_generate_circle,
    points_generate_uniform,
)


def test_same_size(state, points_gen, bounds_gen, df_dir):
    test_repeat = 100
    query_repeat = 100

    test(
        test_repeat,
        query_repeat,
        points_gen,
        bounds_gen,
        state,
        timer=True,
        time_df_name=df_dir,
    )


def test_asymptotic(state, points_gen, bounds_gen, df_dir):
    test_repeat = 1
    query_repeat = 100

    for n in range(10000, 100001, 1000):
        state["n"] = n
        test(
            test_repeat,
            query_repeat,
            points_gen,
            bounds_gen,
            state,
            timer=True,
            time_df_name=df_dir,
        )


if __name__ == "__main__":
    state = {
        "left_bound": -1000,  # grid -100, one_far -1000
        "right_bound": 1000,  # grid 100, one_far -900
        "n": 10000,
        "center": (0, 0),
        "radius": 100,
    }

    draw_points(
        points_generate_uniform(state),
        "data/img/punkty_uniform.png",
    )
    draw_points(
        points_generate_circle(state),
        "data/img/punkty_circle.png",
    )
    draw_points(
        generate_grid(state),
        "data/img/punkty_grid.png",
    )
    draw_points(
        generate_one_far(state),
        "data/img/punkty_one_far.png",
    )
    print("--- rysowanie punktów done ---")

    test_same_size(state, "uniform", "random", "data/csv/ss_u_r.csv")
    print("--- testy uniform done ---")
    show_points_single_test("data/csv/ss_u_r.csv")

    test_same_size(state, "circle", "random", "data/csv/ss_c_r.csv")
    print("--- testy circle done ---")
    show_points_single_test("data/csv/ss_c_r.csv")

    test_same_size(state, "grid", "random", "data/csv/ss_g_r.csv")
    print("--- testy grid done ---")
    show_points_single_test("data/csv/ss_g_r.csv")

    test_same_size(state, "one_far", "random", "data/csv/ss_o_r.csv")
    print("--- testy one_far done ---")
    show_points_single_test("data/csv/ss_o_r.csv")

    test_asymptotic(state, "uniform", "random", "data/csv/as_u_r.csv")
    test_asymptotic(state, "circle", "random", "data/csv/as_c_r.csv")
    test_asymptotic(state, "grid", "random", "data/csv/as_g_r.csv")
    test_asymptotic(state, "one_far", "random", "data/csv/as_o_r.csv")
    test_asymptotic(state, "uniform", "small", "data/csv/as_u_s.csv")
    test_asymptotic(state, "uniform", "big", "data/csv/as_u_b.csv")
    test_asymptotic(state, "circle", "small", "data/csv/as_c_s.csv")
    test_asymptotic(state, "circle", "big", "data/csv/as_c_b.csv")
    test_asymptotic(state, "grid", "small", "data/csv/as_g_s.csv")
    test_asymptotic(state, "grid", "big", "data/csv/as_g_b.csv")
    test_asymptotic(state, "one_far", "small", "data/csv/as_o_s.csv")
    test_asymptotic(state, "one_far", "big", "data/csv/as_o_b.csv")
    print("--- testy asymptotyczne done ---")

    for func_name in ["query", "setup"]:
        draw("data/csv/as_u_r.csv", f"data/img/as_u_r_{func_name}.png", func_name)
        draw("data/csv/as_c_r.csv", f"data/img/as_c_r_{func_name}.png", func_name)
        draw("data/csv/as_u_s.csv", f"data/img/as_u_s_{func_name}.png", func_name)
        draw("data/csv/as_u_b.csv", f"data/img/as_u_b_{func_name}.png", func_name)
        draw("data/csv/as_c_s.csv", f"data/img/as_c_s_{func_name}.png", func_name)
        draw("data/csv/as_c_b.csv", f"data/img/as_c_b_{func_name}.png", func_name)

        draw("data/csv/as_g_r.csv", f"data/img/as_g_r_{func_name}.png", func_name)
        draw("data/csv/as_o_r.csv", f"data/img/as_o_r_{func_name}.png", func_name)
        draw("data/csv/as_g_s.csv", f"data/img/as_g_s_{func_name}.png", func_name)
        draw("data/csv/as_g_b.csv", f"data/img/as_g_b_{func_name}.png", func_name)
        draw("data/csv/as_o_s.csv", f"data/img/as_o_s_{func_name}.png", func_name)
        draw("data/csv/as_o_b.csv", f"data/img/as_o_b_{func_name}.png", func_name)
    print("--- rysowanie wykresów done ---")
