
import utils.basic_rules as rl

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import ListedColormap

from math import inf
import pandas as pd




def iterations():
    '''
    PROGRAMA PRINCIPAL
    '''
    sz_r = 400
    sz_c = 400
    D = 0.22
    d = 2
    n_cycles = 100
    d_data={}

    # reproduction rate
    R_0 = 1.15
    t_infecc = 10
    
    
    
    # probabilidad de E -> I
    l_p_I = rl.f_p_I()
    
    # personas infectadas y expuestas al principio
    l_I_int = [ 5 ,  10 ,  15 ,  20 ,  25 ]
    l_E_int = [75 , 150 , 225 , 300 , 375 ]

    ## ciclo para inicializar listas vacías dentro del diccionario con datos
    for i in range(5):
        d_data["E_int:"+str(l_E_int[i])+";I_int:"+str(l_I_int[i])] = []

    #####
    for i in range(5):
        # n_personas I o E corresponden a valores en la i-ésima entrada
        # del arr correspondiente
        I_int = l_I_int[i]
        E_int = l_E_int[i]
        
        print("\n----- I_int:\t%d\tE_int:\t%d-----" % (I_int, E_int))
        
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
        t_L = 0
        d_variable = True

        d_params = {"p_E" :  p_E, 
                    "p_I" :  l_p_I,         # pasamos toda la lista
                    "t_I" :  t_I, 
                    "p_Q" :  p_Q,
                    "t_Q" :  t_Q, 
                    "p_R" :  rl.f_p_R,         # pasamos la función como key
                    "t_R" :  t_R, 
                    "d"   :  d,
                    "t_L" :  t_L, 
                    "t"   :  0, 
                    "d_variable":d_variable}


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
        # la información relevante es la que corresponde a los infectados
        d_data["E_int:"+str(l_E_int[i])+";I_int:"+str(l_I_int[i])] = d_cont["i"]
    ######################################

    # enviar datos a la carpeta de interés
    file_str = "exportedData/b_Fig5b.csv"
    d_data["t"] = time
    df = pd.DataFrame(d_data)
    df.to_csv(file_str)

    # consideraremos solo ciertas llaves de interés, no todas, para el plot
    # relevant keys
    r_ks = list(d_data.keys())
    r_ks.remove("t")
    #ax, fig = plt.subplots()

    fig = df.plot(x = "t", y = r_ks , xlabel = "tiempo (d)",
            ylabel= "fracción de personas infectadas (i)",
            title = "Fig 5b" ,
            color = ["red", "blue", "lime", "cyan", "green"])
    fig = fig.get_figure()

    fig.savefig("b_fig5b_D{}.png".format(D))

    plt.show()
    #print(max(d_cont["i"]))

    print("\n----------- ARCHIVO GENERADO-----------\n")

if __name__ == "__main__":
    iterations()
