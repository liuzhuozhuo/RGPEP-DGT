import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl
import feynman as fyn

from src.transforms.format import *
from src.search.comparison import find_equal_subarrays, find_equal_subarrays_3D
from src.transforms.concatenation import in_out_connections, rearrange_in_out_points, equalize_x_spacing, find_loops

def represent_diagram_as_png (points, connection, symmetry_num, colors, linestyles, show_index = True, directory = "", figsize_=(4,2)):

    #Failproof for empty connections
    if (np.all(connection == 0)):
        return 
    
    #Prune points and reindex connections
    points, connection = prune_points_and_reindex(points, connection)

    points = trim_zeros_2D(points)
    connection = trim_zeros_3D(connection, axis=1)

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
                if np.isin(i, np.concatenate(loops)):
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

def represent_diagram_as_png_feynman (points, connection, symmetry_num, colors, flavour_,linestyle_ = ["solid", "dotted", "solid", "solid"], directory = "", figsize_=(4,3), arrow_ = [False, False, True, True]):

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
    diagram = fyn.Diagram(ax)

    j = 0 #Auxiliary linestyle index for gauge bosons
    loops = find_equal_subarrays_3D(connection)

    def is_loop(position, loops):
        position = tuple(position)
        for key, positions in loops.items():
            if position in positions:
                return True, positions.index(position)
        return False, None

    for conn in connection:
        for i in range(len(conn)):
            distance = np.linalg.norm(points[conn[i, 0]-1] - points[conn[i, 1]-1])
            tf_loop, loop_index = is_loop([j, i], loops)
            if tf_loop:
                if flavour_[j] == "simple" and colors[j] in ["blue", "red"]:
                    if colors[j] == "blue":
                        direc = -1
                    else:
                        direc = 1
                    diagram.line(diagram.vertex(xy=(points[conn[i, 0]-1, 0], points[conn[i, 0]-1, 1]), markersize=4), 
                                diagram.vertex(xy=(points[conn[i, 1]-1, 0], points[conn[i, 1]-1, 1]), markersize=4)
                                , flavour=flavour_[j], shape = "elliptic", ellipse_position=2*loop_index-1, 
                                nloops = distance*5, xamp=0.1, yamp=0.12, ellipse_spread = 0.35, phase = 7,color = colors[j], linestyle = linestyle_[j], linewidth = 0.5,
                                arrow = arrow_[j], arrow_param={"direction": direc, 'width':0.3, 'length': 0.3  }).scale(1)
                else:
                    diagram.line(diagram.vertex(xy=(points[conn[i, 0]-1, 0], points[conn[i, 0]-1, 1]), markersize=4), 
                                diagram.vertex(xy=(points[conn[i, 1]-1, 0], points[conn[i, 1]-1, 1]), markersize=4)
                                , flavour=flavour_[j], shape = "elliptic", ellipse_position=2*loop_index-1, 
                                nloops = distance*5, xamp=0.1, yamp=0.12, ellipse_spread = 0.35, phase = 7,color = colors[j], linestyle = linestyle_[j], linewidth = 0.5).scale(1)
            elif conn[i, 0] == conn[i, 1] and conn[i ,0] != 0:
                ax.scatter(points[conn[i, 0]-1, 0], points[conn[i, 0]-1, 1], color = colors[j], s = 50, zorder = 10, marker="*")
            else:
                if flavour_[j] == "simple" and colors[j] in ["blue", "red"]:
                    if colors[j] == "blue":
                        direc = -1
                    else:
                        direc = 1
                    diagram.line(diagram.vertex(xy=(points[conn[i, 0]-1, 0], points[conn[i, 0]-1, 1]), markersize=4), 
                             diagram.vertex(xy=(points[conn[i, 1]-1, 0], points[conn[i, 1]-1, 1]), markersize=4)
                             , flavour=flavour_[j], color =colors[j], linestyle = linestyle_[j], linewidth = 0.7, arrow = arrow_[j], arrow_param={"direction": direc, 'width':0.3, 'length': 0.3  }).scale(1)
                else:
                    diagram.line(diagram.vertex(xy=(points[conn[i, 0]-1, 0], points[conn[i, 0]-1, 1]), markersize=4), 
                             diagram.vertex(xy=(points[conn[i, 1]-1, 0], points[conn[i, 1]-1, 1]), markersize=4)
                             , flavour=flavour_[j], color =colors[j], linestyle = linestyle_[j], nloops = distance*4, xamp=0.1, yamp=0.12, linewidth = 0.7).scale(1)
        j+=1
    if symmetry_num !=0:
        ax.text(-1, 0.5, f"N = {symmetry_num}", fontsize=12, color="black", ha="left", va="top")
    
    ax.set_aspect("auto")
    plt.xlim(-1, np.max(points[:, 0]) + 1)
    plt.ylim(np.min(points[:, 1]) - 2, np.max(points[:, 1]) + 2)
    diagram.draw()
    plt.show()

def represent_order_diagram(points, connection, symmetry_num, process, colors_=['black', 'black', 'blue', 'red'], flavour=['loopy','simple', 'simple', 'simple'], linestyle = ["solid", "dotted", "solid", "solid"], directory_ = "", figsize=(4,3), arrow = [False, False, True, True]):
    for i in range(len(points)):
        in_out_connections_ = in_out_connections(connection[i])
        inp_g = len(np.trim_zeros(in_out_connections_[0, 0]))
        out_g = len(np.trim_zeros(in_out_connections_[0, 1]))
        inp = 0
        out = 0
        for j in range(1, len(connection[i])):
            inp += len(np.trim_zeros(in_out_connections_[j, 0]))
            out += len(np.trim_zeros(in_out_connections_[j, 1]))
        if inp == 0 and out == 0 and inp_g == process[0] and out_g == process[1]:
            rearrange_in_out_points(points[i], connection[i])
            points[i]=equalize_x_spacing(points[i], 2)
            find_loops(points[i], connection[i])
            represent_diagram_as_png_feynman(points[i], connection[i], i, colors=colors_, flavour_=flavour, linestyle_=linestyle, arrow_=arrow, directory=directory_, figsize_=figsize)
