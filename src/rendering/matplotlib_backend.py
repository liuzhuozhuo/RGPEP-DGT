import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl

from src.transforms.format import prune_points_and_reindex
from src.search.comparison import find_equal_subarrays

def represent_diagram_as_png (points, connection, symmetry_num, colors, linestyles, show_index = True, directory = "", figsize_=(4,2)):

    #Failproof for empty connections
    if (np.all(connection == 0)):
        return 
    
    #Prune points and reindex connections
    points, connection = prune_points_and_reindex(points, connection)

    #points = trim_zeros_2D(points)
    #connection = trim_zeros_3D(connection, axis=1)

    #Initialize figure
    fig=plt.figure(figsize=figsize_) 
    ax=fig.add_subplot(111)
    ax.axis('off')

    j = 0 #Auxiliary linestyle index for gauge bosons

    for conn in connection:
        loops = find_equal_subarrays(conn)
        # Following the point made previously len(conn) indicate the number of connections instead of number of types of particles.
        for i in range(len(conn)):
            # In the case that the type of particle is a photon a spetial type of line is used to represent it.
            if (linestyles[j] == "photon"):
                with mpl.rc_context({'path.sketch': (3, 15, 1)}):
                    if np.isin(i, loops):
                        middle_point = (points[conn[i, 0]-1] + points[conn[i, 1]-1]) / 2
                        circle = plt.Circle((middle_point[0], middle_point[1]), np.linalg.norm(points[conn[i, 0]-1]-middle_point), color=colors[j], fill=False)
                        ax.add_patch(circle)
                    elif conn[i, 0] == conn[i, 1] and conn[i ,0] != 0:
                        ax.scatter(points[conn[i, 0]-1, 0], points[conn[i, 0]-1, 1], color = colors[j])
                    else:
                        ax.plot([points[conn[i, 0]-1, 0], points[conn[i, 1]-1, 0]], [points[conn[i, 0]-1, 1], points[conn[i, 1]-1, 1]], color=colors[j])
            else:
                if np.isin(i, loops):
                    middle_point = (points[conn[i, 0]-1] + points[conn[i, 1]-1]) / 2
                    circle = plt.Circle((middle_point[0], middle_point[1]), np.linalg.norm(points[conn[i, 0]-1]-middle_point), color=colors[j], fill=False, linestyle=linestyles[j])
                    ax.add_patch(circle)
                elif conn[i, 0] == conn[i, 1] and conn[i ,0] != 0:
                    ax.scatter(points[conn[i, 0]-1, 0], points[conn[i, 0]-1, 1], color = colors[j], s = 50, zorder = 10)
                else:
                    ax.plot([points[conn[i, 0]-1, 0], points[conn[i, 1]-1, 0]], [points[conn[i, 0]-1, 1], points[conn[i, 1]-1, 1]], color=colors[j], linestyle=linestyles[j])
        j+=1
    ax.axis('equal')
    if show_index:
        for i in range(len(points)):
            ax.text(points[i, 0], points[i, 1], str(i+1), fontsize=12, color="black", ha="right", va="top")
    if symmetry_num !=0:
        ax.text(-1, 0.5, f"N = {symmetry_num}", fontsize=12, color="black", ha="left", va="top")
    if directory != "":
        plt.savefig(directory, bbox_inches='tight')
        plt.close() #Added to not show in the notebook 


