
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


# Save to files
import json
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


def save_dict_to_file_type(dictionary, file_name, out_type):
    """
    Saves a dictionary to a text file in JSON format.

    Args:
    dictionary (dict): The dictionary to save.
    file_name (str): The name of the file to save the dictionary to.
    """

    # Get the current date and time
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Add the current time to the file name
    file_name_with_time = f"{file_name}_{current_time}.{out_type}"


    with open(file_name_with_time, 'w') as file:
        json.dump(dictionary, file)