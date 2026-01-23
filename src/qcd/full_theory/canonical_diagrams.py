import numpy as np

from src.transforms.format import combine_connections # Used to combine different types of connections (particles) into a single array

"""
First order
"""
# H_A^3
points_1st_1 = np.array([[0, 1], [0, 3], [1, 2], [2, 2]])
connections_1st_1g = np.array([[1, 3], [2, 3], [3, 4]]) 
connections_1st_1i = np.array([[0, 0]])
connections_1st_1p = np.array([[0, 0]])
connections_1st_1a = np.array([[0, 0]])
connections_1st_1 = combine_connections(3, connections_1st_1g, connections_1st_1i, connections_1st_1p, connections_1st_1a)

points_1st_2 = np.array([[0, 2], [1, 2], [2, 1], [2, 3]])
connections_1st_2g = np.array([[1, 2], [2, 3], [2, 4]]) 
connections_1st_2i = np.array([[0, 0]])
connections_1st_2p = np.array([[0, 0]])
connections_1st_2a = np.array([[0, 0]])
connections_1st_2 = combine_connections(3, connections_1st_2g, connections_1st_2i, connections_1st_2p, connections_1st_2a)

# H_ψAψ
points_1st_3 = np.array([[0, 1], [0, 3], [1, 2], [2, 2]])
connections_1st_3g = np.array([[1, 3]])
connections_1st_3i = np.array([[0, 0]])
connections_1st_3p = np.array([[2, 3], [3, 4]])
connections_1st_3a = np.array([[0, 0]])
connections_1st_3 = combine_connections(3, connections_1st_3g, connections_1st_3i, connections_1st_3p, connections_1st_3a) #b†a†b

points_1st_4 = np.array([[0, 2], [1, 2], [2, 1], [2, 3]])
connections_1st_4g = np.array([[2, 3]])
connections_1st_4i = np.array([[0, 0]])
connections_1st_4p = np.array([[1, 2], [2, 4]])
connections_1st_4a = np.array([[0, 0]])
connections_1st_4 = combine_connections(3, connections_1st_4g, connections_1st_4i, connections_1st_4p, connections_1st_4a) #b†ab

points_1st_5 = np.array([[0, 1], [0, 3], [1, 2], [2, 2]])
connections_1st_5g = np.array([[1, 3]])
connections_1st_5i = np.array([[0, 0]])
connections_1st_5p = np.array([[0, 0]])
connections_1st_5a = np.array([[2, 3], [3, 4]])
connections_1st_5 = combine_connections(3, connections_1st_5g, connections_1st_5i, connections_1st_5p, connections_1st_5a)#d†a†d

points_1st_6 = np.array([[0, 2], [1, 2], [2, 1], [2, 3]])
connections_1st_6g = np.array([[2, 3]])
connections_1st_6i = np.array([[0, 0]])
connections_1st_6p = np.array([[0, 0]])
connections_1st_6a = np.array([[1, 2], [2, 4]])
connections_1st_6 = combine_connections(3, connections_1st_6g, connections_1st_6i, connections_1st_6p, connections_1st_6a) #d†ad

points_1st_7 = np.array([[0, 1], [0, 3], [1, 2], [2, 2]])
connections_1st_7g = np.array([[3, 4]])
connections_1st_7i = np.array([[0, 0]])
connections_1st_7p = np.array([[2, 3]])
connections_1st_7a = np.array([[1, 3]])
connections_1st_7 = combine_connections(3, connections_1st_7g, connections_1st_7i, connections_1st_7p, connections_1st_7a) #b†d†a

points_1st_8 = np.array([[0, 2], [1, 2], [2, 1], [2, 3]])
connections_1st_8g = np.array([[1, 2]])
connections_1st_8i = np.array([[0, 0]])
connections_1st_8p = np.array([[2, 3]])
connections_1st_8a = np.array([[2, 4]])
connections_1st_8 = combine_connections(3, connections_1st_8g, connections_1st_8i, connections_1st_8p, connections_1st_8a) #a†db

can_points_1st = np.empty((8, max(len(points_1st_1), len(points_1st_2), len(points_1st_3), len(points_1st_4), len(points_1st_5), len(points_1st_6), len(points_1st_7), len(points_1st_8)), 2))
can_points_1st[0] = points_1st_1
can_points_1st[1] = points_1st_2
can_points_1st[2] = points_1st_3
can_points_1st[3] = points_1st_4
can_points_1st[4] = points_1st_5
can_points_1st[5] = points_1st_6
can_points_1st[6] = points_1st_7
can_points_1st[7] = points_1st_8

can_connections_1st = np.zeros((8, max(len(connections_1st_1), len(connections_1st_2), len(connections_1st_3), len(connections_1st_4), len(connections_1st_5), len(connections_1st_6), len(connections_1st_7), len(connections_1st_8)), max(len(connections_1st_1[0]), len(connections_1st_2[0]), len(connections_1st_3[0]), len(connections_1st_4[0]), len(connections_1st_5[0]), len(connections_1st_6[0]), len(connections_1st_7[0]), len(connections_1st_8[0])), 2), dtype=int)
can_connections_1st[0] = connections_1st_1
can_connections_1st[1] = connections_1st_2
can_connections_1st[2] = connections_1st_3
can_connections_1st[3] = connections_1st_4
can_connections_1st[4] = connections_1st_5
can_connections_1st[5] = connections_1st_6
can_connections_1st[6] = connections_1st_7
can_connections_1st[7] = connections_1st_8

can_number_1st = np.array([[1], [1], [1], [1], [1], [1], [1], [1]])

""""
Second order
"""

"""# H_A^4"""
"#1 to 3"
points_2nd_1_1 = np.array([[0, 1], [0, 3], [0, 5], [1, 4], [2, 3], [4, 1]])
connections_2nd_1_1g = np.array([[1, 5], [2, 4], [3, 4], [5, 6]])
connections_2nd_1_1i = np.array([[4, 5]])
connections_2nd_1_1p = np.array([[0, 0]])
connections_2nd_1_1a = np.array([[0, 0]])
connections_2nd_1_1 = combine_connections(4, connections_2nd_1_1g, connections_2nd_1_1i, connections_2nd_1_1p, connections_2nd_1_1a) #a†a†a†a

points_2nd_1_2 = np.array([[0, 1], [0, 3], [0, 5], [1, 2], [2, 3], [4, 1]])
connections_2nd_1_2g = np.array([[1, 4], [2, 4], [3, 5], [5, 6]])
connections_2nd_1_2i = np.array([[4, 5]])
connections_2nd_1_2p = np.array([[0, 0]])
connections_2nd_1_2a = np.array([[0, 0]])
connections_2nd_1_2 = combine_connections(4, connections_2nd_1_2g, connections_2nd_1_2i, connections_2nd_1_2p, connections_2nd_1_2a) #a†a†a†a

points_2nd_1_3 = np.array([[0, 1], [0, 3], [0, 5], [1, 4], [2, 3], [4, 1]])
connections_2nd_1_3g = np.array([[1, 4], [2, 5], [3, 4], [5, 6]])
connections_2nd_1_3i = np.array([[4, 5]])
connections_2nd_1_3p = np.array([[0, 0]])
connections_2nd_1_3a = np.array([[0, 0]])
connections_2nd_1_3 = combine_connections(4, connections_2nd_1_3g, connections_2nd_1_3i, connections_2nd_1_3p, connections_2nd_1_3a) #a†a†a†a

"#2 to 2"
points_2nd_2_1 = np.array([[0, 1], [0, 3], [1, 2], [2, 2], [3, 1], [3, 3]])
connections_2nd_2_1g = np.array([[1, 3], [2, 3], [4, 5], [4, 6]])
connections_2nd_2_1i = np.array([[3, 4]])
connections_2nd_2_1p = np.array([[0, 0]])
connections_2nd_2_1a = np.array([[0, 0]])
connections_2nd_2_1 = combine_connections(4, connections_2nd_2_1g, connections_2nd_2_1i, connections_2nd_2_1p, connections_2nd_2_1a) #a†a†aa s-type

points_2nd_2_2 = np.array([[0, 1], [0, 3], [1, 1], [2, 3], [3, 1], [3, 3]])
connections_2nd_2_2g = np.array([[1, 3], [2, 4], [3, 5], [4, 6]])
connections_2nd_2_2i = np.array([[3, 4]])
connections_2nd_2_2p = np.array([[0, 0]])
connections_2nd_2_2a = np.array([[0, 0]])
connections_2nd_2_2 = combine_connections(4, connections_2nd_2_2g, connections_2nd_2_2i, connections_2nd_2_2p, connections_2nd_2_2a) #a†a†aa t-type

points_2nd_2_3 = np.array([[0, 1], [0, 3], [1, 3], [2, 1], [3, 1], [3, 3]])
connections_2nd_2_3g = np.array([[1, 4], [2, 3], [3, 6], [4, 5]])
connections_2nd_2_3i = np.array([[3, 4]])
connections_2nd_2_3p = np.array([[0, 0]])
connections_2nd_2_3a = np.array([[0, 0]])
connections_2nd_2_3 = combine_connections(4, connections_2nd_2_3g, connections_2nd_2_3i, connections_2nd_2_3p, connections_2nd_2_3a) #a†a†aa t-type

points_2nd_2_4 = np.array([[0, 1], [0, 3], [1, 1], [2, 3], [3, 1], [3, 3]])
connections_2nd_2_4g = np.array([[1, 4], [2, 3], [3, 5], [4, 6]])
connections_2nd_2_4i = np.array([[3, 4]])
connections_2nd_2_4p = np.array([[0, 0]])
connections_2nd_2_4a = np.array([[0, 0]])
connections_2nd_2_4 = combine_connections(4, connections_2nd_2_4g, connections_2nd_2_4i, connections_2nd_2_4p, connections_2nd_2_4a) #a†a†aa u-type

points_2nd_2_5 = np.array([[0, 1], [0, 3], [1, 3], [2, 1], [3, 1], [3, 3]])
connections_2nd_2_5g = np.array([[1, 3], [2, 4], [3, 6], [4, 5]])
connections_2nd_2_5i = np.array([[3, 4]])
connections_2nd_2_5p = np.array([[0, 0]])
connections_2nd_2_5a = np.array([[0, 0]])
connections_2nd_2_5 = combine_connections(4, connections_2nd_2_5g, connections_2nd_2_5i, connections_2nd_2_5p, connections_2nd_2_5a)#a†a†aa u-type

"#3 to 1"
points_2nd_3_1 = np.array([[0, 1], [2, 3], [3, 4], [4, 1], [4, 3], [4, 5]])
connections_2nd_3_1g = np.array([[1, 2], [2, 4], [3, 5], [3, 6]])
connections_2nd_3_1i = np.array([[2, 3]])
connections_2nd_3_1p = np.array([[0, 0]])
connections_2nd_3_1a = np.array([[0, 0]])
connections_2nd_3_1 = combine_connections(4, connections_2nd_3_1g, connections_2nd_3_1i, connections_2nd_3_1p, connections_2nd_3_1a) #a†aaa

points_2nd_3_2 = np.array([[0, 1], [2, 3], [3, 2], [4, 1], [4, 3], [4, 5]])
connections_2nd_3_2g = np.array([[1, 2], [3, 4], [3, 5], [2, 6]])
connections_2nd_3_2i = np.array([[2, 3]])
connections_2nd_3_2p = np.array([[0, 0]])
connections_2nd_3_2a = np.array([[0, 0]])
connections_2nd_3_2 = combine_connections(4, connections_2nd_3_2g, connections_2nd_3_2i, connections_2nd_3_2p, connections_2nd_3_2a) #a†aaa

points_2nd_3_3 = np.array([[0, 1], [2, 3], [3, 4], [4, 1], [4, 3], [4, 5]])
connections_2nd_3_3g = np.array([[1, 2], [3, 4], [2, 5], [3, 6]])
connections_2nd_3_3i = np.array([[2, 3]])
connections_2nd_3_3p = np.array([[0, 0]])
connections_2nd_3_3a = np.array([[0, 0]])
connections_2nd_3_3 = combine_connections(4, connections_2nd_3_3g, connections_2nd_3_3i, connections_2nd_3_3p, connections_2nd_3_3a) #a†aaa

"""H_ψA^2ψ"""
"2 to 2 "
points_2nd_4_1 = np.array([[0, 1], [0, 3], [1, 2], [2, 2], [3, 1], [3, 3]])
connections_2nd_4_1g = np.array([[2, 3], [4, 6]])
connections_2nd_4_1i = np.array([[3, 4]])
connections_2nd_4_1p = np.array([[1, 3], [4, 5]])
connections_2nd_4_1a = np.array([[0, 0]])
connections_2nd_4_1 = combine_connections(4, connections_2nd_4_1g, connections_2nd_4_1i, connections_2nd_4_1p, connections_2nd_4_1a) #b†a†ab s-type

points_2nd_4_2 = np.array([[0, 1], [0, 3], [1, 2], [2, 2], [3, 1], [3, 3]])
connections_2nd_4_2g = np.array([[2, 3], [4, 6]])
connections_2nd_4_2i = np.array([[3, 4]])
connections_2nd_4_2p = np.array([[0, 0]])
connections_2nd_4_2a = np.array([[1, 3], [4, 5]])
connections_2nd_4_2 = combine_connections(4, connections_2nd_4_2g, connections_2nd_4_2i, connections_2nd_4_2p, connections_2nd_4_2a) #d†a†ad s-type

points_2nd_4_3 = np.array([[0, 1], [0, 3], [1, 3], [2, 1], [3, 1], [3, 3]])
connections_2nd_4_3g = np.array([[1, 4], [3, 6]])
connections_2nd_4_3i = np.array([[3, 4]])
connections_2nd_4_3p = np.array([[2, 3], [4, 5]])
connections_2nd_4_3a = np.array([[0, 0]])
connections_2nd_4_3 = combine_connections(4, connections_2nd_4_3g, connections_2nd_4_3i, connections_2nd_4_3p, connections_2nd_4_3a) #b†a†ab t-type

points_2nd_4_4 = np.array([[0, 1], [0, 3], [1, 3], [2, 1], [3, 1], [3, 3]])
connections_2nd_4_4g = np.array([[1, 4], [3, 6]])
connections_2nd_4_4i = np.array([[3, 4]])
connections_2nd_4_4p = np.array([[0, 0]])
connections_2nd_4_4a = np.array([[2, 3], [4, 5]])
connections_2nd_4_4 = combine_connections(4, connections_2nd_4_4g, connections_2nd_4_4i, connections_2nd_4_4p, connections_2nd_4_4a) #d†a†ad t-type

points_2nd_4_5 = np.array([[0, 1], [0, 3], [1, 3], [2, 1], [3, 1], [3, 3]])
connections_2nd_4_5g = np.array([[2, 3], [1, 4]])
connections_2nd_4_5i = np.array([[3, 4]])
connections_2nd_4_5p = np.array([[3, 6]])
connections_2nd_4_5a = np.array([[4, 5]])
connections_2nd_4_5 = combine_connections(4, connections_2nd_4_5g, connections_2nd_4_5i, connections_2nd_4_5p, connections_2nd_4_5a) #b†d†aa t-type

points_2nd_4_6 = np.array([[0, 1], [0, 3], [1, 3], [2, 1], [3, 1], [3, 3]])
connections_2nd_4_6g = np.array([[3, 6], [4, 5]])
connections_2nd_4_6i = np.array([[3, 4]])
connections_2nd_4_6p = np.array([[2, 3]])
connections_2nd_4_6a = np.array([[1, 4]])
connections_2nd_4_6 = combine_connections(4, connections_2nd_4_6g, connections_2nd_4_6i, connections_2nd_4_6p, connections_2nd_4_6a) #d†a†ad t-type

points_2nd_4_7 = np.array([[0, 1], [0, 3], [1, 3], [2, 1], [3, 1], [3, 3]])
connections_2nd_4_7g = np.array([[2, 4], [1, 3]])
connections_2nd_4_7i = np.array([[3, 4]])
connections_2nd_4_7p = np.array([[3, 6]])
connections_2nd_4_7a = np.array([[4, 5]])
connections_2nd_4_7 = combine_connections(4, connections_2nd_4_7g, connections_2nd_4_7i, connections_2nd_4_7p, connections_2nd_4_7a) #b†d†aa u-type

points_2nd_4_8 = np.array([[0, 1], [0, 3], [1, 3], [2, 1], [3, 1], [3, 3]])
connections_2nd_4_8g = np.array([[3, 5], [4, 6]])
connections_2nd_4_8i = np.array([[3, 4]])
connections_2nd_4_8p = np.array([[2, 3]])
connections_2nd_4_8a = np.array([[1, 4]])
connections_2nd_4_8 = combine_connections(4, connections_2nd_4_8g, connections_2nd_4_8i, connections_2nd_4_8p, connections_2nd_4_8a) #d†a†ad u-type

"#1 to 3"
points_2nd_5_1 = np.array([[0, 1], [0, 3], [0, 5], [1, 4], [2, 3], [4, 1]])
connections_2nd_5_1g = np.array([[2, 4], [5, 6]])
connections_2nd_5_1i = np.array([[4, 5]])
connections_2nd_5_1p = np.array([[3, 4]])
connections_2nd_5_1a = np.array([[1, 5]])
connections_2nd_5_1 = combine_connections(4, connections_2nd_5_1g, connections_2nd_5_1i, connections_2nd_5_1p, connections_2nd_5_1a) 

points_2nd_5_2 = np.array([[0, 1], [0, 3], [0, 5], [1, 2], [2, 3], [4, 1]])
connections_2nd_5_2g = np.array([[2, 4], [5, 6]])
connections_2nd_5_2i = np.array([[4, 5]])
connections_2nd_5_2p = np.array([[3, 5]])
connections_2nd_5_2a = np.array([[1, 4]])
connections_2nd_5_2 = combine_connections(4, connections_2nd_5_2g, connections_2nd_5_2i, connections_2nd_5_2p, connections_2nd_5_2a)

points_2nd_5_3 = np.array([[0, 1], [0, 3], [0, 5], [1, 4], [2, 3], [4, 1]])
connections_2nd_5_3g = np.array([[1, 5], [2, 4]])
connections_2nd_5_3i = np.array([[4, 5]])
connections_2nd_5_3p = np.array([[5, 6], [3, 4]])
connections_2nd_5_3a = np.array([[0, 0]])
connections_2nd_5_3 = combine_connections(4, connections_2nd_5_3g, connections_2nd_5_3i, connections_2nd_5_3p, connections_2nd_5_3a)

points_2nd_5_4 = np.array([[0, 1], [0, 3], [0, 5], [1, 4], [2, 3], [4, 1]])
connections_2nd_5_4g = np.array([[1, 4], [2, 5]])
connections_2nd_5_4i = np.array([[4, 5]])
connections_2nd_5_4p = np.array([[5, 6], [3, 4]])
connections_2nd_5_4a = np.array([[0, 0]])
connections_2nd_5_4 = combine_connections(4, connections_2nd_5_4g, connections_2nd_5_4i, connections_2nd_5_4p, connections_2nd_5_4a)

points_2nd_5_5 = np.array([[0, 1], [0, 3], [0, 5], [1, 4], [2, 3], [4, 1]])
connections_2nd_5_5g = np.array([[1, 5], [2, 4]])
connections_2nd_5_5i = np.array([[4, 5]])
connections_2nd_5_5p = np.array([[0, 0]])
connections_2nd_5_5a = np.array([[5, 6], [3, 4]])
connections_2nd_5_5 = combine_connections(4, connections_2nd_5_5g, connections_2nd_5_5i, connections_2nd_5_5p, connections_2nd_5_5a)

points_2nd_5_6 = np.array([[0, 1], [0, 3], [0, 5], [1, 4], [2, 3], [4, 1]])
connections_2nd_5_6g = np.array([[1, 4], [2, 5]])
connections_2nd_5_6i = np.array([[4, 5]])
connections_2nd_5_6p = np.array([[0, 0]])
connections_2nd_5_6a = np.array([[5, 6], [3, 4]])
connections_2nd_5_6 = combine_connections(4, connections_2nd_5_6g, connections_2nd_5_6i, connections_2nd_5_6p, connections_2nd_5_6a)

"3 to 1"
points_2nd_6_1 = np.array([[0, 1], [2, 3], [3, 4], [4, 1], [4, 3], [4, 5]])
connections_2nd_6_1g = np.array([[1, 2], [3, 5]])
connections_2nd_6_1i = np.array([[2, 3]])
connections_2nd_6_1p = np.array([[2, 4]])
connections_2nd_6_1a = np.array([[3, 6]])
connections_2nd_6_1 = combine_connections(4, connections_2nd_6_1g, connections_2nd_6_1i, connections_2nd_6_1p, connections_2nd_6_1a)

points_2nd_6_2 = np.array([[0, 1], [2, 3], [3, 2], [4, 1], [4, 3], [4, 5]])
connections_2nd_6_2g = np.array([[1, 2], [3, 5]])
connections_2nd_6_2i = np.array([[2, 3]])
connections_2nd_6_2p = np.array([[3, 4]])
connections_2nd_6_2a = np.array([[2, 6]])
connections_2nd_6_2 = combine_connections(4, connections_2nd_6_2g, connections_2nd_6_2i, connections_2nd_6_2p, connections_2nd_6_2a)

points_2nd_6_3 = np.array([[0, 1], [2, 3], [3, 4], [4, 1], [4, 3], [4, 5]])
connections_2nd_6_3g = np.array([[2, 4], [3, 5]])
connections_2nd_6_3i = np.array([[2, 3]])
connections_2nd_6_3p = np.array([[1, 2], [3, 6]])
connections_2nd_6_3a = np.array([[0, 0]])
connections_2nd_6_3 = combine_connections(4, connections_2nd_6_3g, connections_2nd_6_3i, connections_2nd_6_3p, connections_2nd_6_3a)

points_2nd_6_4 = np.array([[0, 1], [2, 3], [3, 4], [4, 1], [4, 3], [4, 5]])
connections_2nd_6_4g = np.array([[2, 5], [3, 4]])
connections_2nd_6_4i = np.array([[2, 3]])
connections_2nd_6_4p = np.array([[1, 2], [3, 6]])
connections_2nd_6_4a = np.array([[0, 0]])
connections_2nd_6_4 = combine_connections(4, connections_2nd_6_4g, connections_2nd_6_4i, connections_2nd_6_4p, connections_2nd_6_4a)

points_2nd_6_5 = np.array([[0, 1], [2, 3], [3, 4], [4, 1], [4, 3], [4, 5]])
connections_2nd_6_5g = np.array([[2, 4], [3, 5]])
connections_2nd_6_5i = np.array([[2, 3]])
connections_2nd_6_5p = np.array([[0, 0]])
connections_2nd_6_5a = np.array([[1, 2], [3, 6]])
connections_2nd_6_5 = combine_connections(4, connections_2nd_6_5g, connections_2nd_6_5i, connections_2nd_6_5p, connections_2nd_6_5a)

points_2nd_6_6 = np.array([[0, 1], [2, 3], [3, 4], [4, 1], [4, 3], [4, 5]])
connections_2nd_6_6g = np.array([[2, 5], [3, 4]])
connections_2nd_6_6i = np.array([[2, 3]])
connections_2nd_6_6p = np.array([[0, 0]])
connections_2nd_6_6a = np.array([[1, 2], [3, 6]])
connections_2nd_6_6 = combine_connections(4, connections_2nd_6_6g, connections_2nd_6_6i, connections_2nd_6_6p, connections_2nd_6_6a)

"""H_∂AAψψ""" 
"2 to 2"
points_2nd_7_1 = np.array([[0, 1], [0, 3], [1, 2], [2, 2], [3, 1], [3, 3]])
connections_2nd_7_1g = np.array([[1, 3], [2, 3]])
connections_2nd_7_1i = np.array([[3, 4]])
connections_2nd_7_1p = np.array([[4, 5]])
connections_2nd_7_1a = np.array([[4, 6]])
connections_2nd_7_1 = combine_connections(4, connections_2nd_7_1g, connections_2nd_7_1i, connections_2nd_7_1p, connections_2nd_7_1a)

points_2nd_7_2 = np.array([[0, 1], [0, 3], [1, 2], [2, 2], [3, 1], [3, 3]])
connections_2nd_7_2g = np.array([[4, 5], [4, 6]])
connections_2nd_7_2i = np.array([[3, 4]])
connections_2nd_7_2p = np.array([[1, 3]])
connections_2nd_7_2a = np.array([[2, 3]])
connections_2nd_7_2 = combine_connections(4, connections_2nd_7_2g, connections_2nd_7_2i, connections_2nd_7_2p, connections_2nd_7_2a)

points_2nd_7_3 = np.array([[0, 1], [0, 3], [1, 1], [2, 3], [3, 1], [3, 3]])
connections_2nd_7_3g = np.array([[2, 4], [4, 6]])
connections_2nd_7_3i = np.array([[3, 4]])
connections_2nd_7_3p = np.array([[0, 0]])
connections_2nd_7_3a = np.array([[1, 3], [3, 5]])
connections_2nd_7_3 = combine_connections(4, connections_2nd_7_3g, connections_2nd_7_3i, connections_2nd_7_3p, connections_2nd_7_3a)

points_2nd_7_4 = np.array([[0, 1], [0, 3], [1, 1], [2, 3], [3, 1], [3, 3]])
connections_2nd_7_4g = np.array([[2, 4], [4, 6]])
connections_2nd_7_4i = np.array([[3, 4]])
connections_2nd_7_4p = np.array([[1, 3], [3, 5]])
connections_2nd_7_4a = np.array([[0, 0]])
connections_2nd_7_4 = combine_connections(4, connections_2nd_7_4g, connections_2nd_7_4i, connections_2nd_7_4p, connections_2nd_7_4a)

"#1 to 3"
points_2nd_8_1 = np.array([[0, 1], [0, 3], [0, 5], [1, 4], [2, 3], [4, 1]])
connections_2nd_8_1g = np.array([[2, 4], [3, 4]])
connections_2nd_8_1i = np.array([[4, 5]])
connections_2nd_8_1p = np.array([[1, 5], [5, 6]])
connections_2nd_8_1a = np.array([[0, 0]])
connections_2nd_8_1 = combine_connections(4, connections_2nd_8_1g, connections_2nd_8_1i, connections_2nd_8_1p, connections_2nd_8_1a)

points_2nd_8_2 = np.array([[0, 1], [0, 3], [0, 5], [1, 4], [2, 3], [4, 1]])
connections_2nd_8_2g = np.array([[2, 4], [3, 4]])
connections_2nd_8_2i = np.array([[4, 5]])
connections_2nd_8_2p = np.array([[0, 0]])
connections_2nd_8_2a = np.array([[1, 5], [5, 6]])
connections_2nd_8_2 = combine_connections(4, connections_2nd_8_2g, connections_2nd_8_2i, connections_2nd_8_2p, connections_2nd_8_2a)

points_2nd_8_3 = np.array([[0, 1], [0, 3], [0, 5], [1, 4], [2, 3], [4, 1]])
connections_2nd_8_3g = np.array([[1, 5], [5, 6]])
connections_2nd_8_3i = np.array([[4, 5]])
connections_2nd_8_3p = np.array([[3, 4]])
connections_2nd_8_3a = np.array([[2, 4]])
connections_2nd_8_3 = combine_connections(4, connections_2nd_8_3g, connections_2nd_8_3i, connections_2nd_8_3p, connections_2nd_8_3a)

"3 to 1"
points_2nd_9_1 = np.array([[0, 1], [2, 3], [3, 4], [4, 1], [4, 3], [4, 5]])
connections_2nd_9_1g = np.array([[3, 5], [3, 6]])
connections_2nd_9_1i = np.array([[2, 3]])
connections_2nd_9_1p = np.array([[1, 2], [2, 4]])
connections_2nd_9_1a = np.array([[0, 0]])
connections_2nd_9_1 = combine_connections(4, connections_2nd_9_1g, connections_2nd_9_1i, connections_2nd_9_1p, connections_2nd_9_1a)

points_2nd_9_2 = np.array([[0, 1], [2, 3], [3, 4], [4, 1], [4, 3], [4, 5]])
connections_2nd_9_2g = np.array([[3, 5], [3, 6]])
connections_2nd_9_2i = np.array([[2, 3]])
connections_2nd_9_2p = np.array([[0, 0]])
connections_2nd_9_2a = np.array([[1, 2], [2, 4]])
connections_2nd_9_2 = combine_connections(4, connections_2nd_9_2g, connections_2nd_9_2i, connections_2nd_9_2p, connections_2nd_9_2a)

points_2nd_9_3 = np.array([[0, 1], [2, 3], [3, 4], [4, 1], [4, 3], [4, 5]])
connections_2nd_9_3g = np.array([[1, 2], [2, 4]])
connections_2nd_9_3i = np.array([[2, 3]])
connections_2nd_9_3p = np.array([[3, 5]])
connections_2nd_9_3a = np.array([[3, 6]])
connections_2nd_9_3 = combine_connections(4, connections_2nd_9_3g, connections_2nd_9_3i, connections_2nd_9_3p, connections_2nd_9_3a)

"""H_(ψψ)2"""
"2 to 2"
points_2nd_10_1 = np.array([[0, 1], [0, 3], [1, 2], [2, 2], [3, 1], [3, 3]])
connections_2nd_10_1g = np.array([[0, 0]])
connections_2nd_10_1i = np.array([[3, 4]])
connections_2nd_10_1p = np.array([[1, 3], [4, 5]])
connections_2nd_10_1a = np.array([[2, 3], [4, 6]])
connections_2nd_10_1 = combine_connections(4, connections_2nd_10_1g, connections_2nd_10_1i, connections_2nd_10_1p, connections_2nd_10_1a)

points_2nd_10_2 = np.array([[0, 1], [0, 3], [1, 1], [2, 3], [3, 1], [3, 3]])
connections_2nd_10_2g = np.array([[0, 0]])
connections_2nd_10_2i = np.array([[3, 4]])
connections_2nd_10_2p = np.array([[2, 4], [4, 6]])
connections_2nd_10_2a = np.array([[1, 3], [3, 5]])
connections_2nd_10_2 = combine_connections(4, connections_2nd_10_2g, connections_2nd_10_2i, connections_2nd_10_2p, connections_2nd_10_2a)

points_2nd_10_3 = np.array([[0, 1], [0, 3], [1, 1], [2, 3], [3, 1], [3, 3]])
connections_2nd_10_3g = np.array([[0, 0]])
connections_2nd_10_3i = np.array([[3, 4]])
connections_2nd_10_3p = np.array([[1, 3], [3, 5], [2, 4], [4, 6]])
connections_2nd_10_3a = np.array([[0, 0]])
connections_2nd_10_3 = combine_connections(4, connections_2nd_10_3g, connections_2nd_10_3i, connections_2nd_10_3p, connections_2nd_10_3a)

points_2nd_10_4 = np.array([[0, 1], [0, 3], [1, 1], [2, 3], [3, 1], [3, 3]])
connections_2nd_10_4g = np.array([[0, 0]])
connections_2nd_10_4i = np.array([[3, 4]])
connections_2nd_10_4p = np.array([[0, 0]])
connections_2nd_10_4a = np.array([[1, 3], [3, 5], [2, 4], [4, 6]])
connections_2nd_10_4 = combine_connections(4, connections_2nd_10_4g, connections_2nd_10_4i, connections_2nd_10_4p, connections_2nd_10_4a)

points_2nd_10_5 = np.array([[0, 1], [0, 3], [1, 1], [2, 3], [3, 1], [3, 3]])
connections_2nd_10_5g = np.array([[0, 0]])
connections_2nd_10_5i = np.array([[3, 4]])
connections_2nd_10_5p = np.array([[0, 0]])
connections_2nd_10_5a = np.array([[1, 4], [3, 5], [2, 3], [4, 6]])
connections_2nd_10_5 = combine_connections(4, connections_2nd_10_5g, connections_2nd_10_5i, connections_2nd_10_5p, connections_2nd_10_5a)

points_2nd_10_6 = np.array([[0, 1], [0, 3], [1, 1], [2, 3], [3, 1], [3, 3]])
connections_2nd_10_6g = np.array([[0, 0]])
connections_2nd_10_6i = np.array([[3, 4]])
connections_2nd_10_6p = np.array([[1, 4], [3, 5], [2, 3], [4, 6]])
connections_2nd_10_6a = np.array([[0, 0]])
connections_2nd_10_6 = combine_connections(4, connections_2nd_10_6g, connections_2nd_10_6i, connections_2nd_10_6p, connections_2nd_10_6a)

"1 to 3"
points_2nd_11_1 = np.array([[0, 1], [0, 3], [0, 5], [1, 4], [2, 3], [4, 1]])
connections_2nd_11_1g = np.array([[0, 0]])
connections_2nd_11_1i = np.array([[4, 5]])
connections_2nd_11_1p = np.array([[2, 4], [1, 5], [5, 6]])
connections_2nd_11_1a = np.array([[3, 4]])
connections_2nd_11_1 = combine_connections(4, connections_2nd_11_1g, connections_2nd_11_1i, connections_2nd_11_1p, connections_2nd_11_1a)   

points_2nd_11_2 = np.array([[0, 1], [0, 3], [0, 5], [1, 4], [2, 3], [4, 1]])
connections_2nd_11_2g = np.array([[0, 0]])
connections_2nd_11_2i = np.array([[4, 5]])
connections_2nd_11_2p = np.array([[1, 4], [2, 5], [5, 6]])
connections_2nd_11_2a = np.array([[3, 4]])
connections_2nd_11_2 = combine_connections(4, connections_2nd_11_2g, connections_2nd_11_2i, connections_2nd_11_2p, connections_2nd_11_2a)   

points_2nd_11_3 = np.array([[0, 1], [0, 3], [0, 5], [1, 4], [2, 3], [4, 1]])
connections_2nd_11_3g = np.array([[0, 0]])
connections_2nd_11_3i = np.array([[4, 5]])
connections_2nd_11_3p = np.array([[3, 4]])
connections_2nd_11_3a = np.array([[2, 4], [1, 5], [5, 6]])
connections_2nd_11_3 = combine_connections(4, connections_2nd_11_3g, connections_2nd_11_3i, connections_2nd_11_3p, connections_2nd_11_3a)   

points_2nd_11_4 = np.array([[0, 1], [0, 3], [0, 5], [1, 4], [2, 3], [4, 1]])
connections_2nd_11_4g = np.array([[0, 0]])
connections_2nd_11_4i = np.array([[4, 5]])
connections_2nd_11_4p = np.array([[3, 4]])
connections_2nd_11_4a = np.array([[1, 4], [2, 5], [5, 6]])
connections_2nd_11_4 = combine_connections(4, connections_2nd_11_4g, connections_2nd_11_4i, connections_2nd_11_4p, connections_2nd_11_4a)   

"3 to 1"
points_2nd_12_1 = np.array([[0, 1], [2, 3], [3, 4], [4, 1], [4, 3], [4, 5]])
connections_2nd_12_1g = np.array([[0, 0]])
connections_2nd_12_1i = np.array([[2, 3]])
connections_2nd_12_1p = np.array([[1, 2], [2, 4], [3, 5]])
connections_2nd_12_1a = np.array([[3, 6]])
connections_2nd_12_1 = combine_connections(4, connections_2nd_12_1g, connections_2nd_12_1i, connections_2nd_12_1p, connections_2nd_12_1a)

points_2nd_12_2 = np.array([[0, 1], [2, 3], [3, 4], [4, 1], [4, 3], [4, 5]])
connections_2nd_12_2g = np.array([[0, 0]])
connections_2nd_12_2i = np.array([[2, 3]])
connections_2nd_12_2p = np.array([[1, 2], [2, 5], [3, 4]])
connections_2nd_12_2a = np.array([[3, 6]])
connections_2nd_12_2 = combine_connections(4, connections_2nd_12_2g, connections_2nd_12_2i, connections_2nd_12_2p, connections_2nd_12_2a)

points_2nd_12_3 = np.array([[0, 1], [2, 3], [3, 4], [4, 1], [4, 3], [4, 5]])
connections_2nd_12_3g = np.array([[0, 0]])
connections_2nd_12_3i = np.array([[2, 3]])
connections_2nd_12_3p = np.array([[3, 6]])
connections_2nd_12_3a = np.array([[1, 2], [2, 4], [3, 5]])
connections_2nd_12_3 = combine_connections(4, connections_2nd_12_3g, connections_2nd_12_3i, connections_2nd_12_3p, connections_2nd_12_3a)

points_2nd_12_4 = np.array([[0, 1], [2, 3], [3, 4], [4, 1], [4, 3], [4, 5]])
connections_2nd_12_4g = np.array([[0, 0]])
connections_2nd_12_4i = np.array([[2, 3]])
connections_2nd_12_4p = np.array([[3, 6]])
connections_2nd_12_4a = np.array([[1, 2], [2, 5], [3, 4]])
connections_2nd_12_4 = combine_connections(4, connections_2nd_12_4g, connections_2nd_12_4i, connections_2nd_12_4p, connections_2nd_12_4a)

n_2nd = 55

can_points_2nd = np.empty((n_2nd, max(len(points_2nd_1_1), len(points_2nd_1_2), len(points_2nd_1_3)), 2))
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
can_points_2nd[11] = points_2nd_4_1
can_points_2nd[12] = points_2nd_4_2
can_points_2nd[13] = points_2nd_4_3
can_points_2nd[14] = points_2nd_4_4
can_points_2nd[15] = points_2nd_4_5
can_points_2nd[16] = points_2nd_4_6
can_points_2nd[17] = points_2nd_4_7
can_points_2nd[18] = points_2nd_4_8
can_points_2nd[19] = points_2nd_5_1
can_points_2nd[20] = points_2nd_5_2
can_points_2nd[21] = points_2nd_5_3
can_points_2nd[22] = points_2nd_5_4
can_points_2nd[23] = points_2nd_5_5
can_points_2nd[24] = points_2nd_5_6
can_points_2nd[25] = points_2nd_6_1
can_points_2nd[26] = points_2nd_6_2
can_points_2nd[27] = points_2nd_6_3
can_points_2nd[28] = points_2nd_6_4
can_points_2nd[29] = points_2nd_6_5
can_points_2nd[30] = points_2nd_6_6
can_points_2nd[31] = points_2nd_7_1
can_points_2nd[32] = points_2nd_7_2
can_points_2nd[33] = points_2nd_7_3
can_points_2nd[34] = points_2nd_7_4
can_points_2nd[35] = points_2nd_8_1
can_points_2nd[36] = points_2nd_8_2
can_points_2nd[37] = points_2nd_8_3
can_points_2nd[38] = points_2nd_9_1
can_points_2nd[39] = points_2nd_9_2
can_points_2nd[40] = points_2nd_9_3
can_points_2nd[41] = points_2nd_10_1
can_points_2nd[42] = points_2nd_10_2
can_points_2nd[43] = points_2nd_10_3
can_points_2nd[44] = points_2nd_10_4
can_points_2nd[45] = points_2nd_10_5
can_points_2nd[46] = points_2nd_10_6
can_points_2nd[47] = points_2nd_11_1
can_points_2nd[48] = points_2nd_11_2
can_points_2nd[49] = points_2nd_11_3 
can_points_2nd[50] = points_2nd_11_4
can_points_2nd[51] = points_2nd_12_1
can_points_2nd[52] = points_2nd_12_2
can_points_2nd[53] = points_2nd_12_3
can_points_2nd[54] = points_2nd_12_4

can_connections_2nd = np.empty((n_2nd, max(len(connections_2nd_1_1), len(connections_2nd_1_2), len(connections_2nd_1_3)), max(len(connections_2nd_1_1[0]), len(connections_2nd_1_2[0]), len(connections_2nd_1_3[0])), 2), dtype=int)
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
can_connections_2nd[11] = connections_2nd_4_1
can_connections_2nd[12] = connections_2nd_4_2
can_connections_2nd[13] = connections_2nd_4_3
can_connections_2nd[14] = connections_2nd_4_4
can_connections_2nd[15] = connections_2nd_4_5
can_connections_2nd[16] = connections_2nd_4_6
can_connections_2nd[17] = connections_2nd_4_7
can_connections_2nd[18] = connections_2nd_4_8
can_connections_2nd[19] = connections_2nd_5_1
can_connections_2nd[20] = connections_2nd_5_2
can_connections_2nd[21] = connections_2nd_5_3
can_connections_2nd[22] = connections_2nd_5_4
can_connections_2nd[23] = connections_2nd_5_5
can_connections_2nd[24] = connections_2nd_5_6
can_connections_2nd[25] = connections_2nd_6_1
can_connections_2nd[26] = connections_2nd_6_2
can_connections_2nd[27] = connections_2nd_6_3
can_connections_2nd[28] = connections_2nd_6_4
can_connections_2nd[29] = connections_2nd_6_5
can_connections_2nd[30] = connections_2nd_6_6
can_connections_2nd[31] = connections_2nd_7_1
can_connections_2nd[32] = connections_2nd_7_2
can_connections_2nd[33] = connections_2nd_7_3
can_connections_2nd[34] = connections_2nd_7_4
can_connections_2nd[35] = connections_2nd_8_1
can_connections_2nd[36] = connections_2nd_8_2
can_connections_2nd[37] = connections_2nd_8_3
can_connections_2nd[38] = connections_2nd_9_1
can_connections_2nd[39] = connections_2nd_9_2
can_connections_2nd[40] = connections_2nd_9_3
can_connections_2nd[41] = connections_2nd_10_1
can_connections_2nd[42] = connections_2nd_10_2
can_connections_2nd[43] = connections_2nd_10_3
can_connections_2nd[44] = connections_2nd_10_4
can_connections_2nd[45] = connections_2nd_10_5
can_connections_2nd[46] = connections_2nd_10_6
can_connections_2nd[47] = connections_2nd_11_1
can_connections_2nd[48] = connections_2nd_11_2
can_connections_2nd[49] = connections_2nd_11_3 
can_connections_2nd[50] = connections_2nd_11_4
can_connections_2nd[51] = connections_2nd_12_1
can_connections_2nd[52] = connections_2nd_12_2
can_connections_2nd[53] = connections_2nd_12_3
can_connections_2nd[54] = connections_2nd_12_4