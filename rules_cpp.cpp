#include <iostream>
#include <random>
#include <algorithm>
#include <iterator>
#include <vector>
#include <unordered_map>
#include <string>
#include <chrono>

using namespace std;

/*

g++ -std=c++17

*/

// número aleatorio
unsigned seed = chrono::system_clock::now().time_since_epoch().count();
default_random_engine generator (seed);
uniform_real_distribution<float> distribution (0.0,1.0);


vector<vector<int>> f_getNeigh(int sz_r, int sz_c, int r, int c, int d, vector<vector<int>> ng){

  int rd = d;
  //rd = random(0,d);
  //vector<vector<int>> ng;
  ng = vector<vector<int>> ((2 * d + 1) * (2 * d + 1), vector<int> (2));
  int k = 0;
  for (int i = -rd; i <= rd; i++){
    for (int j = -rd; j <= rd; j++){
      if (r +i >= 0 && r+i < sz_r && c+j >= 0 && c+i < sz_c && ~(i == 0 && j == 0)){
        //ng.push_back({r+i, c+j});
        ng[k] = {r+i, c+j};
      }

      else ng[k] = {-400,-400};
      k++;
    }
  }

  return ng;

}

int s_2_e(float p_E, float npa, vector<vector<int>> ng, vector<vector<int>> arr_population){
  int cnt = 0;
  for (auto el : ng){
    if ( el[0] > -400 && el[1] > -400 &&
      arr_population[el[0]][el[1]] == 2 && arr_population[el[0]][el[1]] == 3){
      cnt++;
    }
  }

  if (npa <= p_E * cnt) {
    return 2;
  }

  return 1;
}



int e_2_i(float p_I, float npa, int t_I, int t){
  if (t_I <= t && npa <= p_I) return 3;
  return 2;
}


int i_2qr(float p_Q, float p_R, float npa, int t_Q, int t_R, int t){

  if (t_Q <= t && npa <= p_Q) return 4;

  if (t_R <= t && npa > p_Q && npa <= p_Q + p_R) return 5;

  return 3;

}

int q_2_r(float p_R, float npa, int t_R, int  t){
  if (t_R <= t && npa <= p_R) return 5;

  return 4;
}



// la función requiere de que ingrese un vector de habitantes, al
// menos la inicialización
vector<vector<int>> f_initPop(int sz_r, int sz_c, float D, vector<vector<int>> &habs){

  // inicialización del array de la población
  vector<vector<int>> arr_population (sz_r, vector<int> (sz_c));

  //
  int t_pop = (int)(D * sz_r * sz_c );

  // requerimos un vector con la posición de las personas (hay t_pop personas)
  vector<vector<int>> lst (sz_r * sz_c, vector<int> (2));


  // generando las posiciones de los habitantes
  for (int i = 0; i < sz_r * sz_c ; i++){
    lst[i] = {(int) (i / sz_c) , i % sz_c };
  }

  // tomando un cierto número de esos habitantes
  sample(lst.begin(), lst.end(), back_inserter(habs),
        t_pop, mt19937{random_device{}()});

  // a los habitantes les asignamos el valor de 1
  for (vector<int> hb : habs){
    arr_population[hb[0]][hb[1]] = 1;
  }

  return arr_population;
}



int f_evolution(int sz_r, int sz_c, unordered_map<string, float> &d_params,
                vector<vector<int>> &arr_tiempo,
                vector<vector<int>> arr_population
                //,vector<vector<int>> arr_evo
              ){
  d_params["t"] += 1;

  vector<int> cnt (6);

  unordered_map<int, vector<vector<int>>> d_changes;

  int d;
  int nv;
  float npa;

  vector<vector<int>> ng;

  cout << "--- Empezando la iteración sobre el espacio\n";
  for (int i = 0; i < sz_r; i++){
    for (int j = 0; j< sz_c; j++){
      cout << "row   " << i << "\t\tcol   " << j << "\n";

      npa = distribution(generator);
      if (arr_population[i][j] == 1)  {
        if (d_params["t"] <= d_params["t_L"]) d = d_params["t_L"];
        else d = 1;

        ng = f_getNeigh(sz_r, sz_c, i, j, d, ng);

        nv = s_2_e(d_params["p_E"], npa, ng, arr_population);

        ng.clear();

        if (nv == 2){
          cnt[0]++;
          d_changes[nv].push_back({i,j});
        }
      }


      else if (arr_population[i][j] == 2) {
        cnt[2]++;
        nv = e_2_i(d_params["p_I"], npa, d_params["t_I"], arr_tiempo[i][j]);

        if (nv != 2) d_changes[nv].push_back({i,j});
        else arr_tiempo[i][j]++;
      }


      else if (arr_population[i][j] == 3){
        nv = i_2qr(d_params["p_Q"], d_params["p_R"] , npa, d_params["t_Q"], d_params["t_R"] , arr_tiempo[i][j]);

        if (nv != 3) d_changes[nv].push_back({i,j});
        else arr_tiempo[i][j]++;

      }

      else if (arr_population[i][j] == 4){
        nv = q_2_r(d_params["p_R"], npa, d_params["t_R"], arr_tiempo[i][j]);

        if (nv != 4) d_changes[nv].push_back({i,j});
        else arr_tiempo[i][j]++;
      }


      else {
        nv = arr_population[i][j];
        arr_tiempo[i][j]++;
      }
    }
  }

  for (unordered_map<int,vector<vector<int>>>::iterator it = d_changes.begin(); it != d_changes.end(); it++){

    for(vector<vector<int>>::iterator it_v = (it->second).begin(); it_v != (it->second).end(); it_v++){

      arr_population[(*it_v)[0]][(*it_v)[1]] = it->first;

      arr_tiempo[(*it_v)[0]][(*it_v)[1]] = 0;

    }
  }

  return 0;
}


int data_fig3a(int n_habs, unordered_map<string,vector<float>> &d_cont, vector<vector<int>> arr_population){
  int s = 0, e = 0, i= 0, q = 0, r = 0;
  for (vector<int> rw : arr_population){
    for (int val : rw){
      switch(val){
        case 1:
          s++;
          continue;

        case 2:
          e++;
          continue;

        case 3:
          i++;
          continue;

        case 4:
          q++;
          continue;

        case 5:
          r++;
          continue;

        default:
          continue;
      }


    }
  }

  d_cont["s"].push_back(s / n_habs);
  d_cont["e"].push_back(e / n_habs);
  d_cont["i"].push_back(i / n_habs);
  d_cont["q"].push_back(q / n_habs);
  d_cont["r"].push_back(r / n_habs);

  return 0;
}



int main(){
  int sz_r = 400, sz_c = 400;
  float D = 0.46;
  int d = 2;
  int n_cycles = 10;

  float p_E = 0.5;
  float p_I = 0.5;
  int t_I = 8;
  float p_Q = 0.1;
  int t_Q = 2;
  float p_R = 0.12;
  int t_L = 1000;
  int t_R = 18;

  unordered_map<string, float> d_params ({
    {"p_E", p_E},
    {"p_I", p_I},
    {"p_Q", p_Q},
    {"p_R", p_R},
    {"t_I", (float)t_I},
    {"t_Q", (float)t_Q},
    {"t_L", (float)t_L},
    {"t_R", (float)t_R},
    {"t", 0},
    {"d", (float)d}
  });

  int I_int = 6, E_int = 200;
  vector<vector<int>> habs;

  vector<vector<int>> arr_population = f_initPop(sz_r, sz_c, D, habs);

  vector<vector<int>> arr_tiempo (sz_r, vector<int> (sz_c));

  int n_habs = habs.size();

  // requerimos tomar I_int + E_int elementos de habs, ya están en sample
  for (int k = 0; k < I_int + E_int; k++){
    if (k < I_int) arr_population[habs[k][0]][habs[k][1]] = 3;
    else arr_population[habs[k][0]][habs[k][1]] = 2;
  }

  unordered_map<string,vector<float>> d_cont ({
    {"s", {(n_habs - I_int - E_int)/((float) n_habs)}},
    {"e", {E_int / (float) n_habs}},
    {"i", {I_int / (float) n_habs}},
    {"q", {0}},
    {"r", {0}}
  });

  for (int c = 0; c < n_cycles; c++){
    cout << "Ciclo:\t" << c << "\n";
    f_evolution(sz_r, sz_c,
                d_params,
                arr_tiempo,
                arr_population);
    cout << "--- luego de evo\n";
    data_fig3a(n_habs, d_cont, arr_population);
    cout << "--- luego de datitos uwu\n";
  }




  return 0;
}
