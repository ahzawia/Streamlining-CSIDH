
import copy 
from config import p_list, batch_length, batchbound, batchsize, batchstart, batchstop

from enum import Enum, auto


# State and OperationMode are to be removed
class OperationState(Enum):
    S0 = auto() # no point to be sampled in the inner loop
    S1 = auto() # new point sampling state
    S2 = auto()
    S3 = auto() # old action state
    S4 = auto() # terminating state

# 
# The `OperationMode` class is not fully implemented; however, it provides sufficient functionality for our current needs.
class OperationMode:
    def __init__(self, init_state:OperationState, start=-1, end=-1, min_bound=-1):
        self.state = init_state
        self.prev_state = None

        # related to State.S0
        self.start = start #'S0'
        self.end = end #'S0'
        self.min_bound = min_bound  + 1 #'S0'
        self.rbatchbound = copy.deepcopy(batchbound)

        # mainly for random coin
        self.r_coin_list = []
        self.current_r_coin = None
        self.next_r_coin = None

        # mainly for S1 and S0 evaluation
        self.batch_i_previous = None
 

    def update_current_r_coin(self):
        r_coin = self.current_r_coin
        self.current_r_coin = copy.deepcopy(self.next_r_coin)
        self.next_r_coin = None
        return r_coin

    def set_current_r_coin(self, clib, itr, batch_i, targets, Js):
        if self.state == OperationState.S0:
            self.current_r_coin = 1
            self.next_r_coin = 1
        else:
            if  batch_i == targets[0]:
                batch_i_current = batch_i
                jx_current = Js[batch_i_current][0]
                pos_li_x_current = batchstart[batch_i_current] if jx_current == -1 else batchstart[batch_i_current] + jx_current 
                self.current_r_coin = clib.random_coin(pos_li_x_current, batch_i_current)
            if  batch_i != targets[-1]:
                batch_i_next = targets[itr+1]
                jx_next = Js[batch_i_next][0]
                pos_li_x_next = batchstart[batch_i_next] if jx_next == -1 else batchstart[batch_i_next] + jx_next 
                self.next_r_coin = clib.random_coin(pos_li_x_next, batch_i_next)   

    def update(self):
        if self.state == OperationState.S0:
            self.state = OperationState.S1
        elif self.state != OperationState.S1:
            raise NotImplementedError(f"State {self.state} transition not implemented")
        
        return self.state

    
    def handle_invalid_input(self, C):
        if self.state == OperationState.S0:
            return self.state_S0_invalid(C)
        elif self.state == OperationState.S1:
            return self.state_S1_invalid(C)
        elif self.state == OperationState.S2:
            return self.state_S2_invalid(C)
    
    def state_S0_invalid(self, C):
        # Implement the logic to handle invalid input for state S0
        pass
    
    def state_S1_invalid(self, C):
        # Implement the logic to handle invalid input for state S1
        pass
    
    def state_S2_invalid(self, C):
        # Implement the logic to handle invalid input for state S2
        pass

abs_min_with_sign = lambda a, b: min(a, abs(b)) * (1 if b >= 0 else -1)

def compute_ri_rj_qij(ei, ej, I_qij, bound, J_qij):
    e_comm1 = [0] * len(ei) 
    e_comm2 = [0] * len(ej) 

    for i in range(batch_length):
        if I_qij[i] == 1:
            jx = J_qij[i]
            for j in range(batchsize[i]):
                pos_li = batchstart[i] + j
                if jx == j :
                    e_comm1[pos_li] = abs_min_with_sign(bound, ei[pos_li]) 
                    ei[pos_li] =  ei[pos_li] - e_comm1[pos_li]

                    e_comm2[pos_li] = abs_min_with_sign(bound, ej[pos_li]) 
                    ej[pos_li] =  ej[pos_li] - e_comm2[pos_li]

    if e_comm1 != e_comm2:
        raise Exception("e_comm_ij_1 != e_comm_ij_2")
    
    return ei, ej, e_comm2

# #########################################
# General functions 
# ######################################### 
#  
def get_pos_li(i, j):
    # inputs 
    # i is the batch index
    # j is the index within the batch j can be -1 or \in \Z
    return batchstart[i] if j == -1 else batchstart[i] + j 

def sign_encoded(e_i_j):
    if e_i_j > 0:
        return  1
    elif e_i_j < 0:
        return -1
    else:
        return  0

def get_e_i_j_sign(e, i, j):
    e_i_j = e[get_pos_li(i, j)] 
    return sign_encoded(e_i_j)

def find_random_j(e, i):
    # TODO
    raise Exception("find_random_j is not implemented") 

# TODO replace with find_random_j
def find_first_nonzero_j(e, i):
    # Not secure
    for j in range(batchsize[i]):
        sign = get_e_i_j_sign(e, i, j)
        if sign != 0:
            return j, sign  # Return the index of the first nonzero element
    # return -1, sign # Return -1 if all elements are zero
    return 0, sign # Return -1 if all elements are zero

def index_of_largest_abs_value(e, i):
    e_i = e[batchstart[i]: batchstop[i]]

    if not e_i:
        return -1  # Return -1 if the list is empty
    
    # Initialize the index of the largest absolute value
    index_of_max = 0
    
    # Iterate over the list starting from the first index
    for j in range(1, len(e_i)):
        # Compare the absolute values of elements
        if abs(e_i[j]) > abs(e_i[index_of_max]):
            index_of_max = j

    return index_of_max, get_e_i_j_sign(e, i, index_of_max)

def select_torsion_point_index_Ts(epsilon):
    return 1 if epsilon == -1 else 0


def cmov(A, B, condition):
    selection = int(condition)
    return (B, A)[selection]

def cswap(A, B, condition):
    if condition:
        return B, A
    else:
        return A, B

def int_cswap(x, y, cond):
    # Convert condition to 0 or 1, assuming cond is either 0 (false) or 1 (true)
    masked_cond = cond & 1
    
    # perform swapping
    # If masked_cond is 1, swap occurs. If 0, no swap.
    dummy = masked_cond * (x - y)
    x_new = x - dummy
    y_new = y + dummy
    return (x_new, y_new)

def cprint(message, flg=False):
    if flg:
        print(message)