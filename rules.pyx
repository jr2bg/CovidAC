from random import sample, uniform

def f_getNeigh(int sz_r, int sz_c, int r, int c):
    '''
    función que da la vecindad para el elemento ubicado en
    la fila r y columna c
    sz_r y sz_c corresponden al tamaño del array
    '''
    cdef list ng = []
    for i in range(-1,2):
        for j in range(-1,2):
            if r + i >= 0 and r + i < sz_r and c + j>= 0 and c + j < sz_c and \
                not (r == 0 and j == 0):
                ng.append((r+i,c+j))
    return ng


def s_2_e(float p_E, float npa,list ng, list arr_population):
    '''
    función que determina si la celda puede pasar de S a E
    para ello, la celda debe ser suceptible
    Se requiere la vecindad, y la probabilidad de pasar a E
    así como la población arr_population
    también se requiere de un número pseudo-aleatorio npa, para determinar si pasa o no a E
    '''
    cdef int cnt = 0
    for r,c in ng:
        #print(r,c)
        if arr_population[r][c] == 2 or arr_population[r][c] == 3:
            cnt += 1

    if npa <= p_E * cnt:
        #t = 0
        return 2 # pasa a Expuesto
    #t += 1
    return 1    # queda en Suceptible


def e_2_i(float p_I, float npa, int t_I, int t):
    '''
    función que determina si la celda pasa de Expuesto (2) a Infectado (3)
    p_I -> probabilidad de pasar a infectado
    npa -> número pseudo aleatorio
    t_I -> tiempo mínimo de permanencia en expuesto
    t -> tiempo que ha pasado la celda en Expuesto
    '''

    if t_I <= t and npa <= p_I:
        #t = 0
        return 3
    #t += 1
    return 2


def i_2qr(float p_Q, float p_R, float npa, int t_Q, int t_R, int t):
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
        #t = 0
        return 4
    if t_R <= t and npa <= p_R:
        #t = 0
        return 5

    #t += 1
    return 3


def q_2_r(float p_R, float npa, int t_R, int t):
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

def f_initPop(int sz_r, int sz_c, float D):
    '''
    función para inicializar la población
    '''
    cdef list arr_population = [[0 for i in range(sz_c)] for j in range(sz_r)]
    # total de la población
    cdef int t_pop = int(D * sz_r * sz_c)

    # se eligen t_pop celdas de arr_population para que sean los habitantes
    lst = [(r,c) for c in range(sz_c) for r in range(sz_r)]
    #print(t_pop)
    habs = sample(lst, t_pop)

    # a todos los habitantes son suceptibles en el arreglo de la población
    for r,c in habs:
        arr_population[r][c] = 1

    return arr_population, habs


def iterations():
    '''
    PROGRAMA PRINCIPAL
    '''
    cdef int sz_r = 400
    cdef int sz_c = 400
    cdef float D = 0.1
    cdef int n_cycles = 1000

    # pueden cambiar p_E, p_I, p_Q, p_R y t_Q => t_I y t_R NO CAMBIAN
    cdef float p_E =  0.5
    cdef float p_I =  0.5
    cdef int t_I = 8
    cdef float p_Q =  0.1
    cdef int t_Q =  2
    cdef float p_R = 0.12
    cdef int t_R = 18

    # personas infectadas y expuestas al principio
    cdef int I_int = 6
    cdef int E_int = 200

    arr_population, habs = f_initPop(sz_r, sz_c, D)
    cdef list arr_tiempo = [[0 for i in range(sz_c)] for j in range(sz_r)]

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

    c = 0, i = 0, j = 0
    cdef float npa
    while c < n_cycles:
    #for c in range(n_cycles):
        print(c)
        i = 0
        while i < sz_r:
        #for i in range(sz_r):
            j = 0
            while j < sz_c:
            #for j in range(sz_c):

                ############## Reglas

                # si es suceptible
                if arr_population[i][j] == 1:
                    # obtenemos vecindad
                    ng = f_getNeigh(sz_r, sz_c,i,j)

                    # obtenemos el popsible cambio
                    npa = uniform(0,1)
                    nv = s_2_e(p_E, npa, ng, arr_population)

                # si es expuesto
                elif arr_population[i][j] == 2:
                    npa = uniform(0,1)
                    nv = e_2_i(p_I, npa, t_I, arr_tiempo[i][j])

                # si es infectado
                elif arr_population[i][j] == 3:
                    npa = uniform(0,1)
                    nv = i_2qr(p_Q, p_R, npa, t_Q, t_R, arr_tiempo[i][j])

                # si está en cuarentena
                elif arr_population[i][j] == 4:
                    npa = uniform(0,1)
                    nv = q_2_r(p_R, npa, t_R, arr_tiempo[i][j])

                else:
                    nv = 0

                ############## Fin de las REGLAS

                # si pasa a otro estado
                if nv != arr_population[i][j]:
                    arr_nt[i][j] = 0
                    arr_evo[i][j] = nv

                # mientras no sea una casilla en blanco, vacía, estado 0
                elif arr_population[i][j] != 0:
                    arr_nt[i][j] = arr_tiempo[i][j] + 1
                    arr_evo[i][j] = arr_population[i][j]

                j += 1

            i += 1

        #actualización de los array a considerar
        arr_tiempo = arr_nt.copy()
        arr_population = arr_evo.copy()
        #arr_tiempo = arr_nt
        #arr_population = arr_evo

    c += 1
#if __name__ == "__main__":
#    iterations()
