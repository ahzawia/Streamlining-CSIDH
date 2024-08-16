import copy
from action_system import find_pairs_strategic_two
from config import batch_length, batchbound
from models import proj
from c_interface import C_INTERFACE
from new_g_action_aux import NumberExecutionRounds, EpsFdistJs
from new_g_action_helper import OperationMode, OperationState, cmov, cswap
from new_g_action_helper import compute_ri_rj_qij, get_pos_li, select_torsion_point_index_Ts 
from new_g_action_points import Algorithm_5, Algorithm_5_with_pre_sampled_torsion_points, Algorithm_4
from new_g_action_helper import cprint


# Global variables for debugging, TODO remove
main_flg = False
inner_flg = False
torsion_point_flg = False
scale_eval_flg = False

def reset_round_counter():
    return NumberExecutionRounds([])

# TODO public info
round_counter = NumberExecutionRounds()

def system_action(clibx : C_INTERFACE, A, in_e_list, start, end, min_bound):
    # The input (start, end) sets the target batches between "start" and "end+1".
    # The input (min_bound) sets d-common round(s) to be "min_bound+1"

    global round_counter
    round_counter = NumberExecutionRounds([])

    # The below is redundant, remove later
    e_size = len(in_e_list)
    e_list = copy.deepcopy(in_e_list)
    e_list_l = copy.deepcopy(e_list)
    matching_pairs = find_pairs_strategic_two(e_list_l, start, end, min_bound)
   
    A24 = clibx.xA24(A)
    As = [A, A24]
    efj_q_list = []
    I_q = [1 if start-1 <= i <= end else 0 for i in range(batch_length)]
    rq_list    = [[0] for _ in range(e_size//2)]
    r12_list   = [[0] for _ in range(e_size)]

    idx = 0
    for pair, indices in matching_pairs.items():
        i = pair[0]
        j = pair[1]

        Js_joint = [-1 for _ in range(batch_length)]
        for batch_i in indices.keys():
            Js_joint[batch_i] = indices.get(batch_i)

        r12_list[i], r12_list[j], rq_list[idx] = compute_ri_rj_qij(e_list[i], e_list[j], I_q, min_bound + 1, Js_joint)
        
        efj = EpsFdistJs(clibx, rq_list[idx], I_q)
        efj.f_tilde_list = copy.deepcopy(I_q)
        efj_q_list.append(efj)
        idx = idx + 1

    Tp, Tn = clibx.get_pre_sampled_full_torsion_points_for_A0()
    Tpn_p_list = Algorithm_5_with_pre_sampled_torsion_points(clibx, Tp, Tn, e_size//2, As, efj_q_list, flg=False)
 
    A_out = []
    idx = 0
    for pair, indices in matching_pairs.items():
        i = pair[0]
        j = pair[1] 

        As_q = copy.deepcopy(As) 
        mu_x_q = copy.deepcopy(I_q)
        mu_x_r12 = [batchbound[i] - mu_x_q[i] for i in range(batch_length)]
 
        init_state = OperationState.S0
        op_mode =  OperationMode(init_state, start, end, min_bound)
        As_q, rq_list[idx] = constant_time_g_action_system_evaluation(clibx, Tpn_p_list[idx], As_q, rq_list[idx], mu_x_q, op_mode, efj_q_list[idx])
        idx = idx + 1

        op_mode.state = OperationState.S0 
        e_ij_size = 2
        I_r12a = [1 if mu_x_r12_i > 0 else 0 for mu_x_r12_i in mu_x_r12]
        I_r12b = copy.deepcopy(I_r12a)

        efj_r1 = EpsFdistJs(clibx, r12_list[i], I_r12a)
        efj_r2 = EpsFdistJs(clibx, r12_list[j], I_r12b)
        Tpn_list_r12 = Algorithm_5(clibx, e_ij_size, As_q,  list([efj_r1, efj_r2]), flg=False)
    
        mu_x_i = copy.deepcopy(mu_x_r12)
        As_r1, r12_list[i] = constant_time_g_action_system_evaluation(clibx, Tpn_list_r12[0], As_q, r12_list[i], mu_x_i, op_mode, efj_r1) 
        A_out.append(copy.deepcopy(As_r1[0]))

        op_mode.state = OperationState.S0
        mu_x_j = copy.deepcopy(mu_x_r12)
        As_r2, r12_list[j] = constant_time_g_action_system_evaluation(clibx, Tpn_list_r12[1], As_q, r12_list[j] , mu_x_j, op_mode, efj_r2)        
        A_out.append(copy.deepcopy(As_r2[0]))

    for A_idx in range(len(A_out)):
        A_out[A_idx] = clibx.to_public_key(A_out[A_idx])

    return A_out, copy.deepcopy(round_counter)

def constant_time_g_action_system_evaluation(clibx : C_INTERFACE, Tpn, input_AA24, e, input_mu_list, op_mode:OperationMode, input_efj:EpsFdistJs):

    AA24 = copy.deepcopy(input_AA24)

    if op_mode.state == OperationState.S0:
        mu_list = input_mu_list
    else:
        mu_list = [copy.deepcopy(batchbound[B_i]) for B_i in range(len(batchbound))]
    
    global round_counter
    round_counter.start()
    while not all(x == 0 for x in mu_list):

        if round_counter.num_it_list[-1] > 30:
            # temporary, due to a bug in the code
            raise Exception("exceed the expected iteration count, i.e., {round_counter.num_it_list[-1]}")

        # Just for statistical purposes 
        round_counter.add_one()

        I = [1 if mu_xi > 0 else 0 for mu_xi in mu_list]
        if op_mode.state == OperationState.S1:
            # Compute torsion points of the correct orders, as reflected by the `GetTorsionPoint` method.
            efj = EpsFdistJs(clibx, e, I)
            Tpn = Algorithm_4(clibx, AA24, efj, flg=torsion_point_flg)
        
        elif op_mode.state == OperationState.S0:
            efj = input_efj
            # It indicates that torsion points are already provided in the input (i.e., Tpn).
            pass
        
        else:
            raise("Not implemented")

        AA24, fs, e = algorithm_inner_loop(clibx, Tpn, AA24, e, op_mode, efj)

        # updating the batch bound
        for i in range(batch_length):
            mu_list[i]  = mu_list[i] - fs[i]

        # update the operation statue 
        # The `OperationMode` class is not fully implemented; however, it provides sufficient functionality for our current needs.
        op_mode.update()

    return AA24, e

def Algorithm_3(clibx : C_INTERFACE, A, e):
    # compute A24 of the input curve coefficient A
    A24 = clibx.xA24(A)
    AA24 = [A, A24] 

    mu_list = [copy.deepcopy(batchbound[B_i]) for B_i in range(len(batchbound))]
    
    op_mode = OperationMode(OperationState.S1)
    Tpn = [None, None]

    global round_counter
    round_counter.start()
    while not all(mu_i == 0 for mu_i in mu_list):
        round_counter.add_one()

        # to track a bug
        if round_counter.num_it_list[-1] > 30:
            # temporary, due to a bug in the code
            raise Exception("exceed the expected iteration count, i.e., {round_counter.num_it_list[-1]}")

        I = [1 if mu_xi > 0 else 0 for mu_xi in mu_list]
        efj = EpsFdistJs(clibx, e, I)

        # Compute torsion points of the correct orders, as reflected by the `GetTorsionPoint` method.
        Tpn = Algorithm_4(clibx, AA24, efj, flg=torsion_point_flg)

        AA24, fs, e = algorithm_inner_loop(clibx, Tpn, AA24, e, op_mode, efj)

        # updating the batch bound
        for i in range(batch_length):
            mu_list[i]  = mu_list[i] - fs[i]

        # update the operation statue 
        # The `OperationMode` class is not fully implemented; however, it provides sufficient functionality for our current needs.
        op_mode.update()

    return AA24[0]

def algorithm_inner_loop(clibx : C_INTERFACE, Tpn, AA24, e, op_mode:OperationMode, efj:EpsFdistJs):
    cprint("\n[+] algorithm_inner_loop", flg=inner_flg)

    # Initiate torsion-point failure flags.
    fs = [0 for _ in range(batch_length)]  


    for batch_idx in range(len(efj.targets)): 
        batch_number = efj.targets[batch_idx]

        if efj.I[batch_number] == 1:
            fs[batch_number], e, Tpn, AA24, pos_li = algorithm_inner_loop_computations(clibx, Tpn, AA24, e, batch_number, batch_idx, efj, flg=inner_flg)

            if batch_number == efj.targets[0]:
                Tpn[0] = clibx.xMUL_pos_const(Tpn[0], AA24[1], 0, pos_li, batch_number)

        
    cprint("[-] algorithm_inner_loop", flg=inner_flg)
    return AA24, fs, e

def algorithm_inner_loop_computations(clibx : C_INTERFACE, Tpn, AA24, e_i, batch_number, batch_idx, efj:EpsFdistJs, flg=False):
    cprint("\n[+] algorithm_inner_loop_computations", flg=flg)

    epsilon, f_s, P, Tpn = compute_current_kernel_P_and_next_itr_torsion_point_Ts_next(clibx, Tpn,  AA24[1], batch_number, batch_idx , efj, flg=scale_eval_flg)

    # len_of_T represents the expected number of torsion points to be evaluated, intended for efficiency purposes.
    if batch_number == efj.targets[0]:
        len_of_T = 2 # This should be 1 for our constant time implementation, Algorithm 3
    elif batch_number == efj.targets[-2]:
        len_of_T = 1
    elif batch_number == efj.targets[-1]:
        len_of_T = 0
    else:
        len_of_T = 2

    if len_of_T == 1:
        # A torsion point switching step primarily aimed at enhancing performance.
        target_batch_number = efj.targets[batch_idx+1] if batch_number != efj.targets[0] else batch_number
        target_s = select_torsion_point_index_Ts(efj.previous_epsilons[target_batch_number])
        Tpn[0] = Tpn[target_s]
        

    # Performing the isogeny evaluation, conditioned by f_s
    pos_li = get_pos_li(batch_number, efj.Js[batch_number])
    AA24[0], Tpn = f_conditioned_isogeny_evaluation(clibx, f_s, P, pos_li, batch_number, epsilon, AA24[0], Tpn, len_of_T, flg=flg)
    
    # Updating the secret and computing A24 of the (new) curve coefficient A
    e_i[pos_li] -= f_s  * epsilon
    AA24[1] = clibx.xA24(AA24[0]) if f_s else AA24[1]
    
    if len_of_T == 1:
        # (undo) Revert the earlier performance switching step.
        target_batch_number = efj.targets[batch_idx+1] if batch_number != efj.targets[0] else batch_number
        target_s = select_torsion_point_index_Ts(efj.previous_epsilons[target_batch_number])
        Tpn[target_s] = Tpn[0]

    cprint("[-] algorithm_inner_loop_computations", flg=flg)
    return f_s, e_i, Tpn, AA24, pos_li

def compute_current_kernel_P_and_next_itr_torsion_point_Ts_next(clibx : C_INTERFACE, Tx,  A24, batch_number, batch_idx, efj:EpsFdistJs, flg=False): 
    cprint(f"\n[+] compute_current_kernel_P_and_next_itr_torsion_point_Ts_next {batch_number}", flg=flg)

    # retrieve epsilon
    epsilon = efj.epsilons[batch_number]

    # compute the sign s
    s = select_torsion_point_index_Ts(efj.previous_epsilons[batch_number])
    
    # compute current kernel P and next itr torsion point Tx[next_s]
    target_batch = efj.targets[batch_idx+1::]
    P = copy.deepcopy(Tx[s]) 
    for k in target_batch: 
        if efj.I[k] == 1:
            j_k = efj.Js[k]
            if j_k != -1:         
                P = clibx.xMUL_pos_const(P, A24, 0, get_pos_li(k, j_k), k)

                # Compute next itr torsion point Tx[next_s]
                if target_batch and k == target_batch[0]:
                    next_epsilon = efj.epsilons[k] # check if zero 
                    next_f_tilde = efj.f_tilde_list[k]
                    next_cond =  (next_epsilon == 0) or (next_f_tilde == 0) 

                    # TODO, possible bug use copy.deepcopy
                    # Tx[s] = cmov(P, Tx[s], next_cond)
                    Tx[s] = cmov(copy.deepcopy(P), Tx[s], next_cond)
                    
  
    f_tilde= efj.f_tilde_list[batch_number]
    f_par  = cmov(0, clibx.is_at_infinity(P), epsilon == 0)
    f_s    = (1 - f_par) * f_tilde
    P      = cmov(Tx[s], P, epsilon == 0) # Tx[s] is dummy input can be any thing
 

    cprint("[-] compute_current_kernel_P_and_next_itr_torsion_point_Ts_next\n", flg=flg)
    return epsilon, f_s, P, Tx

def f_conditioned_isogeny_evaluation(clibx : C_INTERFACE, f, Tis, pos_li, pos_batch, epsilon, A, T_list, len_of_T, flg=False):
    cprint("\n[+] conditioned_evaluation", flg=flg)

    #  Skip isogeny evaluation since "Tis" is a point at infinity
    if not f:
        cprint("[-] conditioned_evaluation\n")
        return A, T_list
    
    # Create a deep copy of A to avoid altering the original data
    A_new = copy.deepcopy(A)

    # Initialize a list of projections with the correct length
    P_list = (proj * len_of_T)()

    # Populate P_list with deep copies of T_list elements based on P_index
    for idx in range(len_of_T):
        P_list[idx] = copy.deepcopy(T_list[idx])

    # Perform the isogeny operation using matryoshka method
    A_new, P_list = clibx.xISOG_matryoshka_const(A_new, P_list, len_of_T, Tis, pos_li, pos_batch)

    # Update A and T_list based on the modified P_list
    A = cmov(A_new, A, epsilon != 0)
    for idx in range(len_of_T):
        # T_list[idx] = copy.deepcopy(P_list[idx])
        T_list[idx] = cmov(P_list[idx], T_list[idx], epsilon != 0)
        
    cprint("[-] conditioned_evaluation\n", flg=flg)
    return A, T_list
