from gurobipy import Model, GRB, quicksum
import pandas as pd
import numpy as np

# PARAMETROS
carpetas_parametros = ["parametros_grande", "parametros_chico"]
if input("Ingrese '1' para el modelo grande, '2' para el modelo chico: ") == 1:
    carpeta_parametros = carpetas_parametros[0]
else:
    carpeta_parametros = carpetas_parametros[1]
# Z_iy: pasillos a zonas seguras (1 = el pasillo i llega a la zona segura y | 0 = e.o.c.)
z = pd.read_csv(f'{carpeta_parametros}/pasillo_llega_zona_segura.csv', header=None)
# c_ij: connexiones de pasillos (1 = los pasillos i y j estan conectados | 0 = e.o.c.)
x = pd.read_csv(f'{carpeta_parametros}/conexion_pasillos.csv', header=None)
# d_i: distancia del pasillo i
d = pd.read_csv(f'{carpeta_parametros}/distancia_pasillos.csv', header=None).iloc[:,0]
# v_ci: velocidad máxima del curso c por el pasillo i
v = pd.read_csv(f'{carpeta_parametros}/velocidad_cursos.csv', header=None)
# o_ic: pasillo de origen de los cursos (1 = el pasillo i es el pasillo de origen del curso c | 0 = e.o.c.)
o = pd.read_csv(f'{carpeta_parametros}/pasillo_origen.csv', header=None)
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
r = pd.read_csv(f'{carpeta_parametros}/responsable_zona_curso.csv', header=None)

# CONJUNTOS

C = range(len(n)) # numero de cursos
I = range(len(k))  # numero de pasillos
Y = range(len(q)) # numero de zonas de seguridad 
T = range(int(1 + quicksum(d[i]/v.iloc[c, i] for c in C for i in I))) # tiempo en segundos

# MODELO

modelo = Model("Operación Deyse")
modelo.setParam("TimeLimit", 20) 

# VARIABLES

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

# RESTRICCIONES
# 1. λ corresponde al momento en el que el último curso llega a una zona segura.
for c in C:
    modelo.addConstr((landa >= s[c] + quicksum(quicksum(p[i,c,t] for i in I) for t in T) ),name = "R1")

# 2. Las personas en un pasillo no exceden el máximo.
for i in I:
    for t in T:
        modelo.addConstr((quicksum(p[i,c,t]* n[c] for c in C)  <= k[i]), name = "R2")

# 3. El tiempo en un pasillo es mayor o igual a la distancia del pasillo entre la 
# velocidad máxima del curso.
for c in C:
    for i in I:
        for t in T:
            modelo.addConstr((quicksum(p[i,c, sigma] for sigma in range(t, min(1 + t + int(d[i]/v.iloc[c,i]), len(T)))\
                )>= (d[i]/v.iloc[c,i]) * u[i,c,t]),name = "R3")

# 4. Un curso que pasa por un pasillo debe tener uno de origen. A menos que este sea 
#el primero.
for c in C:
    for i in I:
        for t in range(1, len(T)):
            modelo.addConstr(( u[i,c,t] <= o.iloc[i,c] + quicksum(x.iloc[i,j]*p[j,c,t-1] for j in I if j != i) ), name = "R4")

# 5. Todos los cursos llegan a una zona de seguridad.
for c in C:
    modelo.addConstr((1 == quicksum(quicksum(quicksum((u[i,c,t]*z.iloc[i,y]) for y in Y) for i in I) for t in T)), name = "R5")

# 6. Todos los cursos pasan por su pasillo de origen.
for c in C:
    for i in I:
        modelo.addConstr(o.iloc[c,i] <= quicksum(u[i,c,t] for t in T), name = "R6")


# 7. Las zonas de seguridad no rebalsan.
for y in Y:
    modelo.addConstr((quicksum(quicksum(quicksum(u[i,c,t]*z.iloc[i,y]*n[c] for i in I) for c in C)for t in T)<=q[y]), name = "R7")


# 8. Si un curso ya salió de su sala, debe estar en algún pasillo o en una zona segura,
# y el pasillo de origen es el primero que se recorre.
for c in C:
    for t in T:
        modelo.addConstr((\
            quicksum(quicksum((1-z.iloc[i,y])*p[i,c,t] for y in Y) for i in I) +\
            quicksum(quicksum(quicksum(z.iloc[i,y]*u[i,c,u] for y in Y) for i in I) for u in range(1, t + 1)) ==\
            quicksum(quicksum(o.iloc[i,c]*u[i,c,u] for i in I) for u in range(1, t + 1))\
            ), name = "R8")


# 9. Cada curso está en máximo un pasillo a la vez.
for c in C:
    for t in T:
        modelo.addConstr((quicksum(p[i,c,t] for i in I) <= 1), name = "R9")

# 10. Cursos con discapacitados solo pueden pasar por pasillos aptos
for c in C:
    for i in I:
        modelo.addConstr(quicksum(u[i,c,t] for t in T) <= a[i])


# 11. Los responsables de zona van sí o sí a su zona.
for y in Y:
    modelo.addConstr(quicksum(r.iloc[c, y] * u[i,c,t] * z.iloc[i,y] for c in C for i in I for t in T) >= quicksum(r.iloc[c, y]))

# 12. Un curso pasa por un pasillo máximo una vez.
for c in C:
    for i in I:
        modelo.addConstr(quicksum(u[i,c,t] for t in T) <= 1, name = "R12")


# 13. Un curso puede estar en un pasillo si lo empieza a recorrer o si ya estaba en 
# ese pasillo.
for i in I:
    for c in C:
        for t in range(1, len(T)):

            modelo.addConstr(p[i,c,t] <= u[i, c, t] + p[i,c,t-1],name = "R13")

# 14. sc corresponde al tiempo que el curso c espera en su sala antes de comenzar a 
# recorrer su pasillo de origen.
for c in C:
    modelo.addConstr(quicksum(1 - quicksum(o.iloc[i, c]* u[i,c,tp] for i in I for tp in range(1, t)) for t in T) == s[c], name = "R14")

# 15. Los cursos no pueden empezar ocupando un pasillo.
for i in I:
    for c in C:
        modelo.addConstr(p[i, c, 0] == 0, name = "R15a")
        modelo.addConstr(u[i, c, 0] == 0, name = "R15b")

# 16. λ se encuentra dentro de T.
modelo.AddConstr(landa <= quicksum(d[i]/v.iloc[c, i] for c in C for i in I)) 
modelo.update()
# FUNCION OBJETIVO
modelo.setObjective(landa, GRB.MINIMIZE)

if modelo.isFeasible():
    # OPTIMIZAR MODELO
    modelo.optimize()

    # RESULTADOS (revisenlo ns si esta bien)
    if modelo.status == GRB.OPTIMAL:
        print(f"Tiempo mínimo de evacuación: {landa.X}")
        for c in C:
            print(f"Tiempo de salida del curso {c}: {s[c].X}")
        for i in I:
            for c in C:
                for t in T:
                    if p[i,c,t].X > 0.5:
                        print(f"Pasillo {i} es usado por el curso {c} en el tiempo {t}")
                    if u[i,c,t].X > 0.5:
                        print(f"Pasillo {i} es transitado por el curso {c} en el tiempo {t}")
    else:
        print("No se encontró una solución óptima.")

    print("finish")
else:
    print("No es factible")
    print("finish")