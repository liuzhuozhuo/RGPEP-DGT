import numpy as np
from scipy.special import binom, factorial

from src.transforms.format import trim_zeros_3D, trim_zeros_2D
from src.search.comparison import unique_values
from src.transforms.simplify import simplify_diagram

from src.qcd.full_theory.canonical_diagrams import can_points, can_connections, can_count

def in_out_connections (connections):
    max_len = max([len(path) for path in connections])
    #len(connections) is the number of type of particles
    in_out_connections = np.zeros((len(connections), 2, max_len), dtype=int)
    unique_vals = unique_values(connections.flatten())
    for i in range(len(connections)):
        inp = 0
        out = 0
        for j in range(max_len):
            if connections[i, j, 0] in unique_vals:
                in_out_connections[i, 1, out] = connections[i, j, 0]
                out += 1
            if connections[i, j, 1] in unique_vals:
                in_out_connections[i, 0, inp] = connections[i, j, 1]
                inp += 1
    in_out_connections = trim_zeros_3D(in_out_connections, axis=2)
    return in_out_connections

def how_connected(max_connections, n_connections, n_1, n_2):
    """
    Generate all possible combinations of connections between two diagrams.
    Args:
        max_connections (int): maximum number of connections between the two diagrams for each type of particle
        n_connections (int): number of connections between the two diagrams taking into account the number of types of particles
        n_1 (int): number of input for each type of particle
        n_2 (int): number of output for each type of particle
    Returns:
        combinations (np.array): array of all possible combinations of connections between the two diagrams
        of dimension (n_connections, max_connections, 2)
    """
    combinations = np.zeros((n_connections, max_connections, 2), dtype=int)
    n = 0 
    while n < n_connections:
        for j in range (n_1):
            for k in range(n_2):
                combinations[n, 0] = np.array([j+1, k+1])
                n += 1
                if n == n_connections:
                    break
            if n == n_connections:
                break
            
    n = n_1*n_2
    if max_connections >1:
        while n < n_connections:
            diff = False
            i = 1
            while i < max_connections:  
                for j in range (n_1):
                    for k in range(n_2):
                        for l in range(i):
                            if (j+1) != combinations[n, l, 0] and (k+1) != combinations[n, l, 1]:
                                diff = True
                            else:
                                diff = False
                        if diff:
                            combinations[n, i] = np.array([j+1, k+1])
                            n +=1   
                        if n == n_connections:
                            return combinations      
                i += 1
    else:
        return combinations
    
def make_connection (points1, connections1, points2, connections2, offset = 0):
    in_out_connections1 = in_out_connections(connections1)
    in_out_connections2 = in_out_connections(connections2)

    n_types = len(in_out_connections1)

    #Create the new points array
    points = np.zeros((len(points1) + len(points2), 2))
    points[:len(points1)] = points1
    points[len(points1):] = points2 + np.array([np.max(points1)+1, offset])

    #Displace the connections of the second diagram to rename the points
    for i in range(n_types):
        for j in range(len(in_out_connections2[0])):
            for k in range(len(in_out_connections2[0, 0])):
                if in_out_connections2[i, j, k] != 0:
                    in_out_connections2[i, j, k] += len(points1)

    #n1 and n2 indicate the number of input for each type of particle and output for each type of particle
    n1 = np.zeros(n_types, dtype=int)
    n2 = np.zeros(n_types, dtype=int)
    for i in range(n_types):
        n1[i] = len(np.trim_zeros(in_out_connections1[i, 0]))
        n2[i] = len(np.trim_zeros(in_out_connections2[i, 1]))

    #max_connections indicates the maximum number of connections between the two diagrams for each type of particle
    max_connections = np.zeros(n_types, dtype=int)
    for i in range(n_types):
        max_connections[i] = min(n1[i], n2[i])

    #n_connections indicates the number of connections between the two diagrams taking into account the number of types of particles
    n_connections = np.zeros(n_types, dtype=int)
    for j in range(n_types):
        for i in range(int(max_connections[j])):
            n_connections[j] += int(binom(n1[j], i+1)*binom(n2[j], i+1) * factorial(i+1))
    
    #n_connec indicates the total number of connections between the two diagrams
    n_connec = 0
    for subset in range(1, 1 << n_types):
        product = 1
        for i in range(n_types):
            if subset & (1 << i):
                product *= n_connections[i]
        n_connec += product

    #Use a dummy array to store all possible combinations of connections for each type of particle between the two diagrams
    dummy_combinations = np.zeros((sum(n_connections), n_types,  max(max_connections), 2), dtype=int)
    n = 0
    for i in range(n_types):
        dummy_var = how_connected(max_connections[i], n_connections[i], n1[i], n2[i])
        for j in range(n_connections[i]):
            for k in range(max_connections[i]):
                if(dummy_var[j, k, 0] != 0 and dummy_var[j, k, 1] != 0):
                    dummy_combinations[n, i, k] = dummy_var[j, k]
                else:
                    break
            n+=1

    #From the dummy array, create the array combinations that will store all possible combinations of connections between the two diagrams
    #taking into account mixing different types of particles
    combinations = np.zeros((n_connec, n_types, max(max_connections), 2), dtype=int)

    #The first step is to store a copy of the dummy array in the combinations array, without considering the mixing of different 
    #types of particles since there will be diagrams without mixed particles.
    n = 0
    for i in range(n_types):
        if (n_connections[i] == 0):
            continue
        for j in range(np.sum(n_connections[:i]), n_connections[i]+np.sum(n_connections[:i])):
            for k in range(max_connections[i]):
                if(dummy_combinations[j, i, k, 0] != 0 and dummy_combinations[j, i, k, 1] != 0):
                    combinations[n, i, k] = dummy_combinations[j, i, k]
                else:
                    break
            n+=1        

    #The second step is to store the combinations of connections between the two diagrams taking into account the mixing of 
    #different types of particles. The process could be though as filling a tringular matrix with the combinations of connections
    #between the two diagrams. The first row of the matrix corresponds to the one type case, the second row combining 2 elements of 
    #the first row, this means combining 2 types of particles, and so on.

    #The variable n_start indicates the position in the combinations array where the combinations of connections between 
    #the two diagrams taking into account the mixing of different types of particles start.
    n_start = n

    n_prime = 0
    for i in range(n_types-1):
        leng = 0
        for l in range(i+1, n_types):   
            leng += n_connections[i]*n_connections[l]
        for n in range(n_start, leng+n_start):
            combinations[n, i] = dummy_combinations[n_prime-1, i]
            for j in range(i+1, n_types):
                combinations[n, j] = dummy_combinations[n-n_start+n_connections[i]-1, j]
        n_prime += 1    
    #Create the connections array that will store the connections between the two diagrams.
    connections = np.zeros((n_connec, n_types, len(connections1[0]) + len(connections2[0]) + max(max_connections), 2), dtype=int)
    connections[:n_connec,:n_types,:len(connections1[0])] = connections1
    for i in range(n_connec):
        for j in range(n_types):
            for k in range(max_connections[j]):
                if (combinations[i,j, k, 0] != 0 and combinations[i,j, k, 1] != 0):
                    connections[i,j, len(connections1[0])+k] = np.array([in_out_connections1[j,0, combinations[i, j, k, 0]-1], in_out_connections2[j,1, combinations[i, j, k, 1]-1]])
            if (np.count_nonzero(connections2[j]) != 0):
                for k in range(len(connections2[j])):
                    if (connections2[j, k, 0] != 0 and connections2[j, k, 1] != 0):
                        connections[i,j, len(connections1[0])+max(max_connections)+k] = connections2[j, k] + np.array([len(points1), len(points1)])

    return points, connections

def combine_diagrams_order (points, connections, count, typeofproc, max_order, offset = 0):
    """
    Combine all the diagrams that would contribute to a give order, and type of interaction. If the order that is calculating is 
    the max_order intended, then it will try to skip products that definitely do not contribute.
    """

    #Similar to the one type of particle case, we need to first approximate the number of new diagrams that will produce.
    curr_order = len(points)
    n_types = len(connections[0][0])
    print(n_types)
    max_points = np.zeros((n_types, 2), dtype=int)

    n1 = np.zeros(n_types, dtype=int)
    n2 = np.zeros(n_types, dtype=int)
    for i in range(len(connections[0])): #in number of first order diagrams
        for j in range(n_types):
            n1[j] = len(np.trim_zeros(in_out_connections(connections[0][i])[j, 0]))
            if (n1[j] > max_points[j, 0]):
                max_points[j, 0] = n1[j]
            n2[j] = len(np.trim_zeros(in_out_connections(connections[0][i])[j, 1]))
            if (n2[j] > max_points[j, 1]):
                max_points[j, 1] = n2[j]            
    for i in range(len(connections[-1])):
        for j in range(n_types):
            n1[j] = len(np.trim_zeros(in_out_connections(connections[-1][i])[j, 0]))
            if (n1[j] > max_points[j, 0]):
                max_points[j, 0] = n1[j]
            n2[j] = len(np.trim_zeros(in_out_connections(connections[-1][i])[j, 1]))
            if (n2[j] > max_points[j, 1]):
                max_points[j, 1] = n2[j]

    max_connections = np.zeros(n_types, dtype=int)
    for i in range(n_types):
        max_connections[i] = min(max_points[i, 0], max_points[i, 1])

    n_connec = 0
    n_connections = np.zeros(n_types, dtype=int)
    for i in range(len(connections[0])):
        for j in range(n_types):
            for k in range(int(max_connections[j])):
                n_connections[j] += int(binom(n1[j], i+1)*binom(n2[j], k+1) * factorial(k+1))
        #n_connec indicates the total number of connections between the two diagrams
        for subset in range(1, 1 << n_types):
            product = 1
            for i in range(n_types):
                if subset & (1 << k):
                    product *= n_connections[k]
            n_connec += product
    n = 0
    f = 20

    new_points = np.zeros((4*n_types*len(connections[0])*len(connections[-1])*n_connec*(curr_order+1), len(points[0][0]) + len(points[-1][0]), 2))
    new_connections = np.zeros((4*n_types*len(connections[0])*len(connections[-1])*n_connec*(curr_order+1), n_types, len(connections[0][0]) + len(connections[-1][0])+np.max(max_connections)+5, 2), dtype=int)
    new_count = np.zeros((4*n_types*len(connections[0])*len(connections[-1])*n_connec*(curr_order+1), 1), dtype=int)

    for i in range(len(connections[0])):
        for j in range(len(connections[-1])):
            dummy_points, dummy_connections = make_connection(trim_zeros_2D(points[-1][j]), trim_zeros_3D(connections[-1][j], axis = 1),trim_zeros_2D(points[0][i]), trim_zeros_3D(connections[0][i], axis=1), offset=offset)
            for k in range(len(dummy_connections)):
                if(curr_order+1  == max_order): 
                    in_out_path = in_out_connections(dummy_connections[k])
                    if (len(np.trim_zeros(in_out_path[0, 0])) != typeofproc[0][1] or len(np.trim_zeros(in_out_path[0, 1]))!= typeofproc[0][0]):
                        continue
                simp_points, simp_connections = simplify_diagram(dummy_points, trim_zeros_3D(dummy_connections[k], axis=1))
                for l in range(len(simp_points)):
                    new_points[n, l] = simp_points[l]
                for l in range(n_types):
                    for m in range(len(simp_connections[0])):
                        new_connections[n, l, m] = simp_connections[l, m]
                new_count[n] = count[0][i] * count[-1][j]
                n += 1
            if (curr_order-1 < len(can_connections)):
                dummy_points, dummy_connections = make_connection(trim_zeros_2D(points[0][i]), trim_zeros_3D(connections[0][i], axis=1),trim_zeros_2D(points[-1][j]), trim_zeros_3D(connections[-1][j], axis = 1), offset=offset)
                for k in range(len(dummy_connections)):
                    if(curr_order+1  == max_order): 
                        in_out_path = in_out_connections(dummy_connections[k])
                        if (len(np.trim_zeros(in_out_path[0, 0])) != typeofproc[0][1] or len(np.trim_zeros(in_out_path[0, 1]))!= typeofproc[0][0]):
                            continue
                    simp_points, simp_connections = simplify_diagram(dummy_points, trim_zeros_3D(dummy_connections[k], axis=1))
                    for l in range(len(simp_points)):
                        new_points[n, l] = simp_points[l]
                    for l in range(n_types):
                        for m in range(len(simp_connections[0])):
                            new_connections[n, l, m] = simp_connections[l, m]
                    new_count[n] = count[0][i] * count[-1][j]
                    n += 1
    for i in range(1, 2):
        for j in range(i-1, len(connections)):
            if (i+1 + j) == curr_order:
                for k in range(len(can_connections[i])):
                    for l in range(len(connections[j])):
                        dummy_points, dummy_connections = make_connection(trim_zeros_2D(can_points[i][k]), trim_zeros_3D(can_connections[i][k], axis=1), trim_zeros_2D(points[j][l]), trim_zeros_3D(connections[j][l], axis = 1), offset=offset)
                        for m in range(len(dummy_connections)):
                            if(curr_order+1  == max_order): 
                                in_out_path = in_out_connections(dummy_connections[m])
                                if (len(np.trim_zeros(in_out_path[0, 0])) != typeofproc[0][0] or len(np.trim_zeros(in_out_path[0, 1]))!= typeofproc[0][1]):
                                    continue
                            simp_points, simp_connections = simplify_diagram(dummy_points, trim_zeros_3D(dummy_connections[m], axis=1))
                            for o in range(len(simp_points)):
                                new_points[n, o] = simp_points[o]
                            for o in range(n_types):
                                for p in range(len(simp_connections[0])):
                                    new_connections[n, o, p] = simp_connections[o, p]
                            new_count[n] = can_count[i][k] * count[j][l]        
                            n += 1
                for k in range(len(can_connections[i])):
                    for l in range(len(connections[j])):
                        dummy_points, dummy_connections = make_connection(trim_zeros_2D(points[j][l]), trim_zeros_3D(connections[j][l], axis=1), trim_zeros_2D(can_points[i][k]), trim_zeros_3D(can_connections[i][k], axis = 1), offset=offset)
                        for m in range(len(dummy_connections)):
                            if(curr_order+1  == max_order): 
                                in_out_path = in_out_connections(dummy_connections[m])
                                if (len(np.trim_zeros(in_out_path[0, 0])) != typeofproc[0][0] or len(np.trim_zeros(in_out_path[0, 1]))!= typeofproc[0][1]):
                                    continue
                            simp_points, simp_connections = simplify_diagram(dummy_points, trim_zeros_3D(dummy_connections[m], axis=1))
                            for o in range(len(simp_points)):
                                new_points[n, o] = simp_points[o]
                            for o in range(n_types):
                                for p in range(len(simp_connections[0])):
                                    new_connections[n, o, p] = simp_connections[o, p]
                            new_count[n] = can_count[i][k] * count[j][l] 
                            n += 1

    """for i in range(len(counter_points)):
        for j in range(i, len(connections)):
            if (i+2+ j +1) == curr_order:
                for k in range(len(counter_points[i])):
                    for l in range(len(connections[j])):
                        dummy_points, dummy_connections = make_connection(trim_zeros_2D(np.array(counter_points[i][k])), trim_zeros_3D(np.array([counter_connections[i][k],np.zeros_like(counter_connections[i][k])]), axis=1), trim_zeros_2D(points[j][l]), trim_zeros_3D(connections[j][l], axis = 1), offset=offset)
                        for m in range(len(dummy_connections)):
                            if(curr_order+1  == max_order): 
                                in_out_path = in_out_connections(dummy_connections[m])
                                if (len(np.trim_zeros(in_out_path[0, 0])) != typeofproc[0][0] or len(np.trim_zeros(in_out_path[0, 1]))!= typeofproc[0][1]):
                                    continue
                            simp_points, simp_connections = simplify_diagram(dummy_points, trim_zeros_3D(dummy_connections[m], axis=1))
                            for o in range(len(simp_points)):
                                new_points[n, o] = simp_points[o]
                            for o in range(n_types):
                                for p in range(len(simp_connections[0])):
                                    new_connections[n, o, p] = simp_connections[o, p]
                            new_count[n] = can_count[i][k] * count[j][l]        
                            n += 1
                for k in range(len(counter_points[i])):
                    for l in range(len(connections[j])):
                        dummy_points, dummy_connections = make_connection(trim_zeros_2D(points[j][l]), trim_zeros_3D(connections[j][l], axis=1), trim_zeros_2D(np.array(counter_points[i][k])), trim_zeros_3D(np.array([counter_connections[i][k],np.zeros_like(counter_connections[i][k])]), axis=1), offset=offset)
                        for m in range(len(dummy_connections)):
                            if(curr_order+1  == max_order): 
                                in_out_path = in_out_connections(dummy_connections[m])
                                if (len(np.trim_zeros(in_out_path[0, 0])) != typeofproc[0][0] or len(np.trim_zeros(in_out_path[0, 1]))!= typeofproc[0][1]):
                                    continue
                            simp_points, simp_connections = simplify_diagram(dummy_points, trim_zeros_3D(dummy_connections[m], axis=1))
                            for o in range(len(simp_points)):
                                new_points[n, o] = simp_points[o]
                            for o in range(n_types):
                                for p in range(len(simp_connections[0])):
                                    new_connections[n, o, p] = simp_connections[o, p]
                            new_count[n] = can_count[i][k] * count[j][l] 
                            n += 1 

                """
    #In the case of the gluon diagrams, there is only it second order diagrams, so this will only be used for curr_order = 1, but it should be general, for the cases where 
    #there are higher order canonical diagrams.
    if curr_order < len(can_connections):
        for i in range(len(can_points[curr_order])):
            for j in range(len(can_points[curr_order][i])):
                new_points[n, j] = can_points[curr_order][i][j]
            for j in range(n_types):
                for k in range(len(can_connections[curr_order][i][j])):
                    new_connections[n, j, k] = can_connections[curr_order][i][j][k]
            new_count[n] = can_count[curr_order][i][0]
            n += 1
    
    """if curr_order < len(counter_points):
        for i in range(len(counter_points[curr_order-1])):
            for j in range(len(counter_points[curr_order-1][i])):
                new_points[n, j] = counter_points[curr_order-1][i][j]
            for j in range(n_types):
                for k in range(len(counter_connections[curr_order-1][i])):
                    if j == 0:
                        new_connections[n, j, k] = counter_connections[curr_order-1][i][k]
                    else:
                        new_connections[n, j, k] = np.zeros(2, dtype=int)
            new_count[n] = 0
            n += 1
    """
    return new_points, new_connections, new_count