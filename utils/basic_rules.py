# -*- coding: utf-8 -*-
# este archivo será el usado por todos los demás
from random import randint, uniform, sample
import numpy as np
from scipy.stats import lognorm

def f_getNeigh(sz_r, sz_c,r,c,d, d_variable = True):
    '''
    función que da la vecindad para el elemento ubicado en
    la fila r y columna c
    sz_r y sz_c corresponden al tamaño del array
    d -> radio máximo de la esfera de influencia
    d_variable -> radio de la esfera de influencia es variable o es d
    '''
    if d_variable:
        rd = randint(0,d)
    else:
        rd = d

    ng = []
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


def e_2_i(l_p_I, npa, t_I, t):
    '''
    función que determina si la celda pasa de Expuesto (2) a Infectado (3)
    p_I -> probabilidad de pasar a infectado
    npa -> número pseudo aleatorio
    t_I -> tiempo mínimo de permanencia en expuesto
    t -> tiempo que la celda ha pasado en Expuesto
    '''
    # si el tiempo que ha pasado la celda en Expuesto es mayor a la cantidad
    # de entradas en la lista, consideramos el valor de la última entrada--->??
    #   ----->>> POR QUÉ??
    if t >= len(l_p_I):
        p_I = l_p_I[-1]
    else:
        p_I = l_p_I[t]

    if t_I <= t and npa <= p_I:
        return 3
    return 2


def i_2qr(p_Q, f_p_R, npa, t_Q, t_R, t):
    '''
    función que determina si la celda en infectado (3) pasa a
    en cuarentena (4) o a recuperado (5)
    p_Q -> probabilidad de pasar a en cuarentena
    f_p_R -> función que indica la probabilidad de pasar a R como f(t)
    npa -> número pseudo aleatorio
    t_Q -> tiempo mínimo para entrar a Q
    t_R -> tiempo mínimo para entrar a recuperado
    t   -> tiempo en I
    '''

    if t_Q <= t and npa <= p_Q:
        return 4

    if t_R <= t and npa <= f_p_R(t):
        return 5

    return 3


def q_2_r(f_p_R, npa, t_R, t):
    '''
    función que determina si de Q (4) pasa a R (5)
    f_p_R -> función que indica la probabilidad de pasar a R como f(t)
    npa -> número pseudo aleatorio
    t_R -> tiempo mínimo para que entre a R
    t   -> tiempo que ha pasado en Q
    '''
    if t_R <= t and npa <= f_p_R(t):
        return 5

    return 4

def f_initPop(sz_r, sz_c, D):
    '''
    función para inicializar la población
    '''
    arr_population = [[0 for i in range(sz_c)] for j in range(sz_r)]
    # total de la población
    t_pop = int(D * sz_r * sz_c)

    # se eligen t_pop celdas de arr_population para que sean los habitantes
    lst = [(r,c) for c in range(sz_c) for r in range(sz_r)]

    habs = sample(lst, t_pop)

    # todos los habitantes son suceptibles en el arreglo de la población
    for r,c in habs:
        arr_population[r][c] = 1

    return arr_population, habs


def f_evolution(sz_r, sz_c, d_params, arr_tiempo, arr_nt, arr_population, arr_evo):
    '''
    función de evolución, cambia los array
    d_params -> diccionario que contendrá la información de:
                    p_E,
                    p_I,
                    t_I,
                    p_Q,
                    t_Q,
                    p_R,
                    t_R,
                    d,
                    t_L,
                    t,
                    d_variable

    '''
    d_params["t"] += 1
    cnt = [0 for i in range(6)]

    # diccionario para almacenar los cambios de uno a otro
    d_changes = {2:[], 3:[], 4:[], 5:[]}

    for i in range(sz_r):
        for j in range(sz_c):

            ############## Reglas

            # si es suceptible
            if arr_population[i][j] == 1:

                d = d_params["d"] if d_params["t"] <= d_params["t_L"] else 1
                # obtenemos vecindad
                ng = f_getNeigh(sz_r, sz_c,i,j, d, d_params["d_variable"])

                # obtenemos el popsible cambio
                npa = uniform(0,1)
                nv = s_2_e(d_params["p_E"], npa, ng, arr_population)
                if nv == 2:
                    cnt[0] += 1

                    d_changes[nv].append((i,j))

            # si es expuesto
            elif arr_population[i][j] == 2:
                cnt[2] += 1
                npa = uniform(0,1)
                nv = e_2_i(d_params["p_I"], npa, d_params["t_I"], arr_tiempo[i][j])
                if nv != 2:
                    d_changes[nv].append((i,j))
                else:
                    arr_tiempo[i][j] += 1

            # si es infectado
            elif arr_population[i][j] == 3:
                npa = uniform(0,1)
                nv = i_2qr(d_params["p_Q"], d_params["p_R"], npa, d_params["t_Q"], d_params["t_R"], arr_tiempo[i][j])
                if nv != 3:
                    d_changes[nv].append((i,j))
                else:
                    arr_tiempo[i][j] += 1

            # si está en cuarentena
            elif arr_population[i][j] == 4:
                npa = uniform(0,1)
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
    for key, value in d_changes.items():
        for r,c in value:
            arr_population[r][c] = key
            arr_tiempo[r][c] = 0


def data_exp(n_habs , d_cont,arr_population):
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


################################
########################## 
#############              PROBABILIDADES DE TRANSICIÓN
##########################
################################


# Probabilidad de que una persona que estuvo en contacto con una persona contagiada
# pase a expuesto
# https://www.news18.com/news/lifestyle/for-how-long-a-covid-19-patient-can-infect-others-myupchar-2888611.html
def f_p_E(R_0, D, d, t_infeccioso = 10):
    # número de personas que pudieron entrar en contacto con alguien
    n_p = D * ((2 * d + 1 ) **2 -1)
    
    return R_0 / (n_p * t_infeccioso)


# probabilidad de que E pase a I
# lauer etal 2020
# consideraremos los siguientes valores obtenidos de tratar de reproducir la
# gráfica del artículo de Lauer etal 2020
# Se calculará al principio
def f_p_I(s= 0.465, loc = 0, scale = 5.5, fst_q = 0.0001, lst_q = 0.9999):
    
    st = lognorm.ppf(fst_q, s, scale = scale)
    nd = lognorm.ppf(lst_q, s, scale = scale)
    
    x_cont = np.linspace(st,nd,100)
    lognm_pdf = lognorm.pdf(x_cont,s, loc, scale)
    
    # convertimos a una lista de enteros con índices los días y 
    # las entradas los valores de la probabilidad
    # prob_days[i] = sum ( lognm_pdf[j] | x_cont[j] = i div) / cont
    prob_days = []
    i = 0
    sm = 0
    cont = 0
    
    for j in range(len(x_cont)):
        
        # función monótona creciente
        if i <= x_cont[j] < i+1:
            sm += lognm_pdf[j]
            cont += 1
        else:
            prob_days.append(sm / cont)
            i += 1
            cont = 1
            sm = lognm_pdf[j]
    
    # la última prob se debe anexar al terminar de ejecutarse el código
    prob_days.append(sm / cont)
    
    return prob_days
    


## Probabilidad de recuperación.
## barman etal 2020
def f_p_R(t):
    ## no aparece probabilidad de recuperación
    if t < 10:
        return 0
    elif 10 <=t < 15:
        return 0.046512
    elif 15 <= t < 18:
        return 0.293023
    elif 18 <= t < 20:
        return 0.395349
    elif 20 <= t < 21:
        return 0.465116
    elif 21 <= t < 23:
        return 0.465116
    elif 23 <= t < 25:
        return 0.477419
    elif 25 <= t < 27:
        return 0.534884
    elif 27 <= t < 37:
        return 0.557634
    elif t >= 37:
        return 0.557634
