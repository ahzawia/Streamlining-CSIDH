#  Proof-of-concept Implementation of: Streamlining CSIDH: Cost-Effective Strategies for Group Actions Evaluation


## Description
This implementation is intended to showcase the results of our work (to be released soon). It serves as a proof-of-concept for demonstration purposes only, with a more robust implementation anticipated in future projects. At present, our code benchmark focuses on CSIDH-512.

This project makes use of the following external library:
- **high-ctidh** - [high-ctidh](https://ctidh.isogeny.org/index.html) is a library that implements the CTIDH algorithm, designed for constant-time evaluation of the [CSIDH](https://eprint.iacr.org/2018/383.pdf) group action. We use this library as a benchmark to compare our computational improvements with the original CTIDH work. However, we currently built the high-CTIDH library using its fork, [
high-ctidh](https://git.xx.network/elixxir/high-ctidh), located at `proof_of_concept_implementation/high-ctidh/`. 


## Dependencies
List of libraries or packages required to run the experiments:
- numpy==1.26.4

You can install the required packages using:
```bash
 pip3 install -r requirements.txt 
```

Also, please review the Prerequisites section for our C code, which can be found in the `streamlining_c_src/README.md` file.

## Code Review
- Open the project in your preferred code editor (or terminal).
- Review the main files and scripts located in the `proof_of_concept_implementation/`, `proof_of_concept_implementation/streamlining_src/` , `proof_of_concept_implementation/streamlining_c_src`, `proof_of_concept_implementation/streamlining_c_src/csi-fish`, and `proof_of_concept_implementation/high-ctidh/` directories.
 

## Setup
First, we need to compile our C library. To do this, use the following bash script:
```bash
./build_full.sh
```
This should generate `libhighctidh_512.so` and `libstreamlining.so` in `str_line_csidh_src/` and `proof_of_concept_implementation/`

## Experiments

#### Running an experiment for public set evaluation
To run the first experiment, use the following command:
```bash
python3 experimenting_public_action_set_evaluation.py
```

The script generates and saves the data for Figure 1 into a file name: `outputs/figure1_first_strategic_computation.txt`. An example of an output:

```
D =  {
    2: {
        'individual_computation': [942199.325, 250986.05, 950952.625, 1193185.375, 1190535.7962500001], 
        'strategic_computation': [832048.975, 230054.9, 825458.675, 1062103.875, 1057365.8287499999], 
        'percentage': [11.690769360294329, 8.339567079524935, 13.196656352886137, 10.985845346956246, 11.185717214002711]},
    4: {....}
        }
```

where 2 is the execution set size, 'individual_computation' and 'strategic_computation' are the execution types. The results in the list are formatted as [M, S, a, Metric 1, Metric 2].


#### Running an experiment for private set evaluation
To run the second experiment, use the following command:
```bash
python3 experimenting_private_action_set_evaluation.py 
```
The script generates and saves the data for Figure 1 into a file name: `outputs/Table2_second_strategic_computation.txt`. An example of an output:

```
D =  {
     'individual_computation': [10752471.0, 2822344.5, 12031315.0, 13574815.5, 13611912.35], 
     'strategic_computation': [10027009.0, 2390594.5, 11697860.0, 12417603.5, 12524377.6], 
     'percentage': [6.746932867803131, 15.297565552327152, 2.7715590523562885, 8.52469781265167, 7.989580905580839]
     }
```

Similar to the previous execution, the output is for the execution types 'individual_computation' and 'strategic_computation'. The results in the list are formatted as [M, S, a, Metric 1, Metric 2].

#### Running an experiment for our CSIDH constant-time implementation
To run the second experiment, use the following command:
```bash
python3 experimenting_constant_time_csidh.py
```
The script generates and saves the data for Figure 1 into a file name: `outputs/Algorithm_3_computational_cost.txt`. An example of an output:

```
D =  {
     "ctidh": [446933.0667, 117177.4316, 500360.3617, 564110.4983, 565693.0300649991], 
     "Algorithm3": [434684.2504, 104208.9522, 505992.8885, 538893.2026, 543351.0565849999], 
     "percentage": [2.740637740331242, 11.067386631471443, -1.1256940459598352, 4.470275907999355, 3.949487141008634]
     }
```
 
where "ctidh" and "Algorithm3" represent the computational costs for the original CTIDH implementation and our Algorithm 3, respectively. The results are listed in the format [M, S, a, Metric 1, Metric 2], with "percentage" indicating the percentage difference between them.
