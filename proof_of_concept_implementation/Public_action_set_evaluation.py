import copy
from c_interface import C_INTERFACE
from action_system import pinpoint_action_systems, sum_pair_wise_vectors_of_vector
from action_system import percentage_fun
from helper import save_dict_to_file 

def experimenting_Public_action_set_evaluation(exe_set_size, sim_iteration):
    fname = 'libstreamlining.so'
    mct = C_INTERFACE(fname) 
    A = mct.get_A0()
    E0 = A 
    r_individual_list = []
    strategic_q_r1r2_list = []
    for itr in range(sim_iteration):
        action_list = mct.sample_list_from_classgroup(exe_set_size)
        action_list_bu = copy.deepcopy(action_list)
        
        mct.reset_counters()
        for sk_i in range(exe_set_size):
            EA = mct.g_action_old(copy.deepcopy(E0), action_list[sk_i])
        r_individual_list.append(mct.get_counters())

        s_sys = pinpoint_action_systems(action_list_bu) 
    
        mct.reset_counters()
        for sk_i in range(exe_set_size // 2):
            Ex  = mct.g_action_old(E0, s_sys[3*sk_i])
            Ex1 = mct.g_action_old(copy.deepcopy(Ex), s_sys[3*sk_i + 1])
            Ex2 = mct.g_action_old(copy.deepcopy(Ex), s_sys[3*sk_i + 2])
        strategic_q_r1r2_list.append(mct.get_counters())

    r_individual_list_total = sum_pair_wise_vectors_of_vector(r_individual_list)
    strategic_q_r1r2_list_total = sum_pair_wise_vectors_of_vector(strategic_q_r1r2_list)

    percentage = list(map(percentage_fun, strategic_q_r1r2_list_total, r_individual_list_total))

    r_individual_list_total = [r_individual_list_total[0] / sim_iteration, r_individual_list_total[1] / sim_iteration,
                     r_individual_list_total[2] / sim_iteration, r_individual_list_total[3] / sim_iteration,
                     r_individual_list_total[4] / sim_iteration]

    strategic_q_r1r2_list_total = [strategic_q_r1r2_list_total[0] / sim_iteration, strategic_q_r1r2_list_total[1] / sim_iteration,
                       strategic_q_r1r2_list_total[2] / sim_iteration, strategic_q_r1r2_list_total[3] / sim_iteration,
                       strategic_q_r1r2_list_total[4] / sim_iteration]
 

    return r_individual_list_total, strategic_q_r1r2_list_total, percentage

def experimenting_first_strategic_computation():
    out_file_name = "outputs/figure1_first_strategic_computation.txt"
    execution_set_size_max = 60
    sim_iteration = 5000
    
    # step = 8
    step = 4

    D = {}
    keys = ["individual_computation", "strategic_computation", "percentage"]
    for exe_set_size in range(2, execution_set_size_max, step):
        print("[+] Start for execution set size : ", exe_set_size, " of ", execution_set_size_max)
        D[exe_set_size] = dict(zip(keys, list(experimenting_Public_action_set_evaluation(exe_set_size, sim_iteration))))
    print("D = ", D)
    save_dict_to_file(D, out_file_name)

    print(f"[-] The results is saved to: {out_file_name}")


if __name__ == '__main__':
    # uncomment
    experimenting_first_strategic_computation()
 