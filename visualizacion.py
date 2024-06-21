import pandas as pd
import matplotlib.pyplot as plt
import json
import os


def mostrar_solucion(c, pasillos_utilizados, t_salida, param = '', variacion = '', landa = None):

    
    plt.clf()
    plt.cla()
    plt.close()
    

    coordenadas_pasillos = pd.read_csv('parametros_dsla_parvulario/coordenadas_pasillos.csv', header=None)
    # columna 1 es la coordenada x del vertice pasillo y columna 2 es la coordenada y del vertice del pasillo la columna3 la coordenada x del vertice siguiente y la columna 4 la coordenada y del vertice siguiente
    intervalos = []
    for t in pasillos_utilizados:
        intervalos.append(t)

    #diccionario con los pasillos y sus vertices

    pasillos = {}
    for i in range(len(coordenadas_pasillos)):
        pasillos[i] = [(coordenadas_pasillos[0][i], coordenadas_pasillos[1][i]), (coordenadas_pasillos[2][i], coordenadas_pasillos[3][i])]


    # Grafico con los pasillos, vertices azules, pasillos negros


    for i in range(len(pasillos)):

        plt.plot([pasillos[i][0][0], pasillos[i][1][0]], [pasillos[i][0][1], pasillos[i][1][1]], 'k-')

    # Grafico con los pasillos utilizados en la solucion

    
    for i in pasillos_utilizados:

        k = pasillos_utilizados[i]

        if k >= 0:

            plt.plot([pasillos[k][0][0], pasillos[k][1][0]], [pasillos[k][0][1], pasillos[k][1][1]], 'r-')

    origen = pasillos_utilizados[intervalos[0]]

    plt.plot([pasillos[origen][0][0]], [pasillos[origen][0][1]], 'go')

    # Graficar una region con puntos (0,0), (0,20), (-5,20) y (-5,0)

    plt.fill([0, 0, -5, -5], [0, 20, 20, 0], 'gray')

    # Graficar una region con puntos (4, 0), (14, 0), (14, -5) y (4, -5)

    plt.fill([4, 14, 14, 4], [0, 0, -5, -5], 'gray')

    # Graficar una region con puntos (34, 14), (30, 19), (30, 24), (45, 24), (45, 14)

    plt.fill([34, 30, 30, 38, 38], [14, 19, 24, 24, 14], 'gray')

    # Poner el tiempo de salida del curso abajo a la derecha

    plt.text(50, -5, f'Tiempo de salida: {t_salida}', ha='right', va='bottom')
    plt.text(50, -5, f'Curso: {c}', ha='right', va='top')
    plt.text(50, -2, f'Tiempo de evacuacion: {landa}', ha='right', va='bottom')

    # for i in range(len(pasillos)):
    #     plt.text((pasillos[i][0][0] + pasillos[i][1][0]) / 2, (pasillos[i][0][1] + pasillos[i][1][1]) / 2, str(i + 1), ha='center', va='center', color='orange')

    os.makedirs(f'fotos_{param}_{variacion}', exist_ok=True)

    plt.savefig(f'fotos_{param}_{variacion}/curso{c}')



    # reiniciar el grafico para siguiente curso

    plt.clf()
    plt.cla()
    plt.close()
    

    
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

        print(soluciones[i])
        print(list(soluciones[i].keys())[0])

        mostrar_solucion(i, soluciones[i], list(soluciones[i].keys())[0])

        
    










