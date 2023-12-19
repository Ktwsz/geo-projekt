import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from kdtree import KDTree
from test import generate_points
from quadtree import QTPoint, QuadTree

X_LOWER_LIMIT = 0
X_UPPER_LIMIT = 1010

Y_LOWER_LIMIT = 0
Y_UPPER_LIMIT = 1010

BOUNDS_RADX = 50
BOUDNS_RADY = 50
BOUNDS_STEP = 5

POINTS_NUMBER = 50

POINTS_MIN_COORD = 50
POINS_MAX_COORD = 950

QT_MIN_X = 10
QT_MAX_X = 990
QT_MIN_Y = 10
QT_MAX_Y = 990


fig, ax = plt.subplots()
fig.subplots_adjust(bottom=0.2)

ax.set_xlim(X_LOWER_LIMIT, X_UPPER_LIMIT)
ax.set_ylim(Y_LOWER_LIMIT, Y_UPPER_LIMIT)

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
    ax.set_xlim(X_LOWER_LIMIT, X_UPPER_LIMIT)
    ax.set_ylim(Y_LOWER_LIMIT, Y_UPPER_LIMIT)
    clear_tree()
    set_default()
    plt.draw()


axclearbtn = fig.add_axes([0.1, 0.05, 0.1, 0.075])
clearbtn = Button(axclearbtn, "Wyczyść")
clearbtn.on_clicked(on_clear)


def on_generate(event):
    on_clear(event)
    global points, drawn_points
    points = generate_points(POINTS_MIN_COORD, POINS_MAX_COORD, POINTS_NUMBER)
    for x, y in points:
        p = ax.plot([x], [y], marker="o", markersize=5, color="blue")[0]
        drawn_points.append(p)

    plt.draw()


axgenbtn = fig.add_axes([0.25, 0.05, 0.1, 0.075])
genbtn = Button(axgenbtn, "Wygeneruj")
genbtn.on_clicked(on_generate)


def draw_tree():
    global tree_drawn_segments
    if not isinstance(tree, QuadTree):
        return
    tree_drawn_segments = tree.draw(ax)
    plt.draw()


def on_qtree(event):
    global tree, tree_drawn_segments, points
    if not points:
        return
    clear_tree()
    tree = QuadTree.fixed_size(points, QT_MIN_X, QT_MAX_X, QT_MIN_Y, QT_MAX_Y)
    draw_tree()


def draw_bound(p1, p2):
    xs = [p1[0], p2[0]]
    ys = [p1[1], p2[1]]
    return ax.plot(xs, ys, color="green")[0]


axqtbtn = fig.add_axes([0.45, 0.05, 0.1, 0.075])
qtbtn = Button(axqtbtn, "Quadtree")
qtbtn.on_clicked(on_qtree)


def on_kdtree(event):
    global tree, tree_drawn_segments, points
    if not points:
        return
    clear_tree()
    tree = KDTree(points)
    plt.draw()


axkdtbtn = fig.add_axes([0.75, 0.05, 0.1, 0.075])
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

    update_bounds(mousex, mousey)
    update_points()


plt.connect("motion_notify_event", on_move)
plt.connect("key_press_event", on_key_press)
plt.connect("button_press_event", on_click)
plt.show()
