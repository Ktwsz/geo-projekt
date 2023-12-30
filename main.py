from math import log10
from threading import Thread
from matplotlib.axes import Axes
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, RangeSlider, TextBox, CheckButtons
from kdtree import KDTree
import numpy as np
from quadtree import QuadTree
from time import sleep


def generate_points(xrange, yrange, n):
    r = np.random.uniform
    return [(r(*xrange), r(*yrange)) for _ in range(n)]


X_LOWER_LIMIT = -1000
X_UPPER_LIMIT = 1000

Y_LOWER_LIMIT = -1000
Y_UPPER_LIMIT = 1000

DEFAULT_X_RANGE = (-500, 500)
DEFAULT_Y_RANGE = (-500, 500)

DEFAULT_BOUNDS_RADX = 50
DEFAULT_BOUDNS_RADY = 50
BOUNDS_STEP = 5

DEFAULT_POINTS_NUMBER = 50

VIS_SLEEP_TIME = 1

subplots: tuple[Figure, Axes] = plt.subplots()
fig = subplots[0]
ax = subplots[1]
fig.set_dpi(100)
fig.set_size_inches(8, 6)
ax.set_position((0.1, 0.25, 0.7, 0.7))

xrange = DEFAULT_X_RANGE
yrange = DEFAULT_Y_RANGE


def set_ax_limits():
    xmargin = log10(xrange[1] - xrange[0])
    ymargin = log10(yrange[1] - yrange[0])
    ax.set_xlim(xrange[0] - xmargin, xrange[1] + xmargin)
    ax.set_ylim(yrange[0] - ymargin, yrange[1] + ymargin)


set_ax_limits()

xsliderax = fig.add_axes((0.1, 0.17, 0.65, 0.03))
xslider = RangeSlider(
    ax=xsliderax,
    label="zakres x",
    valmin=X_LOWER_LIMIT,
    valmax=X_UPPER_LIMIT,
    valinit=DEFAULT_X_RANGE,
)

ysliderax = fig.add_axes((0.1, 0.12, 0.65, 0.03))
yslider = RangeSlider(
    ax=ysliderax,
    label="zakres y",
    valmin=Y_LOWER_LIMIT,
    valmax=Y_UPPER_LIMIT,
    valinit=DEFAULT_Y_RANGE,
)

pointstxtbxax = fig.add_axes((0.1, 0.04, 0.1, 0.04))
pointstxtbx = TextBox(ax=pointstxtbxax, label="liczba\npunktów")
pointstxtbx.label.set_x(-0.1)
pointstxtbx.label.set_y(0.5)
pointstxtbx.label.set_fontsize(9)

pointstxtbx.set_val(str(DEFAULT_POINTS_NUMBER))


def get_points_number():
    return int(pointstxtbx.text)


def set_x_range(r):
    global xrange
    xrange = r
    set_ax_limits()


def set_y_range(r):
    global yrange
    yrange = r
    set_ax_limits()


xslider.on_changed(set_x_range)
yslider.on_changed(set_y_range)


def set_sliders_active(active):
    xslider.set_active(active)
    yslider.set_active(active)


loadbtnax = fig.add_axes((0.1, 0.955, 0.1, 0.04))
loadbtn = Button(loadbtnax, "Wczytaj")

filetxtbxax = fig.add_axes((0.29, 0.955, 0.35, 0.04))
filetxtbx = TextBox(ax=filetxtbxax, label="ścieżka\ndo pliku")
filetxtbx.label.set_x(-0.02)
filetxtbx.label.set_y(0.5)
filetxtbx.label.set_fontsize(7)

savebtnax = fig.add_axes((0.7, 0.955, 0.1, 0.04))
savebtn = Button(savebtnax, "Zapisz")


def on_load(_):
    global points
    on_clear(None)
    path = filetxtbx.text
    with open(path) as f:
        for line in f:
            x, y = line.split(" ")
            x = float(x)
            y = float(y)
            points.append((x, y))

    for x, y in points:
        p = ax.plot([x], [y], marker="o", markersize=5, color="blue")[0]
        drawn_points.append(p)

    plt.draw()


def on_save(_):
    path = filetxtbx.text
    with open(path, "w") as f:
        for x, y in points:
            f.write(str(x) + " " + str(y) + "\n")


loadbtn.on_clicked(on_load)
savebtn.on_clicked(on_save)

vischckbxax = fig.add_axes((0.43, -0.07, 0.2, 0.18))
vischckbxax.spines.clear()
vischckbx = CheckButtons(
    ax=vischckbxax,
    labels=["wizualizacja"],
    actives=[False],
)
vischckbx.labels[0].set_x(0.2)


def on_check(event):
    if not is_visualize_checked():
        finish_animation()
        clear_animation()
        if tree:
            clear_tree()
            draw_tree()


vischckbx.on_clicked(on_check)


def is_visualize_checked():
    return vischckbx.get_status()[0]


points = []
drawn_points = []
bounds = []
drawn_bounds = []

tree = None
tree_drawn_segments = []

bounds_radx = DEFAULT_BOUNDS_RADX
bounds_rady = DEFAULT_BOUDNS_RADY

mousex = 0
mousey = 0


def set_default():
    global points, drawn_points, bounds, drawn_bounds, tree, tree_drawn_segments
    points = []
    drawn_points = []
    bounds = []
    drawn_bounds = []
    tree = None
    tree_drawn_segments = []


def clear_tree():
    global tree_drawn_segments
    for s in tree_drawn_segments:
        s.remove()
    tree_drawn_segments = []


sleep_time = VIS_SLEEP_TIME
th = None


def finish_animation():
    global th, sleep_time
    if th:
        sleep_time = 0
        th.join()
        sleep_time = VIS_SLEEP_TIME
        th = None


def on_clear(event):
    finish_animation()
    ax.cla()
    set_ax_limits()
    clear_tree()
    set_default()
    set_sliders_active(True)
    plt.draw()


axclearbtn = fig.add_axes((0.75, 0.04, 0.1, 0.04))
clearbtn = Button(axclearbtn, "Wyczyść")
clearbtn.on_clicked(on_clear)


def on_generate(event):
    on_clear(event)
    global points, drawn_points
    if not pointstxtbx.text:
        return
    points = generate_points(xrange, yrange, get_points_number())
    for x, y in points:
        p = ax.plot([x], [y], marker="o", markersize=5, color="blue")[0]
        drawn_points.append(p)

    plt.draw()


axgenbtn = fig.add_axes((0.22, 0.04, 0.1, 0.04))
genbtn = Button(axgenbtn, "Wygeneruj")
genbtn.on_clicked(on_generate)

animation_objects = []


def clear_animation():
    global animation_objects, sleep_time
    sth_removed = False
    for p in animation_objects:
        if not sleep_time:
            break
        try:
            p.remove()
            sth_removed = True
        except:
            pass
    return sth_removed


def visualize_query(steps):
    global sleep_time, th, animation_objects

    plt.draw()
    if clear_animation():
        plt.draw()
        sleep(sleep_time)
    plt.draw()

    for step in steps:
        if not sleep_time:
            return
        for s in step:
            if not sleep_time:
                return
            animation_objects.append(s.draw(ax))

        plt.draw()
        sleep(sleep_time)

    th = None


def visualize_build(steps):
    global sleep_time, th, animation_objects

    clear_tree()
    for step in steps:
        if not sleep_time:
            return
        for s in step:
            if not sleep_time:
                return
            animation_objects.append(s.draw(ax))

        plt.draw()
        sleep(sleep_time)
    clear_animation()
    if sleep_time:
        plt.draw()
    if sleep_time:
        draw_tree()
    th = None


def draw_tree():
    global tree_drawn_segments, points

    if isinstance(tree, KDTree):
        xs = list(map(lambda t: t[0], points))
        ys = list(map(lambda t: t[1], points))
        draw_bounds = ((min(xs), max(xs)), (min(ys), max(ys)))
        tree.update_draw_bounds(draw_bounds)

    tree_drawn_segments = tree.draw(ax)  # type: ignore
    plt.draw()


def on_qtree(event):
    global tree, tree_drawn_segments, points, th, sleep_time
    if not points:
        return
    finish_animation()
    clear_animation()
    clear_tree()
    if is_visualize_checked():
        if not th:
            tree, steps = QuadTree.from_points(points, True)  # type: ignore
            sleep_time = VIS_SLEEP_TIME
            th = Thread(target=lambda: visualize_build(steps))
            th.start()
    else:
        tree = QuadTree.from_points(points)
        draw_tree()


def draw_bound(p1, p2):
    xs = [p1[0], p2[0]]
    ys = [p1[1], p2[1]]
    return ax.plot(xs, ys, color="green")[0]


axqtbtn = fig.add_axes((0.4, 0.06, 0.1, 0.04))
qtbtn = Button(axqtbtn, "Quadtree")
qtbtn.on_clicked(on_qtree)


def on_kdtree(event):
    global tree, tree_drawn_segments, points, th, sleep_time
    if not points:
        return
    finish_animation()
    clear_animation()
    clear_tree()

    xs = list(map(lambda t: t[0], points))
    ys = list(map(lambda t: t[1], points))
    tree_draw_bounds = ((min(xs), max(xs)), (min(ys), max(ys)))

    if is_visualize_checked():
        if not th:
            tree, steps = KDTree.visualized_init(points, tree_draw_bounds)
            sleep_time = VIS_SLEEP_TIME
            th = Thread(target=lambda: visualize_build(steps))
            th.start()
    else:
        tree = KDTree(
            points,
            draw_bounds=tree_draw_bounds,
        )
        draw_tree()


axkdtbtn = fig.add_axes((0.55, 0.06, 0.1, 0.04))
kdtbtn = Button(axkdtbtn, "KD-Tree")
kdtbtn.on_clicked(on_kdtree)


def clear_bounds():
    global drawn_bounds
    for b in drawn_bounds:
        b.remove()
    drawn_bounds = []
    plt.draw()


def calculate_bounds(x, y, radx, rady):
    global bounds
    bounds = ((x - radx, x + radx), (y - rady, y + rady))


def draw_bounds():
    global drawn_bounds, bounds
    (x1, x2), (y1, y2) = bounds
    p1 = [x1, y1]
    p2 = [x1, y2]
    p3 = [x2, y2]
    p4 = [x2, y1]
    drawn_bounds += [draw_bound(p1, p2)]
    drawn_bounds += [draw_bound(p2, p3)]
    drawn_bounds += [draw_bound(p3, p4)]
    drawn_bounds += [draw_bound(p4, p1)]
    plt.draw()


def get_points_in_bounds():
    if tree is None:
        return set()
    return tree.query(bounds)


def highlight_points(found_points):
    for i, _ in enumerate(drawn_points):
        drawn_points[i].remove()
        x, y = points[i]
        color = "green" if i in found_points else "blue"
        zorder = 2 if i in found_points else 0
        drawn_points[i] = ax.plot(
            [x], [y], marker="o", markersize=5, color=color, zorder=zorder
        )[0]


def update_bounds(mousex, mousey):
    if tree is None:
        return
    clear_bounds()
    calculate_bounds(mousex, mousey, bounds_radx, bounds_rady)
    draw_bounds()


def update_points():
    if tree is None:
        return
    found_points = get_points_in_bounds()
    highlight_points(found_points)


def on_move(event):
    global bounds_radx, bounds_rady, mousex, mousey
    if th is not None:
        return
    if event.inaxes != ax:
        clear_bounds()
        highlight_points(set())
        return
    mousex, mousey = event.xdata, event.ydata
    update_bounds(mousex, mousey)
    if is_visualize_checked():
        highlight_points(set())
    else:
        update_points()
    plt.draw()


def on_click(event):
    global tree, th
    if event.inaxes != ax:
        return
    if is_visualize_checked():
        if th is None:
            p, steps = tree.visualized_query(bounds)
            th = Thread(target=lambda: visualize_query(steps))
            th.start()
    else:
        x, y = event.xdata, event.ydata
        points.append((x, y))
        p = ax.plot([x], [y], marker="o", markersize=5, color="blue")[0]
        drawn_points.append(p)

        if tree:
            tree.insert(x, y, len(points) - 1)
            clear_tree()
            draw_tree()


def on_key_press(event):
    global bounds_radx, bounds_rady, th

    if event.key == "up":
        bounds_rady += BOUNDS_STEP
    if event.key == "down":
        bounds_rady -= BOUNDS_STEP
    if event.key == "right":
        bounds_radx += BOUNDS_STEP
    if event.key == "left":
        bounds_radx -= BOUNDS_STEP

    bounds_radx = max(0, bounds_radx)
    bounds_rady = max(0, bounds_rady)

    update_bounds(mousex, mousey)
    if is_visualize_checked():
        highlight_points(set())
    else:
        update_points()


def on_close(event):
    finish_animation()


plt.connect("close_event", on_close)
plt.connect("motion_notify_event", on_move)
plt.connect("key_press_event", on_key_press)
plt.connect("button_press_event", on_click)
plt.show()
