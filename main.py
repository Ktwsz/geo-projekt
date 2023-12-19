import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from kdtree import KDTree
from test import generate_points
from quadtree import QuadTree

fig, ax = plt.subplots()
fig.subplots_adjust(bottom=0.2)

ax.set_xlim(0, 1010)
ax.set_ylim(0, 1010)

points = []
drawn_points = []
bounds = []
drawn_bounds = []

tree = None
tree_drawn_segments = []


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
    ax.set_xlim(0, 1010)
    ax.set_ylim(0, 1010)
    clear_tree()
    set_default()
    plt.draw()


axclearbtn = fig.add_axes([0.1, 0.05, 0.1, 0.075])
clearbtn = Button(axclearbtn, "Wyczyść")
clearbtn.on_clicked(on_clear)


def on_generate(event):
    on_clear(event)
    global points, drawn_points
    points = generate_points(50, 950, 100)
    for x, y in points:
        p = ax.plot([x], [y], marker="o", markersize=5, color="blue")[0]
        drawn_points.append(p)

    plt.draw()


axgenbtn = fig.add_axes([0.25, 0.05, 0.1, 0.075])
genbtn = Button(axgenbtn, "Wygeneruj")
genbtn.on_clicked(on_generate)


def on_qtree(event):
    global tree, tree_drawn_segments
    clear_tree()
    tree = QuadTree.from_points(points)
    tree_drawn_segments = tree.draw(ax)
    plt.draw()


def draw_bound(p1, p2):
    xs = [p1[0], p2[0]]
    ys = [p1[1], p2[1]]
    return ax.plot(xs, ys, color="green")[0]


axqtbtn = fig.add_axes([0.45, 0.05, 0.1, 0.075])
qtbtn = Button(axqtbtn, "Quadtree")
qtbtn.on_clicked(on_qtree)


def on_kdtree(event):
    global tree, tree_drawn_segments
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


def on_move(event):
    if event.inaxes != ax:
        clear_bounds()
        return
    mousex, mousey = event.xdata, event.ydata
    if tree:
        clear_bounds()
        calculate_bounds(mousex, mousey, 50, 50)
        draw_bounds()
        found_points = get_points_in_bounds()
        highlight_points(found_points)

    plt.draw()


plt.connect("motion_notify_event", on_move)
# plt.connect('button_press_event', on_click)
plt.show()
