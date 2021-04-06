
# Codigo que barre un intervalo para encontrar los valores de la gráfica
#
#

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import ListedColormap

import csv
import pandas as pd

import random

def f_getNeigh(sz_r, sz_c,r,c,d):
    '''
    función que da la vecindad para el elemento ubicado en
    la fila r y columna c
    sz_r y sz_c corresponden al tamaño del array
    d -> radio de la esfera de influencia
    '''
    # selección del radio de la esfera de influencia
    #npa = random.uniform(0,1)
    #rd = 1 if npa < 62 else 0
    rd = random.randint(0,d)
    ng = []

    # ciclo de identificación de las posiciones de la vecindad
    for i in range(-rd, rd +1):
        for j in range(-rd, rd+1):
            if r + i >= 0 and r + i < sz_r and c + j>= 0 and c + j < sz_c and \
                not (i == 0 and j == 0):
                ng.append((r+i,c+j))
    return ng


def s_2_e(p_E, npa, ng, arr_population):
    '''
    función que determina si la celda puede pasar de S a E
    para ello, la celda debe ser suceptible
    Se requiere la vecindad, y la probabilidad de pasar a E
    así como la población arr_population
    también se requiere de un número pseudo-aleatorio npa, para determinar si pasa o no a E
    '''
    cnt = 0
    for r,c in ng:
        if arr_population[r][c] == 2 or arr_population[r][c] == 3:
            cnt += 1

    if npa <= p_E * cnt:
        return 2 # pasa a Expuesto
    return 1    # queda en Suceptible


def e_2_i(p_I, npa, t_I, t):
    '''
    función que determina si la celda pasa de Expuesto (2) a Infectado (3)
    p_I -> probabilidad de pasar a infectado
    npa -> número pseudo aleatorio
    t_I -> tiempo mínimo de permanencia en expuesto
    t -> tiempo que ha pasado la celda en Expuesto
    '''

    if t_I <= t and npa <= p_I:
        return 3
    return 2


def i_2qr(p_Q, p_R, npa, t_Q, t_R, t):
    '''
    función que determina si la celda en infectado (3) pasa a
    en cuarentena (4) o a recuperado (5)
    p_Q -> probabilidad de pasar a en cuarentena
    p_R -> probabilidad de pasar a recuperado
    npa -> número pseudo aleatorio
    t_Q -> tiempo mínimo para entrar a Q
    t_R -> tiempo mínimo para entrar a recuperado
    t   -> tiempo en I
    '''

    if t_Q <= t and npa <= p_Q:
        return 4
    # mejora de la condición para que pase a recuperado
    if t_R <= t and p_Q < npa <= p_Q+p_R:
        return 5

    return 3


def q_2_r(p_R, npa, t_R, t):
    '''
    función que determina si de Q (4) pasa a R (5)
    p_R -> probabilidad de pasar a R
    npa -> número pseudo aleatorio
    t_R -> tiempo mínimo para que entre a R
    t   -> tiempo que ha pasado en Q
    '''
    if t_R <= t and npa <= p_R:
        return 5

    return 4

def f_initPop(sz_r, sz_c, D):
    '''
    función para inicializar la población

    consiste en entregar un arreglo de tamaño sz_r * sz_c, tal que tenga una
    densidad de población D
    '''
    arr_population = [[0 for i in range(sz_c)] for j in range(sz_r)]
    # total de la población
    t_pop = int(D * sz_r * sz_c)

    # se eligen t_pop celdas de arr_population para que sean los habitantes
    lst = [(r,c) for c in range(sz_c) for r in range(sz_r)]

    habs = random.sample(lst, t_pop)

    # todos los habitantes son suceptibles en el arreglo de la población
    for r,c in habs:
        arr_population[r][c] = 1

    return arr_population, habs


def f_evolution(sz_r, sz_c, d_params, arr_tiempo, arr_nt, arr_population, arr_evo):
    '''
    función de evolución, cambia los array

    python pasa arrays por dirección, así que se pueden cambiar los valores
    del array dentro de la función y los cambios permanecen
    '''

    # incremento del tiempo en 1
    d_params["t"] += 1
    # inicialización del array que contendrá el conteo de cada sección
    cnt = [0 for i in range(6)]

    # diccionario para almacenar los cambios de uno a otro
    # las key representan que entra a ese estado, y en la lista asociada
    # cada elemento es una tupla con la posición de la celda
    d_changes = {2:[], 3:[], 4:[], 5:[]}

    for i in range(sz_r):
        for j in range(sz_c):

            ############## Reglas

            # si es suceptible
            if arr_population[i][j] == 1:

                # un lockdown corresponde a un valor de d: 0 <= d <= 1
                d = d_params["d"] if d_params["t"] <= d_params["t_L"] else 1
                # obtenemos vecindad
                ng = f_getNeigh(sz_r, sz_c,i,j, d)

                # obtenemos el popsible cambio
                npa = random.uniform(0,1)
                nv = s_2_e(d_params["p_E"], npa, ng, arr_population)
                if nv == 2:
                    cnt[0] += 1

                    d_changes[nv].append((i,j))

            # si es expuesto
            elif arr_population[i][j] == 2:
                cnt[2] += 1
                npa = random.uniform(0,1)
                nv = e_2_i(d_params["p_I"], npa, d_params["t_I"], arr_tiempo[i][j])
                if nv != 2:
                    d_changes[nv].append((i,j))
                else:
                    arr_tiempo[i][j] += 1

            # si es infectado
            elif arr_population[i][j] == 3:
                npa = random.uniform(0,1)
                nv = i_2qr(d_params["p_Q"], d_params["p_R"], npa, d_params["t_Q"], d_params["t_R"], arr_tiempo[i][j])
                if nv != 3:
                    d_changes[nv].append((i,j))
                else:
                    arr_tiempo[i][j] += 1

            # si está en cuarentena
            elif arr_population[i][j] == 4:
                npa = random.uniform(0,1)
                nv = q_2_r(d_params["p_R"], npa, d_params["t_R"], arr_tiempo[i][j])
                if nv != 4:
                    d_changes[nv].append((i,j))
                else:
                    arr_tiempo[i][j] += 1

            # recuperados o casillas vacías
            else:
                nv = arr_population[i][j]
                arr_tiempo[i][j] += 1

            ############## Fin de las REGLAS

    # como los cambios se almacenaron en un diccionario
    # iteramos sobre los elementos y los cambiamos en el array de la población,
    # además de inicializar el tiempo de estos cambios en cero
    for key, value in d_changes.items():
        for r,c in value:
            arr_population[r][c] = key
            arr_tiempo[r][c] = 0

def data_fig3a(n_habs , d_cont,arr_population):
    s = 0
    e = 0
    i = 0
    q = 0
    r = 0
    for rw in arr_population:
        for val in rw:
            if val == 1:
                s += 1
            elif val == 2:
                e += 1
            elif val == 3:
                i += 1
            elif val == 4:
                q += 1
            elif val == 5:
                r += 1
    d_cont["s"].append(s / n_habs)
    d_cont["e"].append(e / n_habs)
    d_cont["i"].append(i / n_habs)
    d_cont["q"].append(q / n_habs)
    d_cont["r"].append(r / n_habs)

    return d_cont





def iterations():
    '''
    PROGRAMA PRINCIPAL
    '''
    #### ANIMACION
    cmap = ListedColormap(["black", "blue", "green", "red", "cyan", "yellow"])
    #fig = plt.figure(dpi = 200, tight_layout = False, constrained_layout = True)
    #plots = []


    n_cycles = 101
    d_data = {}  # "E_int:"+str()+";I_int:"+str()

    sz_r = 400
    sz_c = 400
    l_D = [0.22, 0.25 , 0.5 , 0.75 , 1]
    l_p_E = [0.2 , 0.4 , 0.6 , 0.8 , 1]



    for D in l_D:
        ## ciclo para inicializar listas vacías dentro del diccionario con datos
        for i in range(5):
            d_data["p_E="+str(l_p_E[i])] = []

        # hay 5 elementos en cada una de las listas
        for p_E in l_p_E:
        ##############################
            # pueden cambiar p_E, p_I, p_Q, p_R y t_Q => t_I y t_R NO CAMBIAN
            #p_E =  0.5
            p_I =  0.5
            t_I = 8     ####
            p_Q =  0.1
            t_Q =  2    ####
            p_R = 0.12
            t_R = 18
            d = 2
            t_L = 0

            d_params = {"p_E" :  p_E, "p_I" :  p_I, "t_I" : t_I, "p_Q" :  p_Q,
                        "t_Q" :  t_Q, "p_R" : p_R, "t_R" : t_R, "d" : d,
                         "t_L" : t_L, "t":0}

            # n_personas I o E corresponden a valores en la i-ésima entrada
            # del arr correspondiente
            I_int = 6
            E_int = 200

            arr_population, habs = f_initPop(sz_r, sz_c, D)
            arr_tiempo = [[0 for i in range(sz_c)] for j in range(sz_r)]

            n_habs = len(habs)

            #### población infectada o expuesta al tiempo 0
            pop_i0 = habs[:I_int]
            pop_e0 = habs[I_int: E_int + I_int]



            for r,c in pop_i0:
                arr_population[r][c] = 3
            for r,c in pop_e0:
                arr_population[r][c] = 2
            ####

            arr_evo = arr_population.copy()
            arr_nt = arr_tiempo.copy()

            #### tiempo primer infectado ---> t_fi
            t_fi = 0

            #### gráficas
            #frac_pers_i = []
            time = []



            ##### Fig 3a
            # no hay en cuarentena ni recuperados, solo suceptibles, expuestos e infects
            d_cont = {"s": [(n_habs - I_int - E_int)/n_habs],
                      "e": [E_int/n_habs],
                      "i":[I_int/n_habs],
                      "q": [0],
                      "r": [0]}

            ####
            #plt.axis('off')
            #img = plt.imshow(arr_population, vmin = 0, vmax = 5, cmap = cmap)
            #plots.append([img])
            #frac_pers_i.append(sum([rw.count(3) for rw in arr_population])/ int(D * sz_r * sz_c))
            time.append(0)




            for c in range(1,n_cycles):
                print(c)
                f_evolution(sz_r, sz_c, d_params, arr_tiempo, arr_nt, arr_population, arr_evo)

                #plt.axis('off')
                #img = plt.imshow(arr_population, vmin = 0, vmax = 5, cmap = cmap)
                #plots.append([img])
                #frac_pers_i.append(sum([rw.count(3) for rw in arr_population])/ int(D * sz_r * sz_c))

                d_cont = data_fig3a(n_habs , d_cont, arr_population)

                time.append(c)

            # la información relevante es la que corresponde a los infectados
            d_data["p_E="+str(p_E)] = d_cont["i"]

        ######################################

        # enviar datos a la carpeta de interés
        file_str = "fig5c_test/D{}.png".format(D)
        d_data["t"] = time
        df = pd.DataFrame(d_data)
        #df.to_csv(file_str)

        # consideraremos solo ciertas llaves de interés, no todas, para el plot
        # relevant keys
        r_ks = list(d_data.keys())
        r_ks.remove("t")


        fig = df.plot(x = "t", y = r_ks , xlabel = "tiempo (d)",
                ylabel= "fracción de personas infectadas (i)",
                title = "Fig 5c" ,
                color = ["red", "blue", "lime", "cyan", "green"]).get_figure()
        fig.savefig(file_str)
        #plt.show()

    #print("\n----------- ARCHIVO GENERADO-----------\n")

    # generar la animación
    # ani = animation.ArtistAnimation(fig, plots, interval=100, blit=True,
    #                                 repeat_delay=1000)
    # Writer = animation.writers['ffmpeg']
    # writer = Writer(fps=15, metadata=dict(artist='Me'), bitrate=1800)
    # ani.save("test_fig5b.mp4", writer = writer)

if __name__ == "__main__":
    iterations()
