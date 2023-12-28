from copy import deepcopy


class Node:
    def __init__(self, ix=None, p=None, left=None, right=None):
        self.ix = ix
        self.p = p
        self.left = left
        self.right = right


class KDTree:
    def __init__(self, points, draw_bounds=None):
        self.tree = self.build_tree(list(enumerate(points)))

        self.draw_bounds = draw_bounds

    def build_tree(self, points, depth=0):
        n = len(points)

        if n == 0:
            return None

        axis = depth % 2

        sorted_points = sorted(points, key=lambda elem: elem[1][axis])

        ix, p = sorted_points[n // 2]

        return Node(
            ix,
            p,
            self.build_tree(sorted_points[: n // 2], depth + 1),
            self.build_tree(sorted_points[n // 2 + 1 :], depth + 1),
        )

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
            other_axis = 1 - axis

            segment = [[None, None], [None, None]]

            segment[axis] = (node.p[axis], node.p[axis])

            segment[other_axis] = current_bounds[other_axis]


            draw_segments = [ax.plot(*segment, color="black")[0]]

            left_bounds = list(deepcopy(current_bounds))
            left_bounds[axis] = (left_bounds[axis][0], node.p[axis])

            right_bounds = list(deepcopy(current_bounds))
            right_bounds[axis] = (node.p[axis], right_bounds[axis][1])

            return (draw_segments +
                    draw_helper(node.left, ax, tuple(left_bounds), depth + 1) +
                    draw_helper(node.right, ax, tuple(right_bounds), depth + 1)
                    )


        return draw_helper(self.tree, ax, self.draw_bounds)
