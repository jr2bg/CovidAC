
import utils.basic_rules as rl

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import ListedColormap

from math import inf
import pandas as pd

import numpy as np


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
    l_D = [0.5]
    l_d = [1,2]
    n_cycles = 100
    imx_1 = []
    imx_2 = []

    # reproduction rate
    R_0 = 1.15
    t_infecc = 10





    lgnormal = np.random.lognormal(lgnml_mu, lgnml_sigma2, 100)

    #####
    for D in l_D:
        for d in l_d:
            print("\n----- D:\t", D, "\td:\t", d , "-----" )
        ##############################
            # pueden cambiar p_E, p_I, p_Q, p_R y t_Q => t_I y t_R NO CAMBIAN
            # número de personas distintas con las que tiene contacto una persona
            # en este caso,
            n_p = D * (2*d + 1)**2

            p_E = R_0 / (n_p * t_infecc)

            p_I =  0.5
            t_I = 8     ####
            p_Q =  0.1
            t_Q =  2    ####
            p_R = 0.12
            t_R = 18
            #d = 2
            t_L = inf
            d_variable = False

            d_params = {"p_E" :  p_E, "p_I" :  p_I, "t_I" : t_I, "p_Q" :  p_Q,
                        "t_Q" :  t_Q, "p_R" : p_R, "t_R" : t_R, "d" : d,
                         "t_L" : t_L, "t":0, "d_variable":d_variable}

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
            #time = []

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
            #time.append(0)




            for c in range(1,n_cycles):
                print(c)
                rl.f_evolution(sz_r, sz_c, d_params, arr_tiempo, arr_nt, arr_population, arr_evo)

                #plt.axis('off')
                #img = plt.imshow(arr_population, vmin = 0, vmax = 5, cmap = cmap)
                #plots.append([img])
                #frac_pers_i.append(sum([rw.count(3) for rw in arr_population])/ int(D * sz_r * sz_c))

                d_cont = rl.data_exp(n_habs , d_cont, arr_population)

                #time.append(c)
            if d == 1:
                imx_1.append(max(d_cont["i"]))
            else:
                imx_2.append(max(d_cont["i"]))
        ######################################

    # enviar datos a la carpeta de interés
    file_str = "exportedData/b_Fig3b.csv"
    #d_cont["t"] = time
    df = pd.DataFrame({"D": l_D, "imx_1":imx_1, "imx_2":imx_2})
    df = df[(df["D"]<= 0.5) & (df["D"] > 0.05) ]
    df.to_csv(file_str)
    df.plot(x = "D", y = ["imx_1", "imx_2"], color = ["red", "yellow"])
    plt.show()

    print("\n----------- ARCHIVO GENERADO-----------\n")

    # # generar la animación
    # ani = animation.ArtistAnimation(fig, plots, interval=100, blit=True,
    #                                 repeat_delay=1000)
    # Writer = animation.writers['ffmpeg']
    # writer = Writer(fps=15, metadata=dict(artist='Me'), bitrate=1800)
    # ani.save("evolucion_d_{}.mp4".format(d), writer = writer)

if __name__ == "__main__":
    iterations()
