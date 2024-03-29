
import utils.basic_rules as rl

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import ListedColormap

from math import inf
import pandas as pd
from scipy.stats import lognorm

import numpy as np

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


def iterations():
    '''
    PROGRAMA PRINCIPAL
    '''
    sz_r = 400
    sz_c = 400
    D = 1
    d = 2
    n_cycles = 100
    d_data={}

    # reproduction rate
    R_0 = 1.15
    t_infecc = 10
    
    l_t_L = [1,5,10,15,20]
    
    # probabilidad de E -> I
    l_p_I = f_p_I()
    for i in range(5):
        d_data["t_L=" + str(l_t_L[i])] = []

    #####
    for t_L in l_t_L:        
        print("\n----- D:\t", D, "\td:\t", d , "-----" )
        ##############################
        # pueden cambiar p_E, p_I, p_Q, p_R y t_Q => t_I y t_R NO CAMBIAN
        # número de personas distintas con las que tiene contacto una persona
        # en este caso,
        n_p = D * (2*d + 1)**2
        
        # probabilidad S -> E
        p_E = R_0 / (n_p * t_infecc)

        #p_I =  0.5
        t_I = 8     ####
        p_Q =  0.1
        t_Q =  2    ####
        #p_R = 0.12
        t_R = 18
        #d = 2
        #t_L = inf
        d_variable = True

        d_params = {"p_E" :  p_E, 
                    "p_I" :  l_p_I,         # pasamos toda la lista
                    "t_I" :  t_I, 
                    "p_Q" :  p_Q,
                    "t_Q" :  t_Q, 
                    "p_R" :  f_p_R,         # pasamos la función como key
                    "t_R" :  t_R, 
                    "d"   :  d,
                    "t_L" :  t_L, 
                    "t"   :  0, 
                    "d_variable":d_variable}

        # personas infectadas y expuestas al principio
        I_int = 6
        E_int = 200

        arr_population, habs = rl.f_initPop(sz_r, sz_c, D)
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

        #### ANIMACION
        #cmap = ListedColormap(["black", "blue", "green", "red", "cyan", "yellow"])
        #fig = plt.figure(dpi = 200, tight_layout = False, constrained_layout = True)
        #plots = []

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
            rl.f_evolution(sz_r, sz_c, d_params, arr_tiempo, arr_nt, arr_population, arr_evo)

            #plt.axis('off')
            #img = plt.imshow(arr_population, vmin = 0, vmax = 5, cmap = cmap)
            #plots.append([img])
            #frac_pers_i.append(sum([rw.count(3) for rw in arr_population])/ int(D * sz_r * sz_c))

            d_cont = rl.data_exp(n_habs , d_cont, arr_population)

            time.append(c)
        d_data["t_L=" + str(t_L)] = d_cont["i"]
    ######################################

    # enviar datos a la carpeta de interés
    file_str = "exportedData/b_Fig5a.csv"
    d_data["t"] = time
    df = pd.DataFrame(d_data)
    df.to_csv(file_str)

    # consideraremos solo ciertas llaves de interés, no todas, para el plot
    # relevant keys
    r_ks = list(d_data.keys())
    r_ks.remove("t")
    #ax, fig = plt.subplots()

    df.plot(x = "t", y = r_ks , xlabel = "tiempo (d)",
            ylabel= "fracción de personas infectadas (i)",
            title = "Fig 5a" ,
            color = ["red", "blue", "lime", "cyan", "green"])

    plt.show()
    #print(max(d_cont["i"]))

    print("\n----------- ARCHIVO GENERADO-----------\n")

if __name__ == "__main__":
    iterations()
