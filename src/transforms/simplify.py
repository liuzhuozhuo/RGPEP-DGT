import numpy as np

from src.transforms.format import trim_zeros_3D

def decrement_number_in_array(array, number):
    array[array == number] -= 1
    return array

def simplify_diagram_it (points, connections):
    """
    Function that will be iterated to simplify the diagram by removing the points and connections that are not needed.
    """
    pos = np.zeros((2, 3), dtype=int)
    for i in range(1, np.max(connections)+1):
        count = 0
        for j in range(len(connections)):
            for k in range(len(connections[j])):
                for l in range(2):
                    if connections[j, k, l] == i:
                        count += 1
                        if count == 1:
                            pos[0] = np.array([j, k, l])
                        elif count == 2:
                            pos[1] = np.array([j, k, l])
                        else:
                            break
        if count == 2 and pos[0, 0] == pos[1, 0]:
            j = pos[0, 0] # type of particle
            points = np.delete(points, i-1, axis=0)
            if pos[0, 2] == 0:
                if pos[1, 2] == 0:
                    prov = np.array([connections[j, pos[0, 1], 1], connections[j, pos[1, 1], 1]])
                elif pos[1, 2] == 1:
                    prov = np.array([connections[j, pos[0, 1], 1], connections[j, pos[1, 1], 0]])  
            elif pos[0, 2] == 1:
                if pos[1, 2] == 0:
                    prov = np.array([connections[j, pos[0, 1], 0], connections[j, pos[1, 1], 1]])                  
                elif pos[1, 1] == 1:
                    prov = np.array([connections[j, pos[0, 1], 0], connections[j, pos[1, 1], 0]])
            connections[j, pos[1, 1]] = np.array([0, 0])
            connections[j, pos[0, 1]] = prov
                    
            for k in range(i, np.max(connections)+1):
                connections = decrement_number_in_array(connections, k)

    return points, trim_zeros_3D(connections, axis=1)

def simplify_diagram (points, connections):
    """
    Simplify the diagram by removing the points and connections that are not needed, by iterating the function simplify_diagram_it, until the 
    number of points and connections does not change anymore.
    """
    new_points, new_connections = simplify_diagram_it(points, connections)
    new_new_points, new_new_connections = simplify_diagram_it(new_points, new_connections)
    while len(new_points) != len(new_new_points) or len(new_connections) != len(new_new_connections):
        new_points, new_connections = new_new_points, new_new_connections
        new_new_points, new_new_connections = simplify_diagram_it(new_points, new_connections)
    return new_new_points, new_new_connections