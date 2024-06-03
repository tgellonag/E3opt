from gurobipy import Model, GRB, quicksum
import pandas as pd
import time
import tkinter as tk
from tkinter import scrolledtext

# definimos el modelo, despues se ejecuta desde la linea 280
def optimizar(carpeta_parametros, multiplicador, tiempo_max = None, final = False):
    # PARAMETROS
    print(f"Modelo con velocidad x{multiplicador} para encontrar cota de tiempo")
    # Z_iy: pasillos a zonas seguras (1 = el pasillo i llega a la zona segura y | 0 = e.o.c.)
    z = pd.read_csv(f'{carpeta_parametros}/pasillo_llega_zona_segura.csv', header=None).to_numpy()
    # c_ij: connexiones de pasillos (1 = los pasillos i y j estan conectados | 0 = e.o.c.)
    x = pd.read_csv(f'{carpeta_parametros}/conexion_pasillos.csv', header=None).to_numpy()
    # d_i: distancia del pasillo i
    d = pd.read_csv(f'{carpeta_parametros}/distancia_pasillos.csv', header=None).iloc[:,0]
    # v_ci: velocidad máxima del curso c por el pasillo i
    v = pd.read_csv(f'{carpeta_parametros}/velocidad_cursos.csv', header=None).to_numpy()
    # o_ic: pasillo de origen de los cursos (1 = el pasillo i es el pasillo de origen del curso c | 0 = e.o.c.)
    o = pd.read_csv(f'{carpeta_parametros}/pasillo_origen.csv', header=None).to_numpy()
    # k_i: capacidad máxima del pasillo i
    k = pd.read_csv(f"{carpeta_parametros}/capacidad_pasillos.csv", header=None).iloc[:,0]
    # n_c: cantidad de personas en el curso c
    n = pd.read_csv(f"{carpeta_parametros}/cantidad_curso.csv", header=None).iloc[:,0]
    # q_y: capacidad máxima de la zona segura y
    q = pd.read_csv(f'{carpeta_parametros}/capacidad_zona.csv', header=None).iloc[:,0]
    # m_c: discapacitados del curso (1 = el curso c tiene algún discapacitado | 0 = e.o.c.)
    m = pd.read_csv(f'{carpeta_parametros}/discapacitado_curso.csv', header=None).iloc[:,0]
    # a_i: pasillo apto para discapacitados (1 = el pasillo i es apto para discapacitados | 0 = e.o.c.)
    a = pd.read_csv(f"{carpeta_parametros}/discapacitado_pasillo.csv", header=None).iloc[:,0]
    # r_cy: responsables zonas, (1 = dentro del curso c se encuantra un responzable de la zona y | 0 = e.o.c)
    r = pd.read_csv(f'{carpeta_parametros}/responsable_zona_curso.csv', header=None).to_numpy()

    # CONJUNTOS

    C = range(len(n)) # numero de cursos
    I = range(len(k))  # numero de pasillos
    Y = range(len(q)) # numero de zonas de seguridad 
    if tiempo_max is None:
        tiempo_max = 1
        for c in C:
            for i in I:
                tiempo_max += d[i]/(v[c, i] * multiplicador)
    print(f"Tiempo máximo: {tiempo_max}") 
    T = range(int(tiempo_max)) # tiempo en segundos
    tiempo_max = len(T)


    # MODELO

    modelo = Model("Operación Deyse")
    modelo.setParam("TimeLimit", 900)

    if not final:
        modelo.setParam("MIPGap", 0.15)


    # VARIABLES

    inicio_total = time.time()

    #Anadiendo variable s
    s = {}
    for c in C:
        s[c]= modelo.addVar(vtype=GRB.CONTINUOUS, name=f's{c}', lb=0)
    p = {}
    u = {}
    #Anadiendo variable p y u
    for i in I:
        for c in C:
            for t in T:
                p[i, c, t] = modelo.addVar(vtype=GRB.BINARY, name=f'p[{i},{c},{t}]')
                u[i, c, t] = modelo.addVar(vtype=GRB.BINARY, name=f'u[{i},{c},{t}]')
    #Anadiendo Variable Landa
    landa = modelo.addVar(vtype=GRB.CONTINUOUS, name='landa', lb=0)
    modelo.update()

    ou = {}
    for c in C:
        suma = 0  # Reset suma for each new c
        for t in T:

            for i in I:

                suma += o[i, c] * u[i, c, t]

            ou[c, t] = suma.copy()


    # RESTRICCIONES
    # 1. λ corresponde al momento en el que el último curso llega a una zona segura.
    for c in C:
        modelo.addConstr((landa >= s[c] + quicksum(quicksum(p[i,c,t] for i in I) for t in T) ),name = "R1")

    print("Restricción 1 lista")

    # 2. Las personas en un pasillo no exceden el máximo.
    for i in I:
        for t in T:
            modelo.addConstr((quicksum(p[i,c,t]* n[c] for c in C)  <= k[i]), name = "R2")

    print("Restricción 2 lista")

    # 3. El tiempo en un pasillo es mayor o igual a la distancia del pasillo entre la 
    # velocidad máxima del curso.
    for c in C:
        for i in I:
            for t in T:
                modelo.addConstr((quicksum(p[i,c, sigma] for sigma in range(t, min(1 + t + int(d[i]/v[c,i]), tiempo_max))\
                    )>= (d[i]/(v[c,i] * multiplicador)) * u[i,c,t]),name = "R3")

    print("Restricción 3 lista")

    # 4. Un curso que pasa por un pasillo debe tener uno de origen. A menos que este sea el primero.
    for c in C:
        for i in I:
            for t in range(1, tiempo_max):
                modelo.addConstr(( u[i,c,t] <= o[i,c] + quicksum(x[i,j]*p[j,c,t-1] for j in I if j != i) ), name = "R4")

    print("Restricción 4 lista")

    # 5. Todos los cursos llegan a una zona de seguridad.
    for c in C:
        modelo.addConstr((1 == quicksum(quicksum(quicksum((u[i,c,t]*z[i,y]) for y in Y) for i in I) for t in T)), name = "R5")

    print("Restricción 5 lista")

    # 6. Todos los cursos pasan por su pasillo de origen.
    for c in C:
        for i in I:
            modelo.addConstr((o[i,c] - quicksum(u[i,c,t] for t in T) <= 0), name = "R6")

    print("Restricción 6 lista")

    # 7. Las zonas de seguridad no rebalsan.
    for y in Y:
        modelo.addConstr((quicksum(quicksum(quicksum(u[i,c,t]*z[i,y]*n[c] for i in I) for c in C)for t in T)<=q[y]), name = "R7")

    print("Restricciones 1-7 listas")

    # 8. Si un curso ya salió de su sala, debe estar en algún pasillo o en una zona segura, y el pasillo de origen es el primero que se recorre.
    for c in C:

        print(f"Restriccion 8: {c}")
        suma1 = 0
        suma2 = 0

        for t in T:

            suma1 += quicksum(z[i, y] * u[i, c, t] for y in Y for i in I)
            suma2 = ou[c, t] 


            modelo.addConstr(
                suma2 <= quicksum((1 - z[i, y]) * p[i, c, t] for y in Y for i in I) + suma1,
                name=f"R8_{c}_{t}.a"
            )
            for i in I:
                modelo.addConstr(
                    quicksum(u[i,c,sigma] for sigma in range(1,t+1)) <= suma2,
                    name=f"R8_{c}_{t}.b"
                )

    print("Restricciones 8 listas")


    # 9. Cada curso está en máximo un pasillo a la vez.
    for c in C:
        for t in T:
            modelo.addConstr((quicksum(p[i,c,t] for i in I) <= 1), name = "R9")
    print("Restricciones 9 listas")
    # 10. Cursos con discapacitados solo pueden pasar por pasillos aptos
    for c in C:
        for i in I:
            modelo.addConstr(quicksum(u[i,c,t] * m[c] for t in T) <= a[i], name = "R10")
    print("Restricciones 10 listas")

    # 11. Los responsables de zona van sí o sí a su zona.
    for y in Y:
        modelo.addConstr(quicksum(quicksum(quicksum(r[c, y] * u[i,c,t] * z[i,y] for c in C) for i in I) for t in T) >= quicksum(r[c, y] for c in C), name = "R11")
    print("Restricciones 11 listas")
    # 12. Un curso pasa por un pasillo máximo una vez.
    for c in C:
        for i in I:
            modelo.addConstr(quicksum(u[i,c,t] for t in T) <= 1, name = "R12")
    print("Restricciones 12 listas")

    # 13. Un curso puede estar en un pasillo si lo empieza a recorrer o si ya estaba en 
    # ese pasillo.
    for i in I:
        for c in C:
            for t in range(1, tiempo_max):
                modelo.addConstr(p[i,c,t] <= u[i, c, t] + p[i,c,t-1],name = "R13")
    print("Restricciones 13 listas")
    # 14. sc corresponde al tiempo que el curso c espera en su sala antes de comenzar a 
    # recorrer su pasillo de origen.
    for c in C:
        modelo.addConstr(quicksum(1 - ou[c, t] for t in T) == s[c], name = "R14")

    print("Restricciones 14 listas")

    # 15. Los cursos no pueden empezar ocupando un pasillo.
    for i in I:
        for c in C:
            modelo.addConstr(p[i, c, 0] == 0, name = "R15a")
            modelo.addConstr(u[i, c, 0] == 0, name = "R15b")
    print("Restricciones 15 listas")
    # 16. λ se encuentra dentro de T.
    modelo.addConstr(landa <= quicksum(d[i]/(v[c, i] * multiplicador) for c in C for i in I) + 1, name = "R16") 
    print("Restricciones 16 listas")
    modelo.update()
    print("Restricciones listas")
    # FUNCION OBJETIVO
    modelo.setObjective(landa, GRB.MINIMIZE)

    # OPTIMIZAR MODELO
    modelo.optimize()

    fin_total = time.time()
    print(f"Tiempo total de ejecución cota superior de tiempo: {fin_total - inicio_total}")

    if final:
        if modelo.status == GRB.OPTIMAL:
            print(f"Tiempo mínimo de evacuación: {landa.X}")
            for c in C:
                print(f"Tiempo de salida del curso {c}: {s[c].X}")
            df_resultados = pd.DataFrame(columns=[f"P{i}" for i in I])
            df_resultados.to_excel("resultados.xlsx", index=False)
            for t in T:
                for i in I:
                    for c in C:
                        if p[i,c,t].X > 0.5:
                            try:
                                df_resultados.loc[t, f"P{i}"] += f", {c}"
                            except:
                                df_resultados.loc[t, f"P{i}"] = f"C: {c}"

            df_resultados = df_resultados.fillna(' ')
            print(df_resultados)

            # Creamos una ventana que muestre la tabla
            def mostrar_tabla(df):
                ventana = tk.Tk()
                ventana.title("Tabla Decision")
                tabla_texto = df.to_string(index=False)

                # Crear un widget Text para mostrar la tabla
                texto_tabla = scrolledtext.ScrolledText(ventana, wrap=tk.NONE)
                texto_tabla.insert(tk.END, tabla_texto)
                texto_tabla.grid(row=0, column=0, sticky='nsew')

                # Configurar la ventana para que el texto se ajuste al tamaño de la ventana
                ventana.grid_rowconfigure(0, weight=1)
                ventana.grid_columnconfigure(0, weight=1)

                # Configurar las barras de desplazamiento horizontal y vertical
                scroll_x = tk.Scrollbar(ventana, orient=tk.HORIZONTAL, command=texto_tabla.xview)
                scroll_x.grid(row=1, column=0, sticky='ew')
                texto_tabla['xscrollcommand'] = scroll_x.set

                scroll_y = tk.Scrollbar(ventana, orient=tk.VERTICAL, command=texto_tabla.yview)
                scroll_y.grid(row=0, column=1, sticky='ns')
                texto_tabla['yscrollcommand'] = scroll_y.set

                # Ejecutar el bucle de eventos de Tkinter
                ventana.mainloop()

            # Llamar a la función para mostrar la tabla
            mostrar_tabla(df_resultados)
        else:
            print("No se encontró una solución óptima.")
        print("finish")
    else:
        if modelo.status == GRB.INFEASIBLE:
            return("infeasible")
        # RESULTADOS (revisenlo ns si esta bien)
        if modelo.status == GRB.OPTIMAL:
            return int(landa.X) * multiplicador




# EJECUCION



carpetas_parametros = ["parametros_mediano", "parametros_chico", "parametros_enano",'parametros_dsla_parvulario']
for i in range(len(carpetas_parametros)):
    print(f"{i+1}. {carpetas_parametros[i]}")
print("\n El conjunto de parametros utilizado en el informe es el de la carpeta: 'parametros_dsla_parvulario' \n")
opcion = input("Ingrese el número de la carpeta de parámetros que desea utilizar: ")
if opcion == '1':
    carpeta_parametros = carpetas_parametros[0]
elif opcion == '2':
    carpeta_parametros = carpetas_parametros[1]
elif opcion == '3':
    carpeta_parametros = carpetas_parametros[2]
elif opcion == '4':
    carpeta_parametros = carpetas_parametros[3]


# Primero resolvemos el problema multiplicando las velocidades para trabajar con menos intervalos de tiempo.

# Para resolver este problema se utiliza una cota superior para T equivalente a la cantidad de periodos de tiempo
# que le tomaría a cada curso pasar por todos los pasillos uno a la vez, lo cual sirve como cota superior al problema
# ya que se espera que un curso no tenga que pasar por todos los pasillos y que los cursos pueden estar recorriendo 
# pasillos al mismo tiempo.
tiempo_max = optimizar(carpeta_parametros=carpeta_parametros, multiplicador= 10)
tiempo_max2 = optimizar(carpeta_parametros=carpeta_parametros, multiplicador= 5)

# Con este resultado, podemos definir una mejor cota superior para el tiempo máximo que los cursos se demorarían en evacuar
# para así utilizar esta cota para el modelo que se busca optimizar (con periodos de 5s).
optimizar(carpeta_parametros=carpeta_parametros, multiplicador=1, tiempo_max=tiempo_max2, final=True)

# Todo este proceso se realiza con el fin de acortar el tiempo de ejecución del programa, para cumplir con el objetivo de
# resolver el modelo en menos de 30 min desde que se ejecuta main.py y se selecciona la opcion 'parametros_dsla_parvulario'.