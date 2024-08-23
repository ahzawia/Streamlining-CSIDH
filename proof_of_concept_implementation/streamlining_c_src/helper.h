#ifndef HELPER_H
#define HELPER_H

#include <stdint.h>
#include <stdlib.h>
#include "models.h"

// // // // // // // // // // 
// for benchmarking TODO maybe remove to better place
void reset_counters();

void get_counters(long long *in_fp_mulsq_count, long long * in_fp_sq_count, long long *in_fp_addsub_count);

// // // // // // // // // // 
// Function to calculate the minimumand  maximum of two int8_t values
int get_bit(unsigned int value, int position);
int8_t min(int8_t x, int8_t y);
int8_t max(int8_t x, int8_t y);
private_key* create_private_key_array(int size);


#endif // HELPER_H