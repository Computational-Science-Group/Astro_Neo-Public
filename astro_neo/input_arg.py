from . import parser as fileParser
from . import helper
import argparse, os, sys

def input():
    parser = argparse.ArgumentParser()

    parser.add_argument('-i','--input',help="Submit input file to EXAFS")
    parser.add_argument("-v","--verbose",help="output verbosity",action="store_true")
    parser.add_argument("-s","--show_input",help = "show input file",action="store_true")
    parser.add_argument("-t",help = "Timeing mode",action="store_true")


    args = parser.parse_args()

    if len(sys.argv)==1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    # Read in file if -i argument is printed
    if args.input!=None:
        file_path = os.path.join(os.getcwd(),args.input)
        file_dict = fileParser.read_input_file(file_path)

    # Read input file
    if args.show_input==True and args.input != None:
        file_dict = fileParser.read_input_file(file_path,verbose=True)

    timeing_mode = args.t

    return file_dict, timeing_mode


def ini_parser(file_dict):
    """Developed Ini parser for astro_neo

    Args:
        file_dicts (_type_): _description_
    """

    Inputs_dict = file_dict['Inputs']
    Populations_dict = file_dict['Populations']
    Mutations_dict = file_dict['Mutations']
    Paths_dict = file_dict['Paths']
    Outputs_dict = file_dict['Outputs']


    # Input
    data_dir = Inputs_dict['data_dir']
    data_file = Inputs_dict['data_file']
    bg_file = Inputs_dict['bg_file']
    rsp_file = Inputs_dict['rsp_file']
    output_file = Inputs_dict['output_file']

    # population
    size_population = int(Populations_dict['population'])
    number_of_generation = int(Populations_dict['num_gen'])
    best_sample = int(Populations_dict['best_sample'])
    lucky_few = int(Populations_dict['lucky_few'])
    cR = float(Populations_dict['cr'])

    # Mutations
    chance_of_mutation = int(Mutations_dict['chance_of_mutation'])
    original_chance_of_mutation = int(
        Mutations_dict['original_chance_of_mutation'])
    F_par = float(Mutations_dict['f'])
    mutated_options = int(Mutations_dict['mutated_options'])

    # Paths
    npaths = int(Paths_dict['npaths'])
    fits = Paths_dict['fits']
    center = helper.str_to_list(Paths_dict['center'])


    # Output
    printgraph = helper.str_to_bool(Outputs_dict['print_graph'])
    num_output_paths = helper.str_to_bool(Outputs_dict['num_output_paths'])
    try:
        steady_state = helper.str_to_bool(Outputs_dict['steady_state'])
    except KeyError:
        steady_state = False

    try:
        distributed = int(Outputs_dict['distributed'])
    except KeyError:
        distributed = 1

    try:
        profile = helper.str_to_bool(Outputs_dict['profile'])
    except KeyError:
        profile = False

    clean_dict = {
        'data_dir': data_dir,
        'data_file':data_file,
        'bg_file':bg_file,
        'rsp_file':rsp_file,
        'output_file':output_file,
        'size_population':size_population,
        'number_of_generation':number_of_generation,
        'best_sample':best_sample,
        'lucky_few':lucky_few,
        'chance_of_mutation':chance_of_mutation,
        'original_chance_of_mutation':original_chance_of_mutation,
        'mutated_options':mutated_options,
        'F': F_par,
        'CR': cR,
        'npaths':npaths,
        'fits':fits,
        'center':center,
        'printgraph':printgraph,
        'num_output_paths':num_output_paths,
        'steady_state':steady_state,
        'distributed':distributed,
        'profile':profile
    }

    return clean_dict
