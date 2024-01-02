from copy import deepcopy
from vis import Eraser, Point, Segment, Rect


class Node:
    def __init__(self, ix=None, p=None, left=None, right=None):
        self.ix = ix
        self.p = p
        self.left = left
        self.right = right


class KDTree:
    def __init__(self, points=None, draw_bounds=None):
        if points is None:
            return

        self.tree = self.build_tree(list(enumerate(points)))

        self.draw_bounds = draw_bounds

    def build_tree(self, points, depth=0):
        sorted_points = [sorted(points, key=lambda elem: elem[1][axis]) for axis in range(2)]

        def build_tree_helper(points, depth=0):
            n = len(points[0])
            if n == 0:
                return None

            axis = depth % 2

            ix, p = points[axis][n // 2]

            left_points = [[(ix1, p1)
                            for ix1, p1
                            in points_axis
                            if p1[axis] - p[axis] < 0 and ix1 != ix]
                           for points_axis in points]

            right_points = [[(ix1, p1)
                             for ix1, p1
                             in points_axis
                             if p1[axis] - p[axis] >= 0 and ix1 != ix]
                            for points_axis in points]

            return Node(
                ix,
                p,
                build_tree_helper(left_points, depth + 1),
                build_tree_helper(right_points, depth + 1),
            )

        return build_tree_helper(sorted_points)

    def query(self, bounds):
        def query_helper(node, bounds, depth=0):
            if node is None:
                return set()

            axis = depth % 2

            search_left = node.p[axis] >= bounds[axis][0]
            search_right = node.p[axis] <= bounds[axis][1]

            is_p_in_bounds = (
                node.p[0] >= bounds[0][0]
                and node.p[0] <= bounds[0][1]
                and node.p[1] >= bounds[1][0]
                and node.p[1] <= bounds[1][1]
            )

            ans = {node.ix} if is_p_in_bounds else set()

            if search_left:
                ans |= query_helper(node.left, bounds, depth + 1)

            if search_right:
                ans |= query_helper(node.right, bounds, depth + 1)

            return ans

        return query_helper(self.tree, bounds)

    def insert(self, x, y, ix):
        def insert_helper(node, new_node, depth=0):
            if node is None:
                return

            axis = depth % 2

            if node.p[axis] >= new_node.p[axis] and node.left is not None:
                insert_helper(node.left, new_node, depth + 1)
            elif node.p[axis] >= new_node.p[axis]:
                node.left = new_node

            if node.p[axis] < new_node.p[axis] and node.right is not None:
                insert_helper(node.right, new_node, depth + 1)
            elif node.p[axis] < new_node.p[axis]:
                node.right = new_node

        new_node = Node(p=(x, y), ix=ix)
        insert_helper(self.tree, new_node)

    def draw(self, ax):
        def draw_helper(node, ax, current_bounds, depth=0):
            if node is None:
                return []

            axis = depth % 2

            segment, left_bounds, right_bounds = KDTree.get_bounds(node.p, axis, current_bounds)

            draw_segments = [ax.plot(*segment, color="black")[0]]

            return (draw_segments +
                    draw_helper(node.left, ax, tuple(left_bounds), depth + 1) +
                    draw_helper(node.right, ax, tuple(right_bounds), depth + 1)
                    )


        return draw_helper(self.tree, ax, self.draw_bounds)


    def visualized_query(self, bounds):
        def query_helper(node, bounds, current_bounds, depth=0):
            if node is None:
                return set(), []

            axis = depth % 2

            segment, left_bounds, right_bounds = KDTree.get_bounds(node.p, axis, current_bounds)

            rc_left = Rect(x1=left_bounds[0][0], y1=left_bounds[1][0], x2=left_bounds[0][1], y2=left_bounds[1][1], color="yellow")
            rc_right = Rect(x1=right_bounds[0][0], y1=right_bounds[1][0], x2=right_bounds[0][1], y2=right_bounds[1][1], color="yellow")

            search_left = node.p[axis] >= bounds[axis][0]
            search_right = node.p[axis] <= bounds[axis][1]

            rc_left_done = Rect(x1=left_bounds[0][0], y1=left_bounds[1][0], x2=left_bounds[0][1], y2=left_bounds[1][1], color="green" if search_left else "red")
            rc_right_done = Rect(x1=right_bounds[0][0], y1=right_bounds[1][0], x2=right_bounds[0][1], y2=right_bounds[1][1], color="green" if search_right else "red")

            is_p_in_bounds = (
                node.p[0] >= bounds[0][0]
                and node.p[0] <= bounds[0][1]
                and node.p[1] >= bounds[1][0]
                and node.p[1] <= bounds[1][1]
            )

            point_vis = Point(node.p[0], node.p[1], "green" if is_p_in_bounds else "blue")

            ans = {node.ix} if is_p_in_bounds else set()
            steps = [[point_vis], [rc_left], [Eraser(rc_left), rc_left_done], [rc_right], [Eraser(rc_right), rc_right_done]]


            if search_left:
                steps += [[Eraser(rc_left_done)]]
                ans_left, steps_left = query_helper(node.left, bounds, tuple(left_bounds), depth + 1)
                ans |= ans_left
                steps += steps_left

            if search_right:
                steps += [[Eraser(rc_right_done)]]
                ans_right, steps_right = query_helper(node.right, bounds, tuple(right_bounds), depth + 1)
                ans |= ans_right
                steps += steps_right

            return ans, steps

        return query_helper(self.tree, bounds, self.draw_bounds)


    @staticmethod
    def get_bounds(p, axis, draw_bounds):
        other_axis = 1 - axis

        segment = [[None, None], [None, None]]

        segment[axis] = (p[axis], p[axis])

        segment[other_axis] = draw_bounds[other_axis]

        left_bounds = list(deepcopy(draw_bounds))
        left_bounds[axis] = (left_bounds[axis][0], p[axis])

        right_bounds = list(deepcopy(draw_bounds))
        right_bounds[axis] = (p[axis], right_bounds[axis][1])

        return segment, left_bounds, right_bounds


    @staticmethod
    def visualized_init(points, draw_bounds):
        def init_helper(points, draw_bounds, depth=0):
            n = len(points)

            if n == 0:
                return None, []

            axis = depth % 2

            sorted_points = sorted(points, key=lambda elem: elem[1][axis])

            ix, p = sorted_points[n // 2]

            node = Node(ix, p)

            segment, left_bounds, right_bounds = KDTree.get_bounds(node.p, axis, draw_bounds)

            p_vis = Point(p[0], p[1], "red")
            steps = [[p_vis], [Point(p[0], p[1], "green"), Segment((segment[0][0],segment[1][0]), (segment[0][1], segment[1][1]))]]

            left_node, left_steps = init_helper(sorted_points[: n // 2], tuple(left_bounds), depth + 1)
            right_node, right_steps = init_helper(sorted_points[n // 2 + 1 :], tuple(right_bounds), depth + 1)

            node.left = left_node
            node.right = right_node

            steps += left_steps
            steps += right_steps

            return node, steps

        root, steps = init_helper(list(enumerate(points)), draw_bounds)

        tree = KDTree()
        tree.tree = root
        tree.draw_bounds = draw_bounds

        return tree, steps

    def update_draw_bounds(self, draw_bounds):
        self.draw_bounds = draw_bounds
