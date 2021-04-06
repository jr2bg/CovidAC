//#define PY_SSIZE_T_CLEAN
//#include <Python.h>
#include <stdio.h>
#include <stdlib.h>
//#include <iterator>

// estructura de datos a usar para almacenar la información de la ubicación
struct Position {
  int row; //= -400;
  int col;// = -400;
  //row = -400;
};

// estructura de la celda, aquí se almacena la info del valor SEIQR o el tiempo
struct Celda {
  //struct Position pos;
  int tiempo;// = 0;
  int vSEIQR;// = 0;
  //Celda.vSEIQR = 0;
};

// estructura que consiste de todas celdas en el universo
struct Univ {
  struct Celda cell[400][400];
};

// estructura que tiene los contadores de cada uno de las "casillas"
struct Cont_SEIQR {
  int s;
  int e;
  int i;
  int q;
  int r;
};

// estructura para los parámetros a utilizar en la simulación
struct Params {
  float p_E;
  float p_I;
  float p_Q;
  float p_R;
  int t_I;
  int t_Q;
  int t_R;
  int t_L;
  int d;
  int t;

};

// número aleatorio entre 0 y 1
float r_01()
{
    return (float)rand() / (float)RAND_MAX ;
}


struct Position *f_getNeigh(int sz_r, int sz_c, int r,int c, int d, struct Position *ng){
  // la función calcula la vecindad para un d en específico
  // devuelve un puntero de longitud (2d+1) **2 -1 (no se cuenta el r,c)

  //struct Position *ng = NULL;
  // memory allocation para la vecindad de interés
  ng = (struct Position *) malloc
        (((2*d +1) * (2*d + 1) -1) * sizeof (struct Position));

  int k = 0;
  // ciclo para considerar el espacio de interés
  for (int i = -d; i < d+1; i++){
    for (int j = -d; j < d+1; j++){
      if ((r + i >= 0) && (r + i < sz_r) && (c + j>= 0) && (c + j < sz_c)
          &&  ~(i == 0 && j == 0)){
        // le vamos anexando valores a
        (ng + k)->row = r+i;
        (ng + k)->col = c+j;
        //k++;
      }
      // en caso de que no se cumplan las condiciones preestablecidas, no se
      // debe considerar esa posición. Puede no existir dentro del universo
      // Por eso, es posible considerar que tiene entradas menores que el tamaño del universo
      else if (i != 0 && j != 0){
        (ng + k)->row = -400;
        (ng + k)->col = -400;
      }
      k++;
    }
  }
  return ng;
}

// el Universo contendrá 400 * 400 celdas
// de suceptible a expuesto
// la vecindad ng nos dará toda a info. No es necesario conocer la fila/columna
int s_2_e(float p_E, float npa, struct Position * ng, int d, struct Univ Universo){
  int cnt = 0;
  int r, c;
  for (int i = 0; i < (2*d +1) * (2*d +1) -1; i++){
    r = (ng+i)-> row;
    c = (ng+i)-> col;

    // si el valor SEIQR es de expuesto (2) o infectado (3), aumenta la posibilidad
    // de estar expuesto.
    // además, debe tener dimensiones usuales
    if ((r > -300) && (c > -300) &&
        (Universo.cell[r][c].vSEIQR == 2 || Universo.cell[r][c].vSEIQR == 3)){
      cnt++;
    }
  }
  if (npa <= p_E * cnt) return 2;
  return 1;
}

// de expuesto a infectado
// basta tener la celda de interés
int e_2_i(float p_I, float npa, int t_I, struct Celda Univ_rc){
  // si el tiempo en expuesto es mayor que el tiempo de exposición mín t_E
  // y además la probabilidad de pasar es mayor que p_I
  if (t_I <= Univ_rc.tiempo && npa <= p_I) return 3;

  return 2;
}

// de infectado a en cuarentena
int i_2_qr(float p_Q, float p_R, float npa, int t_Q, int t_R, struct Celda Univ_rc){
  // si el tiempo en infectado es mayor que t_Q y adempas
  // el número pseudo-aleatorio es menor que p_Q
  if (t_Q <= Univ_rc.tiempo && npa <= p_Q) return 4;
  else if (t_R <= Univ_rc.tiempo && npa <= (p_Q + p_R) && npa > p_Q) return 5;
  return 3;
}

// de infectado|en cuarentena a recuperado
int q_2_r(float p_R, float npa, int t_R, struct Celda Univ_rc){
  // si el tiempo en infectado es mayor que t_R y adempas
  // el número pseudo-aleatorio es menor que p_R
  if (t_R <= Univ_rc.tiempo && npa <= p_R) return 5;
  return 4;
}

//función de evolución
//
struct Univ evolution(int sz_r,
              int sz_c,
              struct Univ Universo,
              struct Params *Parametros,
              struct Cont_SEIQR *Contador){

  // aumenta el tiempo en 1
  Parametros->t++;

  // reinician los contadores
  Contador -> s = 0;
  Contador -> e = 0;
  Contador -> i = 0;
  Contador -> q = 0;
  Contador -> r = 0;

  time_t t_rdm;
  srand((unsigned) time(&t_rdm));

  // nuevo universo con la info actualizada
  struct Univ New_Univ;

  struct Position * ng = NULL;
  int nv;
  float npa;

  // loop sobre el array
  for (int r = 0; r < sz_r; r++){
    for (int c = 0; c < sz_c ; c++){

      npa = 0.5;//r_01();


      switch (Universo.cell[r][c].vSEIQR) {
        case 1:
          ng = f_getNeigh(sz_r,sz_c,r,c, Parametros->d, ng);
          nv = s_2_e(Parametros->p_E, npa,ng, Parametros->d, Universo);

          // liberamos la memoria en ng
          free(ng);
          // si el nuevo valor sigue siendo el mismo o si ha cambiado
          if (nv == 1){
            New_Univ.cell[r][c].tiempo = Universo.cell[r][c].tiempo + 1;
            New_Univ.cell[r][c].vSEIQR =  1 ;
            Contador -> s++;
          }
          else {
            New_Univ.cell[r][c].tiempo = 0 ;
            New_Univ.cell[r][c].vSEIQR =  nv ;
            Contador -> e++;
          }


        case 2:
          nv = e_2_i(Parametros->p_I, npa, Parametros->t_I, Universo.cell[r][c]);

          // si el nuevo valor sigue siendo el mismo o si ha cambiado
          if (nv == 2){
            New_Univ.cell[r][c].tiempo = Universo.cell[r][c].tiempo + 1;
            New_Univ.cell[r][c].vSEIQR =  2 ;
            Contador -> e++;
          }
          else {
            New_Univ.cell[r][c].tiempo = 0 ;
            New_Univ.cell[r][c].vSEIQR =  nv ;
            Contador -> i++;
          }


        case 3:
          nv = i_2_qr(Parametros->p_Q, Parametros->p_R, npa,
                          Parametros->t_Q, Parametros->t_R, Universo.cell[r][c]);

          if (nv == 3){
            New_Univ.cell[r][c].tiempo = Universo.cell[r][c].tiempo + 1;
            New_Univ.cell[r][c].vSEIQR =  3 ;
            Contador -> i ++;
          }
          else {
            New_Univ.cell[r][c].tiempo = 0 ;
            New_Univ.cell[r][c].vSEIQR =  nv ;

            if (nv == 4) Contador -> q ++;
            else Contador -> r ++;
          }


        case 4:
          nv = q_2_r(Parametros->p_R, npa, Parametros->t_R, Universo.cell[r][c]);

          if (nv == 4){
            New_Univ.cell[r][c].tiempo = Universo.cell[r][c].tiempo + 1;
            New_Univ.cell[r][c].vSEIQR =  4 ;
            Contador -> q++;
          }
          else {
            New_Univ.cell[r][c].tiempo = 0 ;
            New_Univ.cell[r][c].vSEIQR =  nv ;

            Contador -> r++;
          }


        default:
          New_Univ.cell[r][c] = Universo.cell[r][c];

      }

      //
      // // si es una celda vacía o es recuperado, permanece igual
      // if (Universo.cell[r][c].vSEIQR == 0 || Universo.cell[r][c].vSEIQR == 5){
      //   //New_Univ[r][c].tiempo = 0;
      //   New_Univ.cell[r][c] = Universo.cell[r][c];
      // }
      //
      // // si es S
      // else if (Universo.cell[r][c].vSEIQR == 1){
      //   ng = f_getNeigh(sz_r,sz_c,r,c, Parametros->d, ng);
      //   nv = s_2_e(Parametros->p_E, npa,ng, Parametros->d, Universo);
      //
      //   // liberamos la memoria en ng
      //   free(ng);
      //   // si el nuevo valor sigue siendo el mismo o si ha cambiado
      //   if (nv == 1){
      //     New_Univ.cell[r][c].tiempo = Universo.cell[r][c].tiempo + 1;
      //     New_Univ.cell[r][c].vSEIQR =  1 ;
      //     Contador -> s++;
      //   }
      //   else {
      //     New_Univ.cell[r][c].tiempo = 0 ;
      //     New_Univ.cell[r][c].vSEIQR =  nv ;
      //     Contador -> e++;
      //   }
      // }
      //
      // // si es E
      // else if (Universo.cell[r][c].vSEIQR == 2){
      //   nv = e_2_i(Parametros->p_I, npa, Parametros->t_I, Universo.cell[r][c]);
      //
      //   // si el nuevo valor sigue siendo el mismo o si ha cambiado
      //   if (nv == 2){
      //     New_Univ.cell[r][c].tiempo = Universo.cell[r][c].tiempo + 1;
      //     New_Univ.cell[r][c].vSEIQR =  2 ;
      //     Contador -> e++;
      //   }
      //   else {
      //     New_Univ.cell[r][c].tiempo = 0 ;
      //     New_Univ.cell[r][c].vSEIQR =  nv ;
      //     Contador -> i++;
      //   }
      // }
      //
      // // si es I
      // else if (Universo.cell[r][c].vSEIQR == 3){
      //   nv = i_2_qr(Parametros->p_Q, Parametros->p_R, npa,
      //                   Parametros->t_Q, Parametros->t_R, Universo.cell[r][c]);
      //
      //   if (nv == 3){
      //     New_Univ.cell[r][c].tiempo = Universo.cell[r][c].tiempo + 1;
      //     New_Univ.cell[r][c].vSEIQR =  3 ;
      //     Contador -> i ++;
      //   }
      //   else {
      //     New_Univ.cell[r][c].tiempo = 0 ;
      //     New_Univ.cell[r][c].vSEIQR =  nv ;
      //
      //     if (nv == 4) Contador -> q ++;
      //     else Contador -> r ++;
      //   }
      // }
      //
      // // si es Q
      // else if (Universo.cell[r][c].vSEIQR == 4){
      //   nv = q_2_r(Parametros->p_R, npa, Parametros->t_R, Universo.cell[r][c]);
      //
      //   if (nv == 4){
      //     New_Univ.cell[r][c].tiempo = Universo.cell[r][c].tiempo + 1;
      //     New_Univ.cell[r][c].vSEIQR =  4 ;
      //     Contador -> q++;
      //   }
      //   else {
      //     New_Univ.cell[r][c].tiempo = 0 ;
      //     New_Univ.cell[r][c].vSEIQR =  nv ;
      //
      //     Contador -> r++;
      //   }
      // }
    }
  }


  printf("Terminator uwu -----\n" );
  return New_Univ;
}



// función principal (de testeo)
int main(){
  int d = 1;
  int sz_r = 400, sz_c = 400;

  ///// inicialización del universo
  struct Univ Universo;
  for (int i = 0; i < sz_r; ++i){
    for (int j = 0; j < sz_c; ++j){
      Universo.cell[i][j].tiempo = 0;
      Universo.cell[i][j].vSEIQR = 1;
    }
  }
  ///////
  //int d = 2;
  //rand();
//  Universo.cell[0][0].vSEIQR = 1;
//  Universo.cell[0][1].vSEIQR = 1;
  Universo.cell[1][0].vSEIQR = 2;
  Universo.cell[1][1].vSEIQR = 3;
  // for (int r = 0; r < sz_r; ++r){
  //   for (int c = 0; c < sz_c; ++c){
  //     if (Universo.cell[r][c].vSEIQR == 1) {
  //       //printf("fila:\t%d;\tcolumna:\t%d\n",r,c);
  //
  //       struct Position * ng = f_getNeigh(sz_r, sz_c, r, c, d);
  //       //
  //       //printf("valor a pasar:\t%d\n", s_2_e(0.2, 0.8, ng, d, Universo));
  //     }
  //   }
  // }

  struct Cont_SEIQR Contador;

  struct Params Parametros;
  Parametros.p_E = 0.5;
  Parametros.p_I = 0.5;
  Parametros.p_Q = 0.1;
  Parametros.p_R = 0.12;
  Parametros.t_I = 8;
  Parametros.t_Q = 2;
  Parametros.t_R = 18;
  Parametros.t_L = 150;
  Parametros.d = 3;
  Parametros.t = 0;
  printf("******** Empieza la evolucion *********** \n");
  evolution(sz_r, sz_c,
            Universo, &Parametros,&Contador);

}
