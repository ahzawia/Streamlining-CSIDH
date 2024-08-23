import copy
from ctypes import *
from streamlining_src.models import private_key, proj, public_key
from config import n_primes, p_list, batchstart, batchstop
from streamlining_src.new_g_action_helper import get_pos_li

class C_INTERFACE(object):

    def __init__(self, fname):
        self.lib = CDLL('./' + fname)
        self.PREFIX = 'highctidh_512_'
        self.lib_name = 'highctidh_'


    def reset_counters(self):
        self.lib.reset_counters()

    def get_counters(self):
        fp_mulsq_count = c_longlong()
        fp_sq_count = c_longlong()
        fp_addsub_count = c_longlong()
        self.lib.get_counters(byref(fp_mulsq_count),
                              byref(fp_sq_count),
                              byref(fp_addsub_count))
        
        SQR = 1.00
        ADD = 0.00
        metric_1 = fp_mulsq_count.value + SQR * fp_sq_count.value + ADD * fp_addsub_count.value

        SQR = 0.80
        ADD = 0.05
        metric_2 = fp_mulsq_count.value + SQR * fp_sq_count.value + ADD * fp_addsub_count.value
        return [fp_mulsq_count.value, fp_sq_count.value, fp_addsub_count.value, metric_1, metric_2]

    def xA24(self, A):
        A24 = proj()
        lib_xA24 = getattr(self.lib, f"{self.PREFIX}xA24")
        lib_xA24(byref(A24), byref(A))
        return A24

    def get_A0(self):
        A = proj()  
        A.x.set_from_large_integer(0)
        A.z.set_from_large_integer(1)
        return A
    
    def get_A_A24(self):
        A = self.get_A0()
        A24 = self.xA24(A)
        return A, A24 
    
    def get_pre_sampled_full_torsion_points_for_A0(self):
        # Important note: full torsion points for A0
        Tp = proj()
        Tp.x.set_from_large_integer(2863794232074819090142297885614451224712892034843146665750175510726192545237614004458801153412993874816745446399024802508134662350707317280993230242829580)
        Tp.z.set_from_large_integer(197424333874579646002798622862872456605858069132916498303460719607609977704645443789980248509198255076091497936908922358632183163604875103266203582214140)
        Tn = proj()
        Tn.x.set_from_large_integer(2863794232074819090142297885614451224712892034843146665750175510726192545237614004458801153412993874816745446399024802508134662350707317280993230242829580)
        Tn.z.set_from_large_integer(5129314462453043448745068995091733097463513425699805839308985922446399582321931093836911864517182998548535443707040522434030698078016498185676676705851519)
        return Tp, Tn 
    
    def to_public_key(self, in_A):
        pk_A = public_key()
        self.lib.to_public_key(byref(pk_A), byref(in_A))
        return pk_A #.value
    
    def action(self, in_A, priv):
        out_pk = public_key()
        in_pk  = self.to_public_key(in_A)

        lib_action = getattr(self.lib, f"{self.PREFIX}action")
        lib_action(byref(out_pk), byref(in_pk), byref(priv))
        return out_pk #.value
    
    def g_action_old(self, in_A, priv):
        out_A = proj() 
        self.lib.action_old(byref(out_A), byref(in_A), byref(priv))
        return out_A

    def elligator(self, A):
        num = 2 # each for the positive and the negative direction in the isogeny graph
        P_pm = (proj * num)()

        lib_elligator= getattr(self.lib, f"{self.PREFIX}elligator")
        lib_elligator(byref(P_pm[0]), byref(P_pm[1]), byref(A)) 
        return P_pm
    
    def random_coin_toss(self, epsilon, batch_number, j_i):
        pos_li = get_pos_li(batch_number, j_i)
        prime_target = p_list[pos_li]
        prime_lower_bound = p_list[batchstart[batch_number]]
        lib_random_coin= getattr(self.lib, f"{self.lib_name}random_coin")
        if epsilon == 0:
            coin = lib_random_coin(prime_lower_bound-1,  prime_lower_bound)
        else:
            coin = lib_random_coin(prime_target*(prime_lower_bound-1), prime_lower_bound*(prime_target-1)) 
        return abs(coin)
    
    def is_at_infinity(self, T:proj):
        return self.lib.is_at_infinity(byref(T))
     
    def clear_power_two(self, T, A24, A_affine):
        #  T is elliptic curve point, of type proj, on A24 of an affine = 0, or 1
        self.lib.clear_power_two(byref(T), byref(A24), A_affine)
        return T

    def xMUL_pos(self, T, A24, Aaffine, pos_li):
        #  T is elliptic curve point, of type proj, on A24 of an Affine = 0, or 1
        self.lib.xMUL_pos(byref(T), byref(A24), Aaffine, pos_li) 
        return T
    
    def xMUL_pos_const(self, T, A24, Aaffine, pos_li, pos_batch):
        #  T is elliptic curve point, of type proj, on A24 of an affine = 0, or 1

        batch_start_idx = batchstart[pos_batch]
        batch_end_idx = batchstop[pos_batch] -1
        if not (batch_start_idx <= pos_li <= batch_end_idx):
            raise ValueError(f"The prime indice {pos_li} is not within the range [{batch_start_idx}, {batch_end_idx}].")
    
        self.lib.xMUL_pos_const(byref(T), byref(A24), Aaffine, pos_li, pos_batch) 
        return T
    
    def csidh_private(self):
        lib_csidh_private= getattr(self.lib, f"{self.PREFIX}csidh_private")
        priv = private_key()
        lib_csidh_private(byref(priv))
        return priv

    # Update, this can be implemented much better, but for the sake of time, it will do.
    def generate_c_sk_v2(self, num_keys):
        s_list = []
        count = num_keys * 1000
        for i in range(num_keys):
            priv = self.csidh_private()
            priv_l = priv.to_list()
            # print(priv_l)
            if not any(priv_l == sublist for sublist in s_list):
                s_list.append(copy.deepcopy(priv))
            count = count - 1
            if count == 0:
                raise("could not find secrets")
        return s_list
   
    def sample_list_from_classgroup(self, num_keys):
 
        s_list = (private_key * num_keys)()

        count = num_keys * 1000
        self.lib.init_classgroup()
        for i in range(num_keys):
            vec_array = (c_int8 * n_primes)()
            self.lib.sample_from_classgroup(vec_array)

            priv = private_key()
            priv = priv.from_int_list(list(vec_array)) 
            priv_l = priv.to_list()

            if not any(priv_l == sublist for sublist in s_list):
                s_list[i] = copy.deepcopy(priv)
            count = count - 1
            if count == 0:
                raise("could not find secrets")
 
        self.lib.clear_classgroup()
        return s_list

    def xISOG_matryoshka(self, A, T, len_of_T, ker, pos_li):
        self.lib.xISOG_matryoshka_pos(byref(A), byref(T), len_of_T, byref(ker), pos_li)
        return A, T
    
    def xISOG_matryoshka_const(self, A, T, len_of_T, ker, pos_li, pos_batch):
        pos_lwr = batchstart[pos_batch]
        pos_luper = batchstop[pos_batch] - 1

        if not (pos_lwr <= pos_li <= pos_luper):
            raise ValueError(f"The prime indice {pos_li} is not within the range [{pos_lwr}, {pos_luper}].")
    
        self.lib.xISOG_matryoshka_pos_const(byref(A), byref(T), len_of_T, byref(ker), pos_li, pos_lwr, pos_luper)
        return A, T