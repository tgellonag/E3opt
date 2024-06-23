import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import json
from copy import deepcopy

def find_floor(lst, target):
    """Find the largest number in lst that is less than or equal to the target."""
    lst = sorted(lst)
    low, high = 0, len(lst) - 1
    result = None

    while low <= high:
        mid = (low + high) // 2
        if lst[mid] == target:
            return lst[mid]
        elif lst[mid] < target:
            result = lst[mid]
            low = mid + 1
        else:
            high = mid - 1

    return result

def load_pasillos(filepath):
    """Load pasillos coordinates from a CSV file."""
    coordenadas = pd.read_csv(filepath, header=None)
    return {i: [(coordenadas[0][i], coordenadas[1][i]), 
                (coordenadas[2][i], coordenadas[3][i])] for i in range(len(coordenadas))}

def prepare_intervals(cursos):
    """Prepare the intervals for each course."""
    return {c: list(cursos[c].keys()) for c in cursos}

def plot_static_elements(ax, pasillos, cursos):
    """Plot static elements of the plot."""
    ax.clear()

    for i in pasillos:

        ax.plot([pasillos[i][0][0], pasillos[i][1][0]], [pasillos[i][0][1], pasillos[i][1][1]], 'k-')

    ax.fill([0, 0, -5, -5], [0, 20, 20, 0], 'gray') # zs 3
    ax.fill([4, 14, 14, 4], [0, 0, -5, -5], 'gray') # zs 2
    ax.fill([34, 30, 30, 45, 45], [14, 19, 24, 24, 14], 'gray') #zs 1

    # Escribir el origen de todos los cursos
    
    for c in cursos:
            
        ax.plot([pasillos[cursos[c][list(cursos[c].keys())[0]]][0][0]], [pasillos[cursos[c][list(cursos[c].keys())[0]]][0][1]], 'go')

    


def update_plot(t, ax, intervalos, cursos, pasillos, colors_markers, pos_zs = None):

    pos_zs_copy = deepcopy(pos_zs)
    """Update the plot for the given time step."""

    plot_static_elements(ax, pasillos, cursos)

    for c in cursos:

        periodo = t // 10

        if periodo >= intervalos[c][0]:

            periodo = find_floor(intervalos[c], periodo)
            next_time = intervalos[c][intervalos[c].index(periodo) + 1] if intervalos[c].index(periodo) + 1 < len(intervalos[c]) else 15
            dif_t = next_time - periodo
            lan = ((t - periodo * 10) / 10) / (dif_t)

            index = cursos[c][periodo]
            prev_period = intervalos[c][intervalos[c].index(periodo) - 1] if intervalos[c].index(periodo) - 1 >= 0 else None
            index_previo = cursos[c][prev_period] if prev_period is not None else None

            if index >= 0:

                if index_previo is not None:

                    if pasillos[index][0] == pasillos[index_previo][0]:                  

                        x = (1 - lan) * pasillos[index][0][0] + lan * pasillos[index][1][0]
                        y = (1 - lan) * pasillos[index][0][1] + lan * pasillos[index][1][1]
                        
                    elif pasillos[index][0] == pasillos[index_previo][1]:

                        x = lan * pasillos[index][1][0] + (1 - lan) * pasillos[index][0][0]
                        y = lan * pasillos[index][1][1] + (1 - lan) * pasillos[index][0][1]

                    elif pasillos[index][1] == pasillos[index_previo][0]:

                        x = lan * pasillos[index][0][0] + (1 - lan) * pasillos[index][1][0]
                        y = lan * pasillos[index][0][1] + (1 - lan) * pasillos[index][1][1]
                    
                    else:

                        x = (lan) * pasillos[index][0][0] + (1-lan) * pasillos[index][1][0]
                        y = (lan) * pasillos[index][0][1] + (1-lan) * pasillos[index][1][1]

                else:

                    x = (1 - lan) * pasillos[index][0][0] + lan * pasillos[index][1][0]
                    y = (1 - lan) * pasillos[index][0][1] + lan * pasillos[index][1][1]

            else:     

                x, y = pos_zs_copy[index].pop(0)

            ax.plot(x, y, colors_markers[c], markersize=10)


    ax.text(40, -5, f'Tiempo: {periodo}', fontsize=12)

def mostrar_animacion_cursos(cursos):
    """Show animation for the given courses."""
    pasillos = load_pasillos('parametros_dsla_parvulario/coordenadas_pasillos.csv')
    intervalos = prepare_intervals(cursos)
    colors_markers = ['b^', 'g^', 'r^', 'c^', 'm^', 'bo', 'go', 'ro', 'co', 'mo', 'bd', 'gd', 'rd']
    pos_zs = {-1 : [(35, 15), (35, 17), (35, 19), (35, 21), (35, 23), (35, 24), (35, 15), (35, 16), (35, 17), (35, 18), (35, 19), (35, 20), (35, 21), (35, 22), (35, 23), (35, 24)],
              -2: [(-2, 18), (-2, 16), (-2, 14), (-2, 12), (-2, 10), (-2, 8), (-2, 6), (-2, 4), (-2, 2), (-2, 0), (-2, 18), (-2, 16), (-2, 14), (-2, 12), (-2, 10), (-2, 8), (-2, 6), (-2, 4), (-2, 2), (-2, 0)],
              -3: [(6, -1), (12, -1), (6, -3), (12, -3), (12, -3), (6, -5), (8, -5), (10, -5), (12, -5), (6, -1), (8, -1), (10, -1), (12, -1), (6, -3), (8, -3), (10, -3), (12, -3), (6, -5), (8, -5), (10, -5), (12, -5)],}

    pos_zs_copy = {}
    
    for z in pos_zs:
        pos_zs_copy[z] = deepcopy(pos_zs[z])

    fig, ax = plt.subplots(figsize=(10, 8))

    def update(t):
        update_plot(t, ax, intervalos, cursos, pasillos, colors_markers, pos_zs=pos_zs_copy)

    ani = FuncAnimation(fig, update, frames=range(150), interval=100)
    ani.save(f'animacion.gif', writer='pillow', fps=10)
    plt.show()

if __name__ == '__main__':
    with open('soluciones.json') as f:
        solucion = json.load(f)

    cursos = {}
    for c in solucion:
        int_c = int(c)
        cursos[int_c] = {}
        for t in solucion[c]:
            try:
                int_t = int(float(t))
                int_val = int(float(solucion[c][t]))
                cursos[int_c][int_t] = int_val
            except ValueError as e:
                print(f"Error converting values c: {c}, t: {t}, value: {solucion[c][t]}")
                # Handle the error as needed (e.g., skip this value or set a default)

    mostrar_animacion_cursos(cursos)
