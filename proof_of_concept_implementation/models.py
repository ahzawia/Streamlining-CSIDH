from ctypes import Structure, c_int8, c_uint64
from config import BITS, UINTBIG_LIMBS, prime_p, primes_num
from helper import out_of_montgomery_num, to_of_montgomery_num 

class uintbig(Structure):
    _fields_ = [("c", c_uint64 * UINTBIG_LIMBS)]

    def print(self, name=''):
        if name!='': 
            print(name,": ", end="")
        for i in range(len(self.c)-1, -1,-1):
            print(f"{self.c[i]}", end="")  # I have removed the space between them
        if name!='': 
            print("\n")
            
    def to_integer(self):
        value = 0
        for i in range(UINTBIG_LIMBS):
            # Each limb's value is shifted left by 64 bits times its position
            value += self.c[i] * (2 ** (64 * i))
        return value

    def to_uintbig(self, value):
        u = uintbig()
        for i in range(UINTBIG_LIMBS):
            # Extract the 64-bit segment of the value for this limb
            u.c[i] = (value >> (64 * i)) & 0xFFFFFFFFFFFFFFFF
        return u
    
    def set_from_large_integer(self, value):
        for i in range(UINTBIG_LIMBS):
            # Extract the 64-bit segment of the value for this limb
            self.c[i] = (value >> (64 * i)) & 0xFFFFFFFFFFFFFFFF

    def print_as_integer(self, name=''):
        value_montgomery = self.to_integer()
        
        R = 1 << BITS
        value = out_of_montgomery_num(value_montgomery, prime_p, R)

        if name!='': 
            print(name,": ", end="")

        print(value, end="")

        if name!='': 
            print()
            
class fp(Structure):
    _fields_ = [("x", uintbig)]

    def set_from_large_integer(self, value):
        R = 1 << BITS
        montgomery_value = to_of_montgomery_num(value, prime_p, R)
        self.x.set_from_large_integer(montgomery_value)
    
    def get_as_large_integer(self):
        large_integer_montgomery = self.x.to_integer()
        R = 1 << BITS
        large_integer = out_of_montgomery_num(large_integer_montgomery, prime_p, R)
        return large_integer

    def print(self):
        # self.x.print()
        self.x.print_as_integer()

    def __eq__(self, other):
        if isinstance(other, fp):
            return self.get_as_large_integer() == other.get_as_large_integer()
        return NotImplemented

class proj(Structure):
    _fields_ = [("x", fp), ("z", fp)]

    def print(self, name="proj"):
        print(name , ": {", end = "")
        print("x: ", end = "")
        self.x.print()
        print(", ", end = "")
        print("z: ", end = "")
        self.z.print()
        # print("}", end = "")
        print("}")

class private_key(Structure):  
    _fields_ = [("e", c_int8 * primes_num)]

    def __setitem__(self, index, value):
        if isinstance(index, slice):
            # Handling slicing
            start, stop, step = index.indices(len(self.e))
            # Check if 'value' is a list and has the right size
            if isinstance(value, (list, tuple)) and len(value) == (stop - start):
                for i, val in enumerate(value):
                    self.e[start + i] = val
            else:
                raise ValueError("private_key: Value must be a list or tuple with the correct number of elements")
        elif isinstance(index, int):
            # Handling single index
            if 0 <= index < len(self.e):
                self.e[index] = value
            else:
                raise IndexError("private_key: Index out of range")
        else:
            raise TypeError("private_key: Index must be an int or slice")

    def __getitem__(self, index):
        if isinstance(index, slice):
            # Handling slicing
            start, stop, step = index.indices(len(self.e))
            return [self.e[i] for i in range(start, stop, step)]
        elif isinstance(index, int):
            # Handling single index
            if 0 <= index < len(self.e):
                return self.e[index]
            else:
                raise IndexError("private_key: Index out of range")
        else:
            raise TypeError("private_key: Index must be an int or slice")
        
    def __str__(self):
        return f"[{', '.join(str(self.e[i]) for i in range(len(self.e)))}]"

    def __repr__(self):
        return f"private_key({[self.e[i] for i in range(len(self.e))]})"

    @classmethod
    def from_int_list(cls, int_list):
        if len(int_list) != primes_num:
            raise ValueError(f"List must contain exactly {primes_num} integers.")
        # Create an instance of ptest
        instance = cls()
        # Copy elements from the list to the ctypes array
        for i in range(primes_num):
            instance.e[i] = int_list[i]
        return instance
    
    def to_list(self): 
        return [self.e[i] for i in range(len(self.e)) ] 

    def is_zero(self):
        """Check if all elements in the ctypes list are zero."""
        return all(x == 0 for x in self.e)

    def get_weight(self):
        return sum(abs(x) for x in self.e)
    
class public_key(Structure):
    _fields_ = [("A", fp) ]

    def print(self, name="public_key"):
        print(name , ": ", end = "")
        self.A.print()
        print("}")
    
    def __eq__(self, other):
        if isinstance(other, public_key):
            return self.A == other.A
        return False




