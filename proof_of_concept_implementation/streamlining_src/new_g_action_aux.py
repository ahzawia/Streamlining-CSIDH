from streamlining_src.c_interface import C_INTERFACE
from config import batch_length, batchstart
from streamlining_src.new_g_action_helper import int_cswap, find_first_nonzero_j, cprint

# A class that counts the number of execution rounds evaluating a group of action(s).
class NumberExecutionRounds():
    def __init__(self, num_it_list=None):
        """Initializes the class with an optional list of iteration counts."""
        self.num_it_list = num_it_list if num_it_list is not None else []
    
    def start(self):
        """Starts a new round of execution."""
        self.num_it_list.append(0)

    def add_one(self):
        """Increments the last execution round by one."""
        if not self.num_it_list:
            raise IndexError("No execution round started. Call start() first.")
        self.num_it_list[-1] += 1
    
    def __add__(self, other):
        """Adds the execution rounds of another NumberExecutionRounds object."""

        if not isinstance(other, NumberExecutionRounds):
            raise TypeError("Both operands must be of type NumberExecutionRounds")

        if self.num_it_list and other.num_it_list:
            result_list = [a + b for a, b in zip(self.num_it_list, other.num_it_list)]
        elif self.num_it_list:
            result_list = self.num_it_list
        else:
            result_list = other.num_it_list
        
        return NumberExecutionRounds(result_list)
    
    def normalize(self, itr):
        """Normalizes the execution rounds by dividing by the given iteration count."""
        self.num_it_list = [a/itr for a in self.num_it_list]

    def __repr__(self):
        """Returns a string representation of the object."""
        total_rounds = sum(self.num_it_list)
        return f"[>] NumberExecutionRounds(Total rounds of execution: {total_rounds}; separate actions rounds: {self.num_it_list})"
    
    def __str__(self):
        """Returns a user-friendly string representation of the object."""
        return self.__repr__()
    
class EpsFdistJs():
    """Manages epsilon values, F-distribution, and J indices."""
    def __init__(self, clibx, in_e, I):
        self.I = I
        self.Js = [-1] * batch_length
        self.epsilons = [0] * batch_length
        self.f_tilde_list = [0] * batch_length

        self.previous_epsilons = None

        # set target batches
        self.targets = []
        self.current_targets_idx = 0

        # TODO this should be "find_random_j"
        self.Js_method = find_first_nonzero_j

        # init the parameters
        self.initialize_parameters(clibx, in_e, I)
        
    def initialize_parameters(self, clibx : C_INTERFACE, e, I):
        """Initialize parameters and set the multiplication strategy."""
        self.I = I
        self.compute_js_epsilon_and_f_tilde(clibx, e, I)
        self.set_multiplication_strategy(I)
        self.update_previous_epsilon()

    def compute_js_epsilon_and_f_tilde(self, clibx : C_INTERFACE, e, I):
        """Compute Js, epsilon, and f_dist based on I and e."""
        for i in range(batch_length):
            if I[i] == 1:
                self.Js[i], self.epsilons[i] = self.Js_method(e, i)
                self.f_tilde_list[i] = clibx.random_coin_toss(self.epsilons[i], i, self.Js[i])

    def get_first_epsilon(self):
        """Retrieve the first epsilon value for the current target."""
        if not self.targets:
            raise ValueError("Targets have not been set.")
        return self.epsilons[self.targets[0]]

    def get_previous_epsilon(self):
        """Calculate and store the previous epsilon values."""
        # previous_epsilons = get_previous_epsilon(self.epsilons, self.f_dist, self.targets, self.I)
        self.previous_epsilons = [0] * batch_length
        epsilon_par = 1
        for i in self.targets:
            if self.I[i] == 1:
                epsilon_i = self.epsilons[i]
                cond = not ((epsilon_i == 0) or (self.f_tilde_list[i] == 0))
                epsilon_par, _ = int_cswap(epsilon_par, epsilon_i, cond)
                self.previous_epsilons[i] = epsilon_par
        return self.previous_epsilons
    
    def update_previous_epsilon(self):
        """Calculate and store the previous epsilon values."""
        # self.epsilon_previous = get_previous_epsilon(self.epsilons, self.f_dist, self.targets, self.I)
        self.get_previous_epsilon()
    
    def print_info(self, flg=True):
        """Output detailed information about the class state."""
        info = {
            "I": self.I,
            "targets": self.targets,
            "Js": self.Js,
            "Js indx": [batchstart[i] + self.Js[i] if self.I[i] == 1 else -1 for i in range(batch_length)],
            "f_dist": self.f_tilde_list,
            "epsilon": self.epsilons,
            "epsilon_previous": self.previous_epsilons,
            "(ordered) f_dist": [self.f_tilde_list[i] for i in self.targets],
            "(ordered) epsilon": [self.epsilons[i] for i in self.targets],
            "(ordered) epsilon_previous": [self.previous_epsilons[i] for i in self.targets]
        }
        for key, value in info.items():
            cprint(f"{key} = {value}", flg=flg)

    def to_next_target(self):
        """Move to the subsequent target index."""
        self.current_targets_idx = self.current_targets_idx + 1

    def set_multiplication_strategy(self, I):
        """Determine the order of target batch indices for multiplication and evaluation."""
        # This function will be updated to improve performance, but for now, it remains a TODO.
        self.targets = [i for i in range(batch_length-1, -1,-1) if I[i] == 1]
        target_temp  = self.targets[:2]
        self.targets = self.targets[2:] + target_temp[::-1]
        self.current_targets_idx = 0
