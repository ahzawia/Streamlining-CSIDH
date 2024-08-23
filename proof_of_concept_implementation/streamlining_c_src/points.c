#include "points.h"
#include "externalfun.h"

#include <assert.h> // TODO for assersion 


void xMUL_pos(proj *T, proj const *A24, int Aaffine, int pos_li) {
    long long dac = primes_dac[pos_li];  //dac_list[pos_li]; 
    int daclen = primes_daclen[pos_li]; //daclen_list[pos_li];  
    int maxdaclen = daclen;
    xMUL_dac(T, A24, Aaffine, T, dac, daclen, maxdaclen);
}

// const
void xMUL_pos_const(proj *T, proj const *A24, int Aaffine, int pos_li, int pos_batch) {
    long long dac = primes_dac[pos_li];  //dac_list[pos_li]; 
    int daclen = primes_daclen[pos_li]; //daclen_list[pos_li];  
    int maxdaclen = primes_batchmaxdaclen[pos_batch]; // daclen;
    xMUL_dac(T, A24, Aaffine, T, dac, daclen, maxdaclen);
}

bool is_at_infinity(proj *Q) {
    // proj T = *Q;
    // unsigned int b1 = fp_iszero(&Q->z) ? true : false;
    return fp_iszero(&Q->z) ? true : false;
}

void clear_power_two(proj *T, proj const *A24, int Aaffine) {
    // clear powers of 2
    xDBL(T, T, A24, Aaffine);
    xDBL(T, T, A24, Aaffine);
}
