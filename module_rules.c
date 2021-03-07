//#define PY_SSIZE_T_CLEAN
//#include <Python.h>
#include <stdio.h>
#include <stdlib.h>
//#include <iterator>

int *f_getNeigh(int sz_r, int sz_c, int r,int c){
  static int ng[8][2];
  int k = 0;
  for (int i = -1; i < 2; i++){
    for (int j = -1; j < 2; j++){
      if ((r + i >= 0) && (r + i < sz_r) && (c + j>= 0) && (c + j < sz_c)
          &&  ~(i == 0 && j == 0)){
        ng[k][0] = r+i;
        ng[k][1] = c+j;
      }
    }
  }
  return &ng[0][0];
}
// *( *(pntr_2d +i) + j)
int s_2_e(float p_E, float npa, int * ng, int ** arr_population){
  int cnt = 0;
  int r, c;
  for (int i = 0; i < 8; i++){
    r = *(ng+i*2); // ng [i][0]
    c = *(ng+i*2 +1); //ng[i][1];

    if (*(*(arr_population + r) + c) == 2 ||
        *(*(arr_population +r) + c) == 3){
      cnt++;
    }
  }
  if (npa <= p_E * cnt) return 2;
  return 1;
}

int main(){
  int * ng = f_getNeigh(7,7,2,1);
  int sz_r = 7, sz_c = 8;
  int arr_population[2][3] = {{1,2,3},{4,5,6}};
  int ** ptr_arrP = &arr_population[0];

  //s_2_e(0.4, 0.3, ng, int ** arr_population)

  for (int i = 0; i < 8; i++){
    printf("%d", *(ng + i));
  }

}
