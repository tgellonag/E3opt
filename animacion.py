import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import json

def mostrar_animacion(c, pasillos_utilizados, t_salida):

    print(pasillos_utilizados)

    coordenadas_pasillos = pd.read_csv('parametros_dsla_parvulario/coordenadas_pasillos.csv', header=None)

    intervalos = []
    for t in pasillos_utilizados:
        intervalos.append(t)
    
    print(intervalos)

    pasillos = {}
    for i in range(len(coordenadas_pasillos)):
        pasillos[i] = [(coordenadas_pasillos[0][i], coordenadas_pasillos[1][i]), (coordenadas_pasillos[2][i], coordenadas_pasillos[3][i])]

    def update(t):

        if t == 0:

            origen = pasillos_utilizados[intervalos[0]]
            plt.plot([pasillos[origen][0][0]], [pasillos[origen][0][1]], 'go')

            for i in range(len(pasillos)):

                plt.plot([pasillos[origen][0][0]], [pasillos[origen][0][1]], 'go')
                plt.plot([pasillos[i][0][0], pasillos[i][1][0]], [pasillos[i][0][1], pasillos[i][1][1]], 'k-')

            plt.fill([0, 0, -5, -5], [0, 20, 20, 0], 'gray')
            plt.fill([4, 14, 14, 4], [0, 0, -5, -5], 'gray')
            plt.fill([34, 30, 30, 38, 38], [14, 19, 24, 24, 14], 'gray')


        if t in intervalos:
        
            index = pasillos_utilizados[t]
            plt.plot([pasillos[index][0][0], pasillos[index][1][0]], [pasillos[index][0][1], pasillos[index][1][1]], 'r-')
        
            origen = pasillos_utilizados[intervalos[0]]
            plt.plot([pasillos[origen][0][0]], [pasillos[origen][0][1]], 'go')



    fig = plt.figure(figsize=(10, 8))
    ani = FuncAnimation(fig, update, frames=range(15), interval=1000)
    
    #Guardar la animacion en gif
    ani.save(f'animaciones/curso{c}.gif', writer='pillow', fps=1)

if __name__ == '__main__':


    # import las soluciones desde json con json

    c = 13
    soluciones = {}

    for i in range(c):

        with open(f'soluciones/curso{i}.json') as f:
            print(f'Abriendo solucion {i}')
            solucion = json.load(f)

        pasillos_utilizados = {}

        for i in solucion:

            pasillos_utilizados[int(i)] = int(solucion[i])

        soluciones[i] = pasillos_utilizados

    print(soluciones)

    for i in soluciones:

        mostrar_animacion(i, soluciones[i], list(soluciones[i].keys())[0])

        

        



