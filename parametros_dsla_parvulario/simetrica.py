import pandas as pd

x = pd.read_csv('conexion_pasillos.csv', header=None).to_numpy()

for i in range(len(x)):

    for j in range(len(x)):

        if x[i][j] == 1 and x[j][i] == 0:

            print(j, i)


