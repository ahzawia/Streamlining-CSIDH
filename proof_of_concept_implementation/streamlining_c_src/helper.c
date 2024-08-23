#include "helper.h"
#include <stdio.h>
#include "externalfun.h"


// // // // // // // // // // 
// for benchmarking TODO maybe remove to better place
void reset_counters() {
    fp_mulsq_count = fp_sq_count = fp_addsub_count = 0;
}

void get_counters(long long *in_fp_mulsq_count, long long * in_fp_sq_count, long long *in_fp_addsub_count){
    *in_fp_mulsq_count = fp_mulsq_count;
    *in_fp_sq_count = fp_sq_count;
    *in_fp_addsub_count = fp_addsub_count;
}


// // // // // // // // // // 
// aux functions
// Helper function to get bit value from processState
int get_bit(unsigned int value, int position) {
    return (value >> position) & 1;
}
// Function to calculate the maximum of two int8_t values
int8_t min(int8_t x, int8_t y) {
    return x < y ? x : y;
}
// Function to calculate the maximum of two int8_t values
int8_t max(int8_t x, int8_t y) {
    return x > y ? x : y;
}
// Function to dynamically allocate an array of private_key with the specified size
private_key* create_private_key_array(int size) {
    return (private_key*)malloc(size * sizeof(private_key));
}
