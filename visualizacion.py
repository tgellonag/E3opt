import pandas as pd
import matplotlib.pyplot as plt


def mostrar_solucion(c, pasillos_utilizados, t_salida):

    coordenadas_pasillos = pd.read_csv('parametros_dsla_parvulario/coordenadas_pasillos.csv', header=None)
    # columna 1 es la coordenada x del vertice pasillo y columna 2 es la coordenada y del vertice del pasillo la columna3 la coordenada x del vertice siguiente y la columna 4 la coordenada y del vertice siguiente

    #diccionario con los pasillos y sus vertices

    pasillos = {}
    for i in range(len(coordenadas_pasillos)):
        pasillos[i] = [(coordenadas_pasillos[0][i], coordenadas_pasillos[1][i]), (coordenadas_pasillos[2][i], coordenadas_pasillos[3][i])]


    # Grafico con los pasillos, vertices azules, pasillos negros


    for i in range(len(pasillos)):

        plt.plot([pasillos[i][0][0], pasillos[i][1][0]], [pasillos[i][0][1], pasillos[i][1][1]], 'k-')

    # Grafico con los pasillos utilizados en la solucion

    
    for i in pasillos_utilizados:

        plt.plot([pasillos[i][0][0], pasillos[i][1][0]], [pasillos[i][0][1], pasillos[i][1][1]], 'r-')

    origen = pasillos_utilizados[0]

    plt.plot([pasillos[origen][0][0]], [pasillos[origen][0][1]], 'go')

    # Graficar una region con puntos (0,0), (0,20), (-5,20) y (-5,0)

    plt.fill([0, 0, -5, -5], [0, 20, 20, 0], 'gray')

    # Graficar una region con puntos (4, 0), (14, 0), (14, -5) y (4, -5)

    plt.fill([4, 14, 14, 4], [0, 0, -5, -5], 'gray')

    # Graficar una region con puntos (34, 14), (30, 19), (30, 24), (45, 24), (45, 14)

    plt.fill([34, 30, 30, 38, 38], [14, 19, 24, 24, 14], 'gray')

    # Poner el tiempo de salida del curso abajo a la derecha

    plt.text(50, -5, f'Tiempo de salida: {t_salida}', ha='right', va='bottom')

    # for i in range(len(pasillos)):
    #     plt.text((pasillos[i][0][0] + pasillos[i][1][0]) / 2, (pasillos[i][0][1] + pasillos[i][1][1]) / 2, str(i + 1), ha='center', va='center', color='orange')

    plt.savefig(f'fotos/curso{c}')

    plt.show()

    # reiniciar el grafico para siguiente curso

    plt.clf()
    plt.cla()
    plt.close()
    

    

    










