import modelo as m

carpetas_parametros = ["parametros_mediano", "parametros_chico", "parametros_enano",'parametros_dsla_parvulario']
for i in range(len(carpetas_parametros)):
    print(f"{i+1}. {carpetas_parametros[i]}")
opcion = input("Ingrese el número de la carpeta de parámetros que desea utilizar: ")
if opcion == '1':
    carpeta_parametros = carpetas_parametros[0]
elif opcion == '2':
    carpeta_parametros = carpetas_parametros[1]
elif opcion == '3':
    carpeta_parametros = carpetas_parametros[2]
elif opcion == '4':
    carpeta_parametros = carpetas_parametros[3]

tiempo_max = m.funcion( carpeta_parametros=carpeta_parametros, multiplicador= 5 )

m.funcion(carpeta_parametros=carpeta_parametros, multiplicador=1, tiempo_max=tiempo_max, final=True)