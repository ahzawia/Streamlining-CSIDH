
# ###########################################
# General functions
# ###########################################

add_fun = lambda x, y: x + y

percentage_fun = lambda x, y: 100 * (1 - x / y)

def mean_fun(list_of_int, n):
    if n == 0:
        raise ValueError("Division by zero is not allowed.")
    
    the_mean = [num / n for num in list_of_int]
    return the_mean

def sum_pair_wise_vectors_of_vector(vect):
    """ returns SUM_i( SUM_j(V_ij)) """
    # Check if V1 is empty or has only one list
    if len(vect) < 2:
        return vect[0]

    output_sum = vect[0]
    # Iterate through V1 in steps of 2
    for i in range(1, len(vect), 1):
        output_sum = list(map(add_fun, output_sum, vect[i]))

    return output_sum

# ###########################################
# 
# ###########################################

def egcd(a, b):
    """Extended Euclidean Algorithm"""
    if a == 0:
        return (b, 0, 1)
    else:
        g, y, x = egcd(b % a, a)
        return (g, x - (b // a) * y, y)

def modinv(a, m):
    """Compute the modular inverse of a modulo m"""
    g, x, y = egcd(a, m)
    if g != 1:
        raise Exception('Modular inverse does not exist')
    else:
        return x % m
    
def to_of_montgomery_num(num, N, R):
    """Compute num from montgomery_num in the Montgomery domain"""
    montgomery_num = (num * R) % N
    return montgomery_num

def out_of_montgomery_num(montgomery_num, N, R):
    """Compute num from montgomery_num in the Montgomery domain"""
    R_inv = modinv(R, N)  # Compute the modular inverse of R modulo N
    num = (montgomery_num * R_inv) % N  # Transform back to the standard representation
    return num


# ###########################################
# For read and write from/to files
# ###########################################
import json

def load_config(config_path):
    """
    Load a configuration file to a text file in JSON format.

    Args:
    config_path (str): The configuration directory+name to be loaded.
    """
    with open(config_path, 'r') as file:
        return json.load(file)
    
from datetime import datetime
def save_dict_to_file(dictionary, file_name):
    """
    Saves a dictionary to a text file in JSON format.

    Args:
    dictionary (dict): The dictionary to save.
    file_name (str): The name of the file to save the dictionary to.
    """
    with open(file_name, 'w') as file:
        json.dump(dictionary, file)