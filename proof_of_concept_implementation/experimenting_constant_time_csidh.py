import copy
from streamlining_src.c_interface import C_INTERFACE
from streamlining_src.helper import add_fun, load_config, percentage_fun, mean_fun, save_dict_to_file
from streamlining_src.models import private_key
from streamlining_src.new_g_action import Algorithm_3 


def test_CT_g_action_correctness_Algorithm_3(clibx : C_INTERFACE, sim_iteration):
    print("[+] test_CT_g_action_correctness_Algorithm_3: ")

    e_list = clibx.generate_c_sk_v2(sim_iteration)
    for i in range(sim_iteration):
        A = clibx.get_A0()
        e_i = e_list[i]
        pk0 = clibx.action(copy.deepcopy(A), copy.deepcopy(e_i))
 
        A_out = Algorithm_3(clibx, copy.deepcopy(A), copy.deepcopy(e_i))
        pk1 = clibx.to_public_key(A_out)
 
        if not (pk0 == pk1):
            pk0.print("pk0")
            pk1.print("pk1")  
            raise Exception(f"for the {i}th key, they are not equal") 
    print("[-] test_CT_g_action_correctness_Algorithm_3: ")

def experimenting_Algorithm_3(clibx : C_INTERFACE, sim_iteration, replication, out_file_name):
    print("[+] experimenting_Algorithm_3: ")

    e_list = clibx.generate_c_sk_v2(sim_iteration)
    A = clibx.get_A0()

    measure_of_ctidh = [0.0, 0.0, 0.0, 0.0, 0.0]
    measure_of_our   = [0.0, 0.0, 0.0, 0.0, 0.0]

    e_size_actual = 0  # added due to a bug
    for e_i in e_list: 

        e = private_key.to_list(copy.deepcopy(e_i))
        try:
            measure_of_our_sk   = [0.0, 0.0, 0.0, 0.0, 0.0]
            for _ in range(replication):
                clibx.reset_counters()
                A_out = Algorithm_3(clibx, copy.deepcopy(A), copy.deepcopy(e))
                pk_i = clibx.to_public_key(A_out)
                measure_of_our_i = clibx.get_counters()
                measure_of_our_sk = list(map(add_fun, measure_of_our_sk, measure_of_our_i))

            measure_of_our = list(map(add_fun, measure_of_our, measure_of_our_sk))
        except Exception as e: 
            print(f"An error occurred: {e}")
            print(f"skipping sk :{e_i}")
            continue
        
        for _ in range(replication):
            clibx.reset_counters()
            pk0 = clibx.action(copy.deepcopy(A), copy.deepcopy(e_i)) 
            measure_of_ctidh_i = clibx.get_counters()
            measure_of_ctidh = list(map(add_fun, measure_of_ctidh, measure_of_ctidh_i))

        e_size_actual = e_size_actual + 1
        print(f"[>] iteration #{e_size_actual} is done ")

    total_tries = replication * e_size_actual #e_size
    measure_of_ctidh = mean_fun(measure_of_ctidh, total_tries)
    measure_of_our   = mean_fun(measure_of_our, total_tries) 

    percentage = list(map(percentage_fun, measure_of_our, measure_of_ctidh))

    print("[>] measure_of_ctidh = ", measure_of_ctidh)
    print("[>] measure_of_our = ", measure_of_our)
    print("[>] percentage = ", percentage)

    D = {}
    keys = ["ctidh", "Algorithm3", "percentage"]
    D[keys[0]] = measure_of_ctidh
    D[keys[1]] = measure_of_our
    D[keys[2]] = percentage
    print(f"[>] D = {D}")

    save_dict_to_file(D, out_file_name)
    print(f"[>] The results is saved to: {out_file_name}")

    print("[-] experimenting_Algorithm_3: ")

def experimenting_constant_time_csidh():
    fname = 'libstreamlining.so'
    clib3 = C_INTERFACE(fname) 

    config_path = 'configs/config_constant_time_csidh.json'
    config_file = load_config(config_path)

    out_file_name = config_file["out_file_name"]
    sim_iteration = config_file["sim_iteration"]
    replication = config_file["replication"]

    # test_CT_g_action_correctness_Algorithm_3(clib3, sim_iteration)
    experimenting_Algorithm_3(clib3, sim_iteration, replication, out_file_name)

if __name__ == '__main__':
    # uncomment
    experimenting_constant_time_csidh()
