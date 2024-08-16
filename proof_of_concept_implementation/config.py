from functools import reduce

# Assuming a definition for UINTBIG_LIMBS, for example:
BITS = 512
UINTBIG_LIMBS = ((BITS+63)//64)

# the number of primes in p
p_list = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317, 331, 337, 347, 349, 353, 359, 367, 373, 587]
primes_num  =  len(p_list) #74
prime_p = 4 * reduce(lambda x, y: x * y, p_list)- 1

batchbound = [10, 14, 16, 17, 17, 17, 18, 18, 18, 18, 18, 13, 13, 1]
batchsize = [2, 3, 4, 4, 5, 5, 6, 7, 7, 8, 8, 6, 8, 1]
batchstart = [0, 2, 5, 9, 13, 18, 23, 29, 36, 43, 51, 59, 65, 73]
batchstop = [2, 5, 9, 13, 18, 23, 29, 36, 43, 51, 59, 65, 73, 74]
batch_length = len(batchsize)
