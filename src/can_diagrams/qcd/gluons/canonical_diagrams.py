import numpy as np

from src.transforms.format import combine_connections # Used to combine different types of connections (particles) into a single array

# First order
points_1st_1 = np.array([[0, 1], [0, 3], [1, 2], [2, 2]])
connections_1st_1g = np.array([[1, 3], [2, 3], [3, 4]]) 
connections_1st_1i = np.array([[0, 0]])

connections_1st_1 = combine_connections(3, connections_1st_1g, connections_1st_1i)

points_1st_2 = np.array([[0, 2], [1, 2], [2, 1], [2, 3]])
connections_1st_2g = np.array([[1, 2], [2, 3], [2, 4]]) 
connections_1st_2i = np.array([[0, 0]])

connections_1st_2 = combine_connections(3, connections_1st_2g, connections_1st_2i)

can_points_1st = np.empty((2, max(len(points_1st_1), len(points_1st_2)), 2))
can_points_1st[0] = points_1st_1
can_points_1st[1] = points_1st_2

can_connections_1st = np.empty((2, max(len(connections_1st_1), len(connections_1st_2)), max(len(connections_1st_1[0]), len(connections_1st_2[0])), 2), dtype=int)
can_connections_1st[0] = connections_1st_1
can_connections_1st[1] = connections_1st_2

can_number_1st = np.array([[1], [1], [1], [1]])

#Second order
points_2nd_1_1 = np.array([[0, 1], [0, 3], [0, 5], [1, 4], [2, 3], [4, 1]])
connections_2nd_1_1g = np.array([[1, 5], [2, 4], [3, 4], [5, 6]])
connections_2nd_1_1i = np.array([[4, 5]])
connections_2nd_1_1 = combine_connections(4, connections_2nd_1_1g, connections_2nd_1_1i)

points_2nd_1_2 = np.array([[0, 1], [0, 3], [0, 5], [1, 2], [2, 3], [4, 1]])
connections_2nd_1_2g = np.array([[1, 4], [2, 4], [3, 5], [5, 6]])
connections_2nd_1_2i = np.array([[4, 5]])
connections_2nd_1_2 = combine_connections(4, connections_2nd_1_2g, connections_2nd_1_2i)

points_2nd_1_3 = np.array([[0, 1], [0, 3], [0, 5], [1, 4], [2, 3], [4, 1]])
connections_2nd_1_3g = np.array([[1, 4], [2, 5], [3, 4], [5, 6]])
connections_2nd_1_3i = np.array([[4, 5]])
connections_2nd_1_3 = combine_connections(4, connections_2nd_1_3g, connections_2nd_1_3i)

points_2nd_2_1 = np.array([[0, 1], [0, 3], [1, 2], [2, 2], [3, 1], [3, 3]])
connections_2nd_2_1g = np.array([[1, 3], [2, 3], [4, 5], [4, 6]])
connections_2nd_2_1i = np.array([[3, 4]])
connections_2nd_2_1 = combine_connections(4, connections_2nd_2_1g, connections_2nd_2_1i)

points_2nd_2_2 = np.array([[0, 1], [0, 3], [1, 1], [2, 3], [3, 1], [3, 3]])
connections_2nd_2_2g = np.array([[1, 3], [2, 4], [3, 5], [4, 6]])
connections_2nd_2_2i = np.array([[3, 4]])
connections_2nd_2_2 = combine_connections(4, connections_2nd_2_2g, connections_2nd_2_2i)

points_2nd_2_3 = np.array([[0, 1], [0, 3], [1, 3], [2, 1], [3, 1], [3, 3]])
connections_2nd_2_3g = np.array([[1, 4], [2, 3], [3, 6], [4, 5]])
connections_2nd_2_3i = np.array([[3, 4]])
connections_2nd_2_3 = combine_connections(4, connections_2nd_2_3g, connections_2nd_2_3i)

points_2nd_2_4 = np.array([[0, 1], [0, 3], [1, 1], [2, 3], [3, 1], [3, 3]])
connections_2nd_2_4g = np.array([[1, 4], [2, 3], [3, 5], [4, 6]])
connections_2nd_2_4i = np.array([[3, 4]])
connections_2nd_2_4 = combine_connections(4, connections_2nd_2_4g, connections_2nd_2_4i)

points_2nd_2_5 = np.array([[0, 1], [0, 3], [1, 3], [2, 1], [3, 1], [3, 3]])
connections_2nd_2_5g = np.array([[1, 3], [2, 4], [3, 6], [4, 5]])
connections_2nd_2_5i = np.array([[3, 4]])
connections_2nd_2_5 = combine_connections(4, connections_2nd_2_5g, connections_2nd_2_5i)

points_2nd_3_1 = np.array([[0, 1], [2, 3], [3, 4], [4, 1], [4, 3], [4, 5]])
connections_2nd_3_1g = np.array([[1, 2], [2, 4], [3, 5], [3, 6]])
connections_2nd_3_1i = np.array([[2, 3]])
connections_2nd_3_1 = combine_connections(4, connections_2nd_3_1g, connections_2nd_3_1i)

points_2nd_3_2 = np.array([[0, 1], [2, 3], [3, 2], [4, 1], [4, 3], [4, 5]])
connections_2nd_3_2g = np.array([[1, 2], [3, 4], [3, 5], [2, 6]])
connections_2nd_3_2i = np.array([[2, 3]])
connections_2nd_3_2 = combine_connections(4, connections_2nd_3_2g, connections_2nd_3_2i)

points_2nd_3_3 = np.array([[0, 1], [2, 3], [3, 4], [4, 1], [4, 3], [4, 5]])
connections_2nd_3_3g = np.array([[1, 2], [3, 4], [2, 5], [3, 6]])
connections_2nd_3_3i = np.array([[2, 3]])
connections_2nd_3_3 = combine_connections(4, connections_2nd_3_3g, connections_2nd_3_3i)

can_points_2nd = np.empty((11, max(len(points_2nd_1_1), len(points_2nd_1_2), len(points_2nd_1_3)), 2))
can_points_2nd[0] = points_2nd_1_1
can_points_2nd[1] = points_2nd_1_2
can_points_2nd[2] = points_2nd_1_3
can_points_2nd[3] = points_2nd_2_1
can_points_2nd[4] = points_2nd_2_2
can_points_2nd[5] = points_2nd_2_3
can_points_2nd[6] = points_2nd_2_4
can_points_2nd[7] = points_2nd_2_5
can_points_2nd[8] = points_2nd_3_1
can_points_2nd[9] = points_2nd_3_2
can_points_2nd[10] = points_2nd_3_3

can_connections_2nd = np.empty((11, max(len(connections_2nd_1_1), len(connections_2nd_1_2), len(connections_2nd_1_3)), max(len(connections_2nd_1_1[0]), len(connections_2nd_1_2[0]), len(connections_2nd_1_3[0])), 2), dtype=int)
can_connections_2nd[0] = connections_2nd_1_1
can_connections_2nd[1] = connections_2nd_1_2
can_connections_2nd[2] = connections_2nd_1_3
can_connections_2nd[3] = connections_2nd_2_1
can_connections_2nd[4] = connections_2nd_2_2
can_connections_2nd[5] = connections_2nd_2_3
can_connections_2nd[6] = connections_2nd_2_4
can_connections_2nd[7] = connections_2nd_2_5
can_connections_2nd[8] = connections_2nd_3_1
can_connections_2nd[9] = connections_2nd_3_2
can_connections_2nd[10] = connections_2nd_3_3

can_number_2nd = np.array([[1], [1], [1], [1], [1], [1], [1], [1], [1], [1], [1]])

can_points = [can_points_1st, can_points_2nd]
can_connections = [can_connections_1st, can_connections_2nd]
can_count = [can_number_1st, can_number_2nd]