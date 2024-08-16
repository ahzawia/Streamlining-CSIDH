import copy
import random  
from c_interface import C_INTERFACE
from new_g_action_aux import EpsFdistJs
from new_g_action_helper import int_cswap, get_pos_li, cprint
from config import batch_length, batchsize, batchstart

def clear_public_primes(clibx : C_INTERFACE, Tx, A24, I):
    # Step 2: Multiplication by 4
    Tx = clibx.clear_power_two(Tx, A24, 0)
    # Product of all primes where i not in I and J_i = j
    for i in range(batch_length):
        if I[i] == 0 :
            for j in range(batchsize[i]):
                pos_li = get_pos_li(i, j)
                Tx = clibx.xMUL_pos(Tx, A24, 0, pos_li)
    return Tx

# TODO This can be implemented much better, but for the sake of time, it will do.
def Algorithm_4(clibx : C_INTERFACE, As, efj:EpsFdistJs, flg=False):
    cprint("\n[+] Algorithm_4: ", flg=flg)

    #  init the output
    Tpn = [None, None]
    Tp, Tn = clibx.elligator(As[0])
    Tp = clear_public_primes(clibx, Tp, As[1], efj.I)
    Tn = clear_public_primes(clibx, Tn, As[1], efj.I)

    epsilon_previous = 1
    eps_list = []

    for i in efj.targets:
        if efj.I[i] == 1:
            j_i = efj.Js[i] 
            if j_i ==-1:
                raise(f"Algorithm_4: j_i = -1!!")
            
            epsilon = efj.epsilons[i]
            cond = not ((epsilon == 0) or (efj.f_tilde_list[i] == 0))
            epsilon_previous, _ = int_cswap(epsilon_previous, epsilon, cond)

            eps_list.append(epsilon)

            dir_p = epsilon_previous == 1
            dir_n = epsilon_previous == -1
            for jth in range(batchsize[i]):
                pos_li = get_pos_li(i, jth)

                if dir_p:
                    Tn = clibx.xMUL_pos(Tn, As[1], 0, pos_li)
                elif dir_n:
                    Tp = clibx.xMUL_pos(Tp, As[1], 0, pos_li)
                else:
                    raise(f"Algorithm_4: we should not be here, maybe I is wrong!!")
            
            for jth in range(batchsize[i]):
                pos_li = get_pos_li(i, jth)
                if dir_p:
                    if j_i != jth:
                        Tp = clibx.xMUL_pos_const(Tp, As[1], 0, pos_li, i)

                elif dir_n:
                    if j_i != jth:
                        Tn = clibx.xMUL_pos_const(Tn, As[1], 0, pos_li, i)
                else:
                    raise(f"Algorithm_4: we should not be here, maybe I is wrong!!")

    Tpn[0] = Tp 
    Tpn[1] = Tn

    cprint("[-] Algorithm_4:", flg=flg)
    return Tpn

# Not finished
# This can be implemented much better, but for the sake of time, it will do.
def helper_gen_Tpn_p_pair_signed(clibx : C_INTERFACE, Tp, Tn, A24, target_com, efj:EpsFdistJs):
    target_p_updates = []
    target_n_updates = []

    epsilon_previous = 1
    eps_list = []

    for i in efj.targets:
        if efj.I[i] == 1:
            j_i = efj.Js[i] 
            if j_i ==-1:
                raise(f"gen_point_pair: j_i = -1!!")
            
            epsilon = efj.epsilons[i]
            cond = not ((epsilon == 0) or (efj.f_tilde_list[i] == 0))
            epsilon_previous, _ = int_cswap(epsilon_previous, epsilon, cond)

            eps_list.append(epsilon)

            dir_p = epsilon_previous == 1
            dir_n = epsilon_previous == -1

            # print(f"batch {i} and previous non-zero batch is {i_previous}")

            for jth in target_com[i]:
                pos_li = get_pos_li(i, jth)

                if dir_p:
                    Tn = clibx.xMUL_pos_const(Tn, A24, 0, pos_li, i)
                    target_n_updates.append(pos_li)
                elif dir_n:
                    Tp = clibx.xMUL_pos_const(Tp, A24, 0, pos_li, i)
                    target_p_updates.append(pos_li)
                else:
                    raise(f"gen_point_pair: we should not be here, maybe I is wrong!!")
            
            for jth in target_com[i]:
                pos_li = get_pos_li(i, jth)
                if dir_p:
                    if j_i != jth:
                        Tp = clibx.xMUL_pos_const(Tp, A24, 0, pos_li, i)
                        target_p_updates.append( pos_li )

                elif dir_n:
                    if j_i != jth:
                        Tn = clibx.xMUL_pos_const(Tn, A24, 0, pos_li, i)
                        target_n_updates.append( pos_li )
                else:
                    raise(f"gen_point_pair: we should not be here, maybe I is wrong!!")
    
    return Tp, Tn, target_p_updates, target_n_updates

# Not finished
# This can be implemented much better, but for the sake of time, it will do.
def gen_Tpn_p_pair_signed(clibx : C_INTERFACE, in_Tp, in_Tn, A24, efj1:EpsFdistJs, efj2:EpsFdistJs, flg=False): 
    cprint("\n[+] gen_Tpn_p_pair_signed: ", flg=flg)   


    if (efj1.I != efj2.I) or (efj1.targets != efj2.targets) :
        raise("gen_Tpn_p_pair_signed: targets mismatch!")
    
    I = efj1.I
    J1 = efj1.Js
    J2 = efj2.Js
    targets = efj1.targets
    
    #  to avoid a bugs 
    Tp = copy.deepcopy(in_Tp)
    Tn = copy.deepcopy(in_Tn) 

    # target_com is the list of all j values representing the required order of Tout
    target_com = [[] for _ in range(batch_length)]
    for i in range(batch_length):
        if I[i] == 1:
            pos_start = 0  # Starting position, static in your code, might be dynamic in some contexts
            
            if batchsize[i] <= 2:
                target_com[i].extend(pos_start + j for j in range(batchsize[i]))
            else:
                j_trial1 = J1[i]
                j_trial2 = J2[i] if J2[i] != j_trial1 else random.choice(
                    [x for x in range(batchsize[i]) if x != j_trial1])  # Choose j_trial2 different from j_trial1

                target_com[i].extend(pos_start + j for j in range(batchsize[i]) if j == j_trial1 or j == j_trial2)


    # CLEAR ALL COMMON FACTORS OUT OF target_com
    for i in range(batch_length):
        if I[i] == 1: # redundant but to make sure
            if batchsize[i] > 2:
                for j in range(batchsize[i]):
                    if j not in target_com[i]:
                        pos_li = batchstart[i] + j
                        Tp = clibx.xMUL_pos_const(Tp, A24, 0, pos_li, i)
                        Tn = clibx.xMUL_pos_const(Tn, A24, 0, pos_li, i)

    Tp1 = copy.deepcopy(Tp)
    Tn1 = copy.deepcopy(Tn)
    Tp1, Tn1, _, _ = helper_gen_Tpn_p_pair_signed(clibx, Tp1, Tn1, A24, target_com, efj1)
   
    Tp2 = copy.deepcopy(Tp)
    Tn2 = copy.deepcopy(Tn)
    Tp2, Tn2, _, _ = helper_gen_Tpn_p_pair_signed(clibx, Tp2, Tn2, A24, target_com, efj2)

    cprint("[-] gen_Tpn_p_pair_signed: ", flg=flg)   
    return [Tp1,Tn1], [Tp2,Tn2]
 
def Algorithm_5_with_pre_sampled_torsion_points(clibx : C_INTERFACE, Tp, Tn, e_size, As, efj_list, flg=False):
    cprint("\n[+] Algorithm_5_with_pre_sampled_torsion_points: ", flg=flg)

    Tpn_p_list = [[None, None] for _ in range(e_size)]
    if e_size%2 != 0 :
        raise(f"generate_Tpn_p_list: the current code support even number of secrets e size ={e_size}")
    for e_idx in range(e_size//2):
        e_idx1 = 2 * e_idx
        e_idx2 = 2 * e_idx + 1
        Tpn_p_list[e_idx1], Tpn_p_list[e_idx2]= gen_Tpn_p_pair_signed(clibx, Tp, Tn, As[1], efj_list[e_idx1], efj_list[e_idx2], flg=flg)

    cprint("[-] Algorithm_5_with_pre_sampled_torsion_points: ", flg=flg)
    return Tpn_p_list

def Algorithm_5(clibx : C_INTERFACE, e_size, As, efj_list, flg=False):
    cprint("\n[+] Algorithm_5: ", flg=flg) 
    
    I = efj_list[0].I 
    Tp, Tn = clibx.elligator(As[0]) 
    Tp = clear_public_primes(clibx, Tp, As[1], I) 
    Tn = clear_public_primes(clibx, Tn, As[1], I)

    Tpn_p_list = Algorithm_5_with_pre_sampled_torsion_points(clibx, Tp, Tn, e_size, As, efj_list, flg=flg)

    cprint("[-] Algorithm_5: ", flg=flg)
    return Tpn_p_list