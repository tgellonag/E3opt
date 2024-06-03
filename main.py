import modelo as m

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
tiempo_max = m.funcion( carpeta_parametros=carpeta_parametros, multiplicador= 5 )

# Con este resultado, podemos definir una mejor cota superior para el tiempo máximo que los cursos se demorarían en evacuar
# para así utilizar esta cota para el modelo que se busca optimizar (con periodos de 5s).
m.funcion(carpeta_parametros=carpeta_parametros, multiplicador=1, tiempo_max=tiempo_max, final=True)

# Todo este proceso se realiza con el fin de acortar el tiempo de ejecución del programa, para cumplir con el objetivo de
# resolver el modelo en menos de 30 min desde que se ejecuta main.py y se selecciona la opcion 'parametros_dsla_parvulario'.