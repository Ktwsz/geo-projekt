from math import log10
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, RangeSlider, TextBox
from kdtree import KDTree
import numpy as np
from quadtree import QTPoint, QuadTree


def generate_points(xrange, yrange, n):
    r = np.random.uniform
    return [(r(*xrange), r(*yrange)) for _ in range(n)]


X_LOWER_LIMIT = -100
X_UPPER_LIMIT = 100

Y_LOWER_LIMIT = -100
Y_UPPER_LIMIT = 100

BOUNDS_RADX = 50
BOUDNS_RADY = 50
BOUNDS_STEP = 5

DEFAULT_POINTS_NUMBER = 50

POINTS_MIN_COORD = 50
POINS_MAX_COORD = 950


fig, ax = plt.subplots()
fig.set_dpi(100)
fig.set_size_inches(8, 6)
ax.set_position([0.1, 0.25, 0.7, 0.7])

xrange = (X_LOWER_LIMIT, X_UPPER_LIMIT)
yrange = (Y_LOWER_LIMIT, Y_UPPER_LIMIT)


def set_ax_limits():
    xmargin = log10(xrange[1] - xrange[0])
    ymargin = log10(yrange[1] - yrange[0])
    ax.set_xlim(xrange[0] - xmargin, xrange[1] + xmargin)
    ax.set_ylim(yrange[0] - ymargin, yrange[1] + ymargin)


set_ax_limits()

xsliderax = fig.add_axes([0.1, 0.15, 0.65, 0.03])
xslider = RangeSlider(
    ax=xsliderax,
    label="zakres x",
    valmin=X_LOWER_LIMIT,
    valmax=X_UPPER_LIMIT,
    valinit=(X_LOWER_LIMIT, X_UPPER_LIMIT),
)

ysliderax = fig.add_axes([0.1, 0.1, 0.65, 0.03])
yslider = RangeSlider(
    ax=ysliderax,
    label="zakres y",
    valmin=Y_LOWER_LIMIT,
    valmax=Y_UPPER_LIMIT,
    valinit=(Y_LOWER_LIMIT, Y_UPPER_LIMIT),
)

pointstxtbxax = fig.add_axes([0.1, 0.04, 0.1, 0.04])
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


points = []
drawn_points = []
bounds = []
drawn_bounds = []

tree = None
tree_drawn_segments = []

bounds_radx = BOUNDS_RADX
bounds_rady = BOUDNS_RADY

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


def on_clear(event):
    ax.cla()
    set_ax_limits()
    clear_tree()
    set_default()
    set_sliders_active(True)
    plt.draw()


axclearbtn = fig.add_axes([0.75, 0.04, 0.1, 0.04])
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


axgenbtn = fig.add_axes([0.22, 0.04, 0.1, 0.04])
genbtn = Button(axgenbtn, "Wygeneruj")
genbtn.on_clicked(on_generate)


def draw_tree():
    global tree_drawn_segments
    if not isinstance(tree, QuadTree) and not isinstance(tree, KDTree):
        return

    tree_drawn_segments = tree.draw(ax)
    plt.draw()


def on_qtree(event):
    global tree, tree_drawn_segments, points
    if not points:
        return
    clear_tree()
    tree = QuadTree.from_points(points)
    draw_tree()


def draw_bound(p1, p2):
    xs = [p1[0], p2[0]]
    ys = [p1[1], p2[1]]
    return ax.plot(xs, ys, color="green")[0]


axqtbtn = fig.add_axes([0.4, 0.04, 0.1, 0.04])
qtbtn = Button(axqtbtn, "Quadtree")
qtbtn.on_clicked(on_qtree)


def on_kdtree(event):
    global tree, tree_drawn_segments, points
    if not points:
        return
    clear_tree()
    tree = KDTree(points, draw_bounds=((X_LOWER_LIMIT, X_UPPER_LIMIT), (Y_LOWER_LIMIT, Y_UPPER_LIMIT)))
    plt.draw()


axkdtbtn = fig.add_axes([0.55, 0.04, 0.1, 0.04])
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
        color = "red" if i in found_points else "blue"
        drawn_points[i] = ax.plot([x], [y], marker="o", markersize=5, color=color)[0]


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
    if event.inaxes != ax:
        clear_bounds()
        return
    mousex, mousey = event.xdata, event.ydata
    update_bounds(mousex, mousey)
    update_points()

    plt.draw()


def on_click(event):
    global tree
    if event.inaxes != ax:
        return
    x, y = event.xdata, event.ydata
    points.append((x, y))
    p = ax.plot([x], [y], marker="o", markersize=5, color="blue")[0]
    drawn_points.append(p)
    if isinstance(tree, QuadTree):
        tree.insert(QTPoint(x, y, len(points) - 1))

    if isinstance(tree, KDTree):
        tree.insert(x, y, len(points) - 1)

    clear_tree()
    draw_tree()


def on_key_press(event):
    global bounds_radx, bounds_rady

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
    update_points()


plt.connect("motion_notify_event", on_move)
plt.connect("key_press_event", on_key_press)
plt.connect("button_press_event", on_click)
plt.show()
