import copy
import math
from streamlining_src.action_system import identify_action_systems_for_private_strategy
from streamlining_src.c_interface import C_INTERFACE
from streamlining_src.helper import load_config, save_dict_to_file
from streamlining_src.new_g_action import system_action
from streamlining_src.new_g_action_aux import NumberExecutionRounds 
from streamlining_src.models import private_key


def get_stat(data):
    import numpy as np

    # Convert to NumPy array
    array_data = np.array(data)

    # Compute statistics
    mean = np.mean(array_data, axis=0)
    std_dev = np.std(array_data, axis=0)
    min_val = np.min(array_data, axis=0)
    max_val = np.max(array_data, axis=0)

    # Create a dictionary to store the statistics
    statistics = {
        'mean': mean,
        'std_dev': std_dev,
        'min': min_val,
        'max': max_val
    }
   
    return mean.tolist(), std_dev.tolist(), min_val.tolist(), max_val.tolist()
    # return statistics
 
def experimenting_private_action_set_evaluation(clibx : C_INTERFACE):
    print("[+] experimenting_private_action_set_evaluation: ")

    config_path = 'configs/config_private_action_set_evaluation.json'
    config_file = load_config(config_path)

    out_file_name = config_file["out_file_name"]

    sim_iteration = config_file["sim_iteration"]
    replication = config_file["replication"] # repeating trials
    sim_iteration = config_file["sim_iteration"]
    execution_set_factors = config_file["execution_set_factors"]
    execution_set_size = config_file["execution_set_size"] * execution_set_factors
    
    clibx.reset_counters() 
    num_it_total = NumberExecutionRounds()
    measure_of2 = []
    measure_of3 = []
    for itr_num in range(sim_iteration):
        print(f"[>] Running an experiment #{itr_num}, for execution set of size {execution_set_size}")

        A = clibx.get_A0()
        secret_set_size = execution_set_size + math.floor(execution_set_size * 0.0)  #use even numbers 
        # This sets the target batches between 3 and 13.
        start, end = 3, 12 
        # this sets d-common round(s) to be 1
        min_bound = 0

        search_flag = True
        while search_flag:
            action_list = clibx.generate_c_sk_v2(secret_set_size)
            action_list_int = [copy.deepcopy(ei.to_list()) for ei in action_list]
            matching_pairs = identify_action_systems_for_private_strategy(action_list_int, start, end, min_bound)
            e_list_l_new = []
            for pair, indices in matching_pairs.items():
                i = pair[0]
                j = pair[1]
                e_list_l_new.append(action_list_int[i])
                e_list_l_new.append(action_list_int[j])
                if execution_set_size == len(e_list_l_new):
                    search_flag = False
                    break
            action_list_int = e_list_l_new

        if execution_set_size != len(action_list_int):
            raise Exception("Not found the required set of secrets")
 
        action_list_to_sys = copy.deepcopy(action_list_int)
        Asys = copy.deepcopy(A)


        clibx.reset_counters()
        measure_of_temp_before = clibx.get_counters()
        try:
            for _ in range(replication):
                _, num_itm = system_action(clibx, Asys, action_list_to_sys, start, end, min_bound)
                num_it_total = num_it_total + num_itm
        except Exception as e:
            # Handle the exception and print the original error message
            print(f"An error occurred: {e}")
            print(f"skipping iteration {itr_num}")
            itr_num = itr_num - 1 
            continue
        measure_of_temp_after = clibx.get_counters()

        measure_of_delta = [a - b for a, b in zip(measure_of_temp_after, measure_of_temp_before)] 
        measure_of2.append([x / (execution_set_factors*replication) for x in measure_of_delta])

        clibx.reset_counters()
        measure_of_temp_before = clibx.get_counters()
        for _ in range(replication):
            for e_i in action_list_int:
                Ai = copy.deepcopy(A)
                e1 = private_key.from_int_list(e_i)
                _ = clibx.action(Ai, e1) 
        measure_of_temp_after = clibx.get_counters()

        measure_of_delta = [a - b for a, b in zip(measure_of_temp_after, measure_of_temp_before)]
        measure_of3.append([x / (execution_set_factors*replication) for x in measure_of_delta])

    num_it_total.normalize(sim_iteration*replication)
    print(num_it_total)

    mean_sys, std_dev_sys, min_val_sys, max_val_sys = get_stat(measure_of2)
    mean_ind, std_dev_ind, min_val_ind, max_val_ind = get_stat(measure_of3)

    print("[>] ####################################")
    print("[>] measure_of result_indiv = ", mean_ind)
    print("[>] measure_of std_dev_ind = ", std_dev_ind)
    print("[>] measure_of min_val_ind = ", min_val_ind)
    print("[>] measure_of max_val_ind = ", max_val_ind)

    print("[>] ####################################")
    print("[>] measure_of system_action = ", mean_sys)
    print("[>] measure_of std_dev_sys = ", std_dev_sys)
    print("[>] measure_of min_val_sys = ", min_val_sys)
    print("[>] measure_of max_val_sys = ", max_val_sys)

    per = [100*(mean_ind[i]-mean_sys[i])/mean_ind[i] for i in range(len(mean_sys))]
    print("[>] Percentage = ", per)

    # #######################
    # Saving our results
    D = {}
    keys = ["individual_computation", "strategic_computation", "percentage"]
    D[keys[0]] = mean_ind
    D[keys[1]] = mean_sys
    D[keys[2]] = per

    print(f"[>] D = {D}")
    save_dict_to_file(D, out_file_name)
    print(f"[>] The results is saved to: {out_file_name}")
    print("[-] experimenting_private_action_set_evaluation: ")

def experimenting_second_strategic_computation():
    fname = 'libstreamlining.so'
    clib5 = C_INTERFACE(fname)
    experimenting_private_action_set_evaluation(clib5)

if __name__ == '__main__':
    # uncomment
    experimenting_second_strategic_computation()