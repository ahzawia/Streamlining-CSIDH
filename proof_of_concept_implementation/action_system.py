from config import batchsize, batchstart 
from models import private_key

add_fun = lambda x, y: x + y

percentage_fun = lambda x, y: 100 * (1 - x / y)

def mean_fun(list_of_int, n):
    if n == 0:
        raise ValueError("Division by zero is not allowed.")
    
    the_mean = [num / n for num in list_of_int]
    return the_mean

def compute_action_difficult(sk, in_size):
    sum_t = 0
    for idx in range(in_size):
        sum_t = sum_t + abs(sk.e[idx])
    return sum_t

# ###########################################
# The first strategy includes helpers, though most are implemented for demonstration purposes only.
# TODO
# ###########################################

def sum_pair_wise_vectors_of_vector(V1):
    # Check if V1 is empty or has only one list
    if len(V1) < 2:
        return V1[0]

    result = V1[0]
    # Iterate through V1 in steps of 2
    for i in range(1, len(V1), 1):
        result = list(map(add_fun, result, V1[i]))

    return result

# This can be implemented much better, but for the sake of time, it will do.
def find_pairs_strategic_one(vectors):
    n = len(vectors)
    used = [False] * n
    pairs = []

    # Create index pairs
    for i in range(n):
        if not used[i]:
            best_j = None
            best_match_score = -1
            for j in range(i+1, n):
                if not used[j]:
                    match_score = 0
                    # Calculate match score based on batch definitions
                    for start, size in zip(batchstart, batchsize):
                        segment_i = vectors[i][start:start+size]
                        segment_j = vectors[j][start:start+size]
                        match_score += sum(1 for x, y in zip(segment_i, segment_j) if x*y>0)
                    
                    if match_score > best_match_score:
                        best_match_score = match_score
                        best_j = j
            
            if best_j is not None:
                pairs.append((i, best_j))
                used[i] = True
                used[best_j] = True
    
    return pairs

# This can be implemented much better, but for the sake of time, it will do.
def get_qij_from_vectors(V1, V2):
    def sign(x):
        if x > 0:
            return 1
        elif x < 0:
            return -1
        return 0

    Vq, Vr1, Vr2 = [], [], []
    for v1, v2 in zip(V1, V2):
        if v1 * v2 > 0:  # Check if both numbers have the same sign
            q = sign(v1) * min(abs(v1), abs(v2))
        else:
            q = 0
        Vq.append(q)
        Vr1.append(v1 - q)
        Vr2.append(v2 - q)

    return Vq, Vr1, Vr2

# This can be implemented much better, but for the sake of time, it will do.
def pinpoint_action_systems(vectors):
    pairs = find_pairs_strategic_one(vectors)
    sys_out = []
    priv = private_key() 
    for pair in pairs:
        Vq, Vr1, Vr2 = get_qij_from_vectors(vectors[pair[0]], vectors[pair[1]])
        sys_out.append(priv.from_int_list(Vq))
        sys_out.append(priv.from_int_list(Vr1))
        sys_out.append(priv.from_int_list(Vr2))
    return sys_out

# ###########################################
# The second strategy includes helpers, though most are implemented for demonstration purposes only.
# TODO
# ###########################################

# This can be implemented much better, but for the sake of time, it will do.
def find_pairs_strategic_two(vectors, start, end, min_bound):
    n = len(vectors)
    pairs = {}
    used = [False] * n  # Track which vectors have been used

    for i in range(n):
        for j in range(i + 1, n):
            if not used[i] and not used[j]:
                match_result, matched_indices = check_sign_matching(vectors[i], vectors[j], start, end, min_bound)
                if match_result:
                    pairs[(i, j)] = matched_indices
                    used[i] = True
                    used[j] = True
                    break  # Move to the next vector i

    return pairs

# Not constant time
# This can be implemented much better, but for the sake of time, it will do.
def check_sign_matching(ei, ej, start, end, min_bound):
    matched_indices = dict() #{} 
    for batch_idx in range(start-1, end+1):
        start = batchstart[batch_idx]
        end = start + batchsize[batch_idx]
        found_match = False
        for k in range(start, end):
            if (ei[k] * ej[k] > 0 and min(abs(ei[k]), abs(ej[k])) > min_bound):  # same sign
                matched_indices[batch_idx] = k - start
                found_match = True
                break
        if not found_match:
            return False, {}
    return True, matched_indices