class Node:
    def __init__(self, ix=None, p=None, left=None, right=None):
        self.ix = ix
        self.p = p
        self.left = left
        self.right = right


class KDTree:
    def __init__(self, points):
        self.tree = self.build_tree(points)

    def build_tree(self, points, depth=0):
        n = len(points)

        if n == 0:
            return None

        axis = depth % 2

        sorted_points = sorted(points, key=lambda elem: elem[1][axis])

        ix, p = sorted_points[n // 2]

        return Node(ix, p,
                    self.build_tree(sorted_points[:n // 2], depth + 1),
                    self.build_tree(sorted_points[n // 2 + 1:], depth + 1))

    def query(self, bounds):
        def query_helper(node, bounds, depth=0):
            if node is None:
                return set()

            axis = depth % 2

            search_left = node.p[axis] >= bounds[axis][0]
            search_right = node.p[axis] <= bounds[axis][1]

            is_p_in_bounds = node.p[0] >= bounds[0][0] and \
                             node.p[0] <= bounds[0][1] and \
                             node.p[1] >= bounds[1][0] and \
                             node.p[1] <= bounds[1][1]

            ans = {node.ix} if is_p_in_bounds else set()

            if search_left:
                ans |= query_helper(node.left, bounds, depth + 1)

            if search_right:
                ans |= query_helper(node.right, bounds, depth + 1)

            return ans

        return query_helper(self.tree, bounds)


def find_points(points, bounds):
    kdtree = KDTree(list(enumerate(points)))

    return kdtree.query(bounds)
