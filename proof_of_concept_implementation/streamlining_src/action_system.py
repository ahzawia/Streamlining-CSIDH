from config import n_primes, batchsize, batchstart 
from streamlining_src.models import private_key

def compute_action_difficult(sk, in_size):
    sum_t = 0
    for idx in range(in_size):
        sum_t = sum_t + abs(sk[idx])
    return sum_t

def return_batch_start_end_indices(batch_number):
    batch_start_idx = batchstart[batch_number]
    batch_end_idx = batch_start_idx + batchsize[batch_number]
    return batch_start_idx, batch_end_idx

# ###########################################
# The first strategy includes helpers, though most are implemented for demonstration purposes only.
# ###########################################

# Those functions (sign) are used to clearly map out the paper and are intended solely for illustration.
def sign(x):
    if x > 0:
        return 1
    elif x < 0:
        return -1
    return 0

# This can be implemented much better, but for the sake of time, it will do.
def identify_action_systems_for_public_strategy(execution_set, n=n_primes):
    # execution set size
    c = len(execution_set) 

    if c < 2:
        # If there are fewer than two executions, return an empty action system
        return []

    # This function works with public set, so no security restriction
    used_action = [False] * c

    # output action system, i.e., pair of actions
    action_systems = []

    # Iterate over all actions in the execution set.
    for i in range(c):
        # Skip if this action has already been paired
        if used_action[i]:
            continue

        best_j = None
        M = -1 # distance metric M
        for j in range(i + 1, c):
            # Skip if this action has already been paired
            if used_action[j]:
                continue 
            # Initialize match score for the current pair (i, j)
            M_ij = 0 
            # calculate match score (M_ij)
            for idx in range(n):
                e_i_idx = execution_set[i][idx]
                e_j_idx = execution_set[j][idx]
                M_ij += int(sign(e_i_idx) != 0 and sign(e_i_idx) == sign(e_j_idx))
            
            # Update the best match if the current pair has a higher score
            if M_ij > M:
                M = M_ij
                best_j = j
        
        if best_j is not None:
            action_systems.append((i, best_j, M))
            used_action[i] = True
            used_action[best_j] = True
    
    return action_systems

# This can be implemented much better, but for the sake of time, it will do.
def get_qij_from_action_pair(e_i, e_j):
    q_ij, r_i, r_j = [], [], []
    for v1, v2 in zip(e_i, e_j):
        if v1 * v2 > 0:  # Check if both numbers have the same sign
            q = sign(v1) * min(abs(v1), abs(v2))
        else:
            q = 0
        q_ij.append(q)
        r_i.append(v1 - q)
        r_j.append(v2 - q)

    return q_ij, r_i, r_j

# This can be implemented much better, but for the sake of time, it will do.
def pinpoint_action_systems(execution_set):
    action_systems = identify_action_systems_for_public_strategy(execution_set)
    action_systems_q_ri_rj = []
    priv = private_key() 
    for pair in action_systems:
        q_ij, r_i, r_j = get_qij_from_action_pair(execution_set[pair[0]], execution_set[pair[1]])
        action_systems_q_ri_rj.append(priv.from_int_list(q_ij))
        action_systems_q_ri_rj.append(priv.from_int_list(r_i))
        action_systems_q_ri_rj.append(priv.from_int_list(r_j))
    return action_systems_q_ri_rj

# ###########################################
# The second strategy includes helpers, though most are implemented for demonstration purposes only.
# ###########################################

# This can be implemented much better, but for the sake of time, it will do.
def identify_action_systems_for_private_strategy(execution_set, start, end, min_bound):
    n = len(execution_set)
    action_systems = {}
    used = [False] * n  # Track which vectors have been used
    for i in range(n):
        for j in range(i + 1, n):
            if not used[i] and not used[j]:
                match_result, matched_indices = check_sign_matching(execution_set[i], execution_set[j], start, end, min_bound)
                if match_result:
                    action_systems[(i, j)] = matched_indices
                    used[i] = True
                    used[j] = True
                    break  # Move to the next vector i

    return action_systems

# Not constant time
# This can be implemented much better, but for the sake of time, it will do.
def check_sign_matching(e_i, e_j, starting_batch, ending_batch, min_bound):
    # matched_indices = {starting_batch-1: j, starting_batch+1: j, ending_batch+1: j} 
    matched_indices = dict() #{} 
    for batch_number in range(starting_batch - 1, ending_batch + 1):
        batch_start_idx, batch_end_idx = return_batch_start_end_indices(batch_number)
        found_match = False
        for k in range(batch_start_idx, batch_end_idx):
            if (e_i[k] * e_j[k] > 0 and min(abs(e_i[k]), abs(e_j[k])) > min_bound):  # same sign
                matched_indices[batch_number] = k - batch_start_idx
                found_match = True
                break
        if not found_match:
            return False, {}
    return True, matched_indices