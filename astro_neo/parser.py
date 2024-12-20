# Parser for Inputs files
import configparser
from dataclasses import dataclass, field

from astro_neo.helper import Bcolors


def check_key(data_list, key_list):
    for this_key in key_list:
        if this_key not in data_list:
            raise KeyError(str(this_key) + ' is missing')


def print_input_file(file_dict):
    for key, value in file_dict.items():
        print("[" + Bcolors.BOLD + str(key) + Bcolors.ENDC + "]")
        for inner_key, inner_value in value.items():
            print('---' + inner_key + ": " + inner_value)


def check_optional_key(og_dict, optional_key_list):
    optional_key = []
    for i in range(len(optional_key_list)):
        try:
            og_dict[optional_key_list[i]]
        except KeyError:
            optional_key.append(optional_key_list[i])

    return optional_key


@dataclass
class InputParamsParser:
    input_dict: dict = field(default_factory=dict)

    def read_input_file(self, input_file, verbose=False):
        config_parser = configparser.ConfigParser()
        config_parser.read(input_file)
        config = config_parser.sections()
        # read into each dict
        file_min = ['Inputs', 'Populations', 'Solvers', 'Mutations', 'Paths', 'Outputs']

        check_key(config, file_min)

        inputs_dict = config_parser['Inputs']
        populations_dict = config_parser['Populations']
        mutations_dict = config_parser['Mutations']
        solvers_dict = config_parser['Solvers']
        paths_dict = config_parser['Paths']
        Outputs_dict = config_parser['Outputs']

        # Checking for minimum inputs
        input_min = ['data_dir', 'data_file', 'output_file']
        input_optional = ['bg_file', 'rsp_file']
        check_key(inputs_dict.keys(), input_min)
        input_missing = check_optional_key(inputs_dict, input_optional)

        population_min = ['population', 'num_gen', 'best_sample', 'lucky_few']
        check_key(populations_dict.keys(), population_min)

        mutation_min = ['chance_of_mutation', 'original_chance_of_mutation']
        mutation_optional = ['mutated_options', 'selection_options', 'crossover_options', 'mutf', 'mutcr']
        check_key(mutations_dict.keys(), mutation_min)
        mut_optional = check_optional_key(mutations_dict, mutation_optional)

        solver_optional = ['solver_type']
        solver_missing = check_optional_key(solvers_dict, solver_optional)

        path_min = ['npaths', 'center', 'fits']
        path_optional = []
        check_key(paths_dict.keys(), path_min)
        path_missing = check_optional_key(paths_dict, path_optional)

        output_min = ['print_graph', 'num_output_paths']
        output_optional = ['steady_state_exit', 'distributed']
        check_key(Outputs_dict.keys(), output_min)
        output_missing = check_optional_key(Outputs_dict, output_optional)
        # Adjust values

        # Pack all of them into a single dicts
        self.input_dict['Inputs'] = inputs_dict
        self.input_dict['Populations'] = populations_dict
        self.input_dict['Mutations'] = mutations_dict
        self.input_dict['Solvers'] = solvers_dict
        self.input_dict['Paths'] = paths_dict
        self.input_dict['Outputs'] = Outputs_dict

        if verbose:
            print_input_file(self.input_dict)

    def verbose(self):
        print_input_file(self.input_dict)

    def export_input_dict(self):
        """
        Convert the file dictionary from multiple dimensions into a singple dictionary
        """
        temp_dict = {
            # Input
            'data_dir': self.input_dict['Inputs']['data_dir'],
            'data_file': self.input_dict['Inputs']['data_file'],
            'output_file': self.input_dict['Inputs']['output_file'],
            'bg_file': self.input_dict['Inputs']['bg_file'],
            'rsp_file': self.input_dict['Inputs']['rsp_file'],

            # Population
            'nPops': int(self.input_dict['Populations']['population']),
            'nGen': int(self.input_dict['Populations']['num_gen']),

            'selOpt': int(self.input_dict['Mutations']['selection_options']),
            'nBestSample': int(self.input_dict['Populations']['best_sample']),
            'nLuckySample': int(self.input_dict['Populations']['lucky_few']),
            # Mutation

            'mut_options': int(self.input_dict['Mutations']['mutated_options']),
            'mutChance': int(self.input_dict['Mutations']['chance_of_mutation']),

            'croOpt': int(self.input_dict['Mutations']['crossover_options']),

            'cR': float(self.input_dict['Mutations']['mutcr']),
            'mutF': float(self.input_dict['Mutations']['mutf']),

            # Solver
            'solver_type': int(self.input_dict['Solvers']['solver_type']),

            # Paths
            'npaths': int(self.input_dict['Paths']['npaths']),
            'center': self.input_dict['Paths']['center'],
            'fits': self.input_dict['Paths']['fits'],
            # 'npaths': self.input_dict['Paths']['path_list'],
            # 'individualOptions': self.input_dict['Paths']['individual_path'],

            # Outputs
            'steadyState': self.input_dict['Outputs']['steady_state_exit'],
            'printGraph': self.input_dict['Outputs']['print_graph'],
            'distributed': self.input_dict['Outputs']['distributed'],
        }

        return temp_dict
## Need to run some sample:
# if __name__ == '__main__':
#
#     checkKey()
