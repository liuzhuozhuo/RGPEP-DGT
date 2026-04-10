import numpy as np

from src.transforms.format import combine_connections # Used to combine different types of connections (particles) into a single array

points_1 = np.array([[0, 1], [0, 3], [1, 2], [2, 1], [2, 3]])
connection_1 = np.array([[[1, 3], [2, 3], [3, 4], [3, 5]], [[0, 0], [0, 0], [0, 0], [0, 0]]])

points_2 = np.array([[0, 1], [0, 2], [0, 3], [1, 2], [2, 2]])
connection_2 = np.array([[[1, 4], [2, 4], [3, 4], [4, 5]], [[0, 0], [0, 0], [0, 0], [0, 0]]])

points_3 = np.array([[0, 2], [1, 2], [2, 1], [2, 2], [2, 3]])
connection_3 = np.array([[[1, 2], [2, 3], [2, 4], [2, 5]], [[0, 0], [0, 0], [0, 0], [0, 0]]])

can_points = [[points_1, points_2, points_3]]
can_connections = [[connection_1, connection_2, connection_3]]
can_count = [[1, 1, 1]]