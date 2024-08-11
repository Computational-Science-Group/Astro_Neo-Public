from astro_neo.helper import str_to_bool

"""
Author: Andy Lau
Last Updated: 1/19/2021

Changes:

2/8/2021: Andy:
    - Function definition for arr to be in 2D

1/20/2021: Andy:
    - Function definition for optional parameters.
    - Changes to allows for multiple inputs folder.

"""


def split_list(arr_str, convert_type=None):
    if convert_type is None:
        return arr_str.split(',')
    else:
        return [convert_type(i) for i in arr_str.split(',')]


def split_path_arr(arr_str, num_compounds):
    """
    Read the path list

    @param str arr_str: str of array for the path list
    @param int num_compounds: number of compounds
    @return:
    """

    starter = []
    end = []
    k = 0
    split_str = []
    for i in arr_str:
        if i == '[':
            starter.append(k)
        elif i == ']':
            end.append(k)
        k = k + 1

    assert (len(starter) == len(end)), 'Bracket setup not right.'
    if num_compounds > 1:
        assert (num_compounds == len(starter)), 'Number of compounds not matched.'
        assert (num_compounds == len(end)), 'Number of compounds not matched.'

    # check if both are zeros, therefore the array is one 1 dimensions
    if len(starter) == 0 and len(end) == 0:
        split_str = list(arr_str.split(","))
    else:
        for i in range(len(starter)):
            split_str.append(arr_str[starter[i] + 1:end[i]].split(","))

    return split_str


def optional_var(input_dict, name_var, alt_var=None, type_var=int, output_var=True):
    """Detections of optional variables exists within input files, and put in corresponding default inputs parameters.
    boolean needs special attentions

    @param dict input_dict: input dictionary
    @param str name_var: name of the variable
    @param str alt_var: alternative of the variable
    @param type type_var: default type of the variable
    @param str output_var: type of variable.
    @return:
    """
    if type_var == bool:
        if name_var in input_dict:
            return_var = str_to_bool(input_dict[name_var])
        else:
            return_var = alt_var
    elif type_var is None:
        if name_var in input_dict:
            return_var = input_dict[name_var]
        else:
            return_var = None
    else:
        if name_var in input_dict:
            return_var = type_var(input_dict[name_var])
        else:
            return_var = type_var(alt_var)

    # return return_var
    input_dict[name_var] = return_var
    if output_var:
        return return_var


def validate_input_file(file_dict):
    inputs_dict = dict(file_dict['Inputs'].items())
    populations_dict = dict(file_dict['Populations'].items())
    mutations_dict = dict(file_dict['Mutations'].items())
    paths_dict = dict(file_dict['Paths'].items())
    outputs_dict = dict(file_dict['Outputs'].items())

    # Inputs
    data_dir = inputs_dict['data_dir']
    data_file = inputs_dict['data_file']
    output_file = inputs_dict['output_file']
    bg_file = optional_var(inputs_dict, 'bg_file', None, None)
    rsp_file = optional_var(inputs_dict, 'rsp_file', None, None)

    # Solver Options

    # Population
    size_population = int(populations_dict['population'])
    number_of_generation = int(populations_dict['num_gen'])
    # print(populations_dict)
    populations_dict['best_sample'] = int(float(populations_dict['best_sample']) / size_population)
    populations_dict['lucky_few'] = int(float(populations_dict['lucky_few']) / size_population)

    # Mutations
    mutations_dict['chance_of_mutation'] = 0.01 * float(mutations_dict['chance_of_mutation'])
    mutations_dict['original_chance_of_mutation'] = 0.01 * float((mutations_dict['original_chance_of_mutation']))
    # mutations_dict['chance_of_mutation_e0'] = 0.01 * float((mutations_dict['chance_of_mutation_e0']))
    selection_options = optional_var(mutations_dict, 'selection_options', 0, int)
    mutation_options = optional_var(mutations_dict, 'mutated_options', 0, int)
    crossover_options = optional_var(mutations_dict, 'crossover_options', 0, int)

    # Paths
    npaths = int(paths_dict['npaths'])
    paths_dict['center'] = split_list(paths_dict['center'], float)
    paths_dict['fits'] = split_list(paths_dict['fits'])

    # paths_dict['path_optimize'] = optional_var(paths_dict, 'path_optimize', False, bool)
    # paths_dict['path_optimize_percent'] = optional_var(paths_dict, 'path_optimize_percent',
    #                                                    0.01, float)

    # Output
    printgraph = str_to_bool(outputs_dict['print_graph'])
    num_output_paths = str_to_bool(outputs_dict['num_output_paths'])
    outputs_dict['distributed'] = optional_var(outputs_dict, 'distributed', 1, int)
    outputs_dict['steady_state_exit'] = optional_var(outputs_dict, 'steady_state_exit', False, bool)

    # Map it back into single dictionary
    validated_data_dict = {
        'Inputs': inputs_dict,
        'Populations': populations_dict,
        'Mutations': mutations_dict,
        'Paths': paths_dict,
        'Outputs': outputs_dict
    }
    # Package into a single dictionary
    return validated_data_dict
