#ifndef MODELS_H
#define MODELS_H

#include <stdint.h>

#define BITS 512
#define UINTBIG_LIMBS ((BITS+63)/64) // You must define this based on the shared library's specification
#define primes_num 74 // Define this based on your requirements

typedef struct uintbig {
    uint64_t c[UINTBIG_LIMBS];
} uintbig;

typedef struct fp {
    uintbig x;
} fp;


typedef struct proj {
    fp x;
    fp z;
} proj;

typedef struct private_key {
    int8_t e[primes_num];
} private_key;

typedef struct public_key {
    fp A; /* Montgomery coefficient: represents y^2 = x^3 + Ax^2 + x */
} public_key;


#endif
