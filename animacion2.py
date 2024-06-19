import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import json

def mostrar_animacion_cursos(cursos):

    coordenadas_pasillos = pd.read_csv('parametros_dsla_parvulario/coordenadas_pasillos.csv', header=None)

    colors_markers = [
    'b^',   # blue
    'g^',   # green
    'r^',   # red
    'c^',   # cyan
    'm^',   # magenta
    'bo',  # blue circles
    'go',  # green circles
    'ro',  # red circles
    'co',  # cyan circles
    'mo',  # magenta circles
    'bd',  # blue plus signs
    'gd',  # green plus signs
    'rd',  # red plus signs
]
    intervalos = {}

    for c in cursos:

        intervalos[c] = []

        for t in cursos[c]:

            intervalos[c].append(t)
    
    print(intervalos)

    pasillos = {}
    for i in range(len(coordenadas_pasillos)):
        pasillos[i] = [(coordenadas_pasillos[0][i], coordenadas_pasillos[1][i]), (coordenadas_pasillos[2][i], coordenadas_pasillos[3][i])]

    def update(t):

        plt.clf()

        for i in range(len(pasillos)):

            plt.plot([pasillos[i][0][0], pasillos[i][1][0]], [pasillos[i][0][1], pasillos[i][1][1]], 'k-')

        plt.fill([0, 0, -5, -5], [0, 20, 20, 0], 'gray')
        plt.fill([4, 14, 14, 4], [0, 0, -5, -5], 'gray')
        plt.fill([34, 30, 30, 38, 38], [14, 19, 24, 24, 14], 'gray')

        for c in cursos:

            if t in intervalos[c]:
            
                index = cursos[c][t]
                plt.plot([(pasillos[index][0][0] + pasillos[index][1][0]) / 2] , [(pasillos[index][0][1] + pasillos[index][1][1]) / 2], colors_markers[c], markersize=10)
            
            
    fig = plt.figure(figsize=(10, 8))
    ani = FuncAnimation(fig, update, frames=range(15), interval=1000)
    
    #Guardar la animacion en gif
    plt.show()

if __name__ == '__main__':


    # import las soluciones desde json con json



    with open(f'soluciones.json') as f:
        print(f'Abriendo solucion')
        solucion = json.load(f)

    st = {}

    for c in solucion:

        stt = {}

        for t in solucion[c]:
            
            stt[int(t)] = int(solucion[c][t])
            

        st[int(c)]= stt

    mostrar_animacion_cursos(st)

        

        



