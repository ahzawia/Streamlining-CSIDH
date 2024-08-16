#ifndef EXTERNALFUN_H
#define EXTERNALFUN_H

#define FIXED_PREFIX highctidh

#define PREFIX highctidh_512


#define CONCATENATE(prefix, name) prefix##name
#define MAKE_NAME(prefix, name) CONCATENATE(prefix, name)

// Aliases for variables
#define primes MAKE_NAME(PREFIX, _primes)
#define primes_dac MAKE_NAME(PREFIX, _primes_dac)
#define primes_daclen MAKE_NAME(PREFIX, _primes_daclen)
#define primes_batchmaxdaclen MAKE_NAME(PREFIX, _primes_batchmaxdaclen)

#define uintbig_1 MAKE_NAME(PREFIX, _uintbig_1)
#define fp_0 MAKE_NAME(PREFIX, _fp_0)
#define fp_1 MAKE_NAME(PREFIX, _fp_1)
#define fp_2 MAKE_NAME(PREFIX, _fp_2)
#define fp_mulsq_count MAKE_NAME(PREFIX, _fp_mulsq_count)
#define fp_sq_count MAKE_NAME(PREFIX, _fp_sq_count)
#define fp_addsub_count MAKE_NAME(PREFIX, _fp_addsub_count)

// Aliases for functions
#define fp_cswap MAKE_NAME(PREFIX, _fp_cswap)
#define fp_inv MAKE_NAME(PREFIX, _fp_inv)
#define fp_mul2 MAKE_NAME(PREFIX, _fp_mul2)

#define uintbig_set MAKE_NAME(PREFIX, _uintbig_set)
#define uintbig_mul3_64 MAKE_NAME(PREFIX, _uintbig_mul3_64)

#define xMUL_dac MAKE_NAME(PREFIX, _xMUL_dac)
#define xMUL MAKE_NAME(PREFIX, _xMUL)
#define xMUL_vartime MAKE_NAME(PREFIX, _xMUL_vartime)


// Aliases for random functions
#define random_coin MAKE_NAME(FIXED_PREFIX, _random_coin)

// Aliases for elliptic curve functions
#define xA24 MAKE_NAME(PREFIX, _xA24)
#define validate MAKE_NAME(PREFIX, _validate)

// Aliases for point sampling and operation
#define elligator MAKE_NAME(PREFIX, _elligator)
#define xDBL MAKE_NAME(PREFIX, _xDBL)

// Aliases for isogeny evaluation
#define csidh_private MAKE_NAME(PREFIX, _csidh_private)
#define xISOG MAKE_NAME(PREFIX, _xISOG)
#define xISOG_matryoshka MAKE_NAME(PREFIX, _xISOG_matryoshka)

// Aliases for actions
// #define action_old MAKE_NAME(PREFIX, _action_old)
#define action MAKE_NAME(PREFIX, _action)


#include <stdio.h>
#include "models.h"
#include <stdbool.h>  // for boolean type

// // // // // // // // // 
// related to p's  
#define primes_num 74
extern const long long primes[primes_num];
extern const long long primes_dac[primes_num];
extern const long long primes_daclen[primes_num];

#define primes_batches 14
extern const long long primes_batchmaxdaclen[primes_batches];

// // // // // // // // // 
// related to fp operations and constants
extern const uintbig uintbig_1;

extern const fp fp_0;
extern const fp fp_1;
extern const fp fp_2;

extern long long fp_mulsq_count;
extern long long fp_sq_count;
extern long long fp_addsub_count;

// // // // // // // // // 
//  Fp functions
extern void fp_cswap(fp *x, fp *y, long long c); /* c is 0 or 1 */
extern void fp_inv(fp *x);
extern void fp_mul2(fp *x, fp const *y);

// // // // // // // // // 
// implemintation for static and inline functions

static inline long long uintbig_uint64_iszero(uint64_t t)
{
  // is t nonzero?
  t |= t>>32;
  // are bottom 32 bits of t nonzero?
  t &= 0xffffffff;
  // is t nonzero? between 0 and 0xffffffff
  t = -t;
  // is t nonzero? 0, or between 2^64-0xffffffff and 2^64-1
  t >>= 63;
  return 1-(long long) t;
}

static inline long long uintbig_iszero(const uintbig *x)
{
  uint64_t t = 0;
  for (long long i = 0;i < UINTBIG_LIMBS;++i)
    t |= x->c[i];
  return uintbig_uint64_iszero(t);
}

static inline long long fp_iszero(const fp *x)
{
  return uintbig_iszero(&x->x);
}

// extern void fp_random_wrapper(fp *x);
// // // // // // // // // 
 

// // // // // // // // // 
//   Random function
extern int64_t random_coin(uint64_t num,uint64_t den);

// // // // // // // // // 
// multiplication
// multiplication of uintbig 
extern void uintbig_set(uintbig *x, uint64_t y);
extern void uintbig_mul3_64(uintbig *x, uintbig const *y, uint64_t z);

// multiplication of points
extern void xMUL_dac(proj *Q, proj const *A24, int Aaffine, proj const *P, long long dac, long long daclen, long long maxdaclen);
extern void xMUL(proj *Q, proj const *A, int Aaffine, proj const *P, uintbig const *k, long long kbits);
extern void xMUL_vartime(proj *Q, proj const *A, int Aaffine, proj const *P, uintbig const *k);
// // // // // // // // // 


// // // // // // // // // 
// proj functions
static inline void proj_cswap(proj *P, proj *Q, long long c)
{
  fp_cswap(&P->x,&Q->x,c);
  fp_cswap(&P->z,&Q->z,c);
}

static inline void proj_cmov(proj *P, const proj *Q, long long c)
{
  fp_cmov(&P->x,&Q->x,c);
  fp_cmov(&P->z,&Q->z,c);
}

// // // // // // // // // 
// Elliptic curve functions
// precompute A24.x = A.x+2*A.z, A24.z = 4*A.z
extern void xA24(proj *A24, const proj *A);
//  validate a curve
extern bool validate(public_key const *in);

// point sampling and operation
extern void elligator(proj *plus,proj *minus,const proj *A);
extern void xDBL(proj *Q, proj const *P, const proj *A24, int Aaffine);

// isogeny evalaution
extern void csidh_private(private_key *priv);
void xISOG(proj *A, proj *P, long long Plen, proj const *K, long long k);
extern void xISOG_matryoshka(proj *A, proj *P, long long Plen, proj const *K, long long k, long long klower, long long kupper);


/* totally not constant-time. */
// extern void action_old(public_key *out, public_key const *in, private_key const *priv);
/* goal: constant time */
extern void action(public_key *out, public_key const *in, private_key const *priv);

#endif