
# este archivo será el usado por todos los demás
from random import randint, uniform, sample

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

    if t_R <= t and npa <= p_R:
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
