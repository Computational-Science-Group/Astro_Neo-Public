import os

from astro_neo.helper import banner
from astro_neo.ini_parser import validate_input_file
from astro_neo.neo_mutator import NeoMutator
from astro_neo.neo_crossover import NeoCrossover
from astro_neo.neo_pars import NeoPars
from astro_neo.neo_pops import NeoPopulations
from astro_neo.neo_result import NeoResult
from astro_neo.neo_selector import NeoSelector
from astro_neo.neo_solver import NeoSolver
from astro_neo.parser import InputParamsParser
from astro_neo.utils import NeoLogger, STRColors


class AstroNeo:

    def __init__(self, verbose_lvl=5):
        """
        Initialize Params:

        """

        print(banner())
        self.logger = NeoLogger()
        self.neo_pars = NeoPars()
        self.mutator = NeoMutator(logger=self.logger)
        self.selector = NeoSelector(logger=self.logger)
        self.crossover = NeoCrossover(logger=self.logger)
        self.solver = NeoSolver(logger=self.logger)
        self.neo_population = NeoPopulations(logger=self.logger)
        self.verbose_lvl = verbose_lvl
        self.result = NeoResult(logger=self.logger)
        self.input_parameters = None

    def neo_read(self, filepath=None, input_parameters=None):
        """
        Read the input file into exafs parameters
        @param str filepath: file path to the ini file
        @param dict input_parameters: Dictionary of input parameters
        """
        if filepath is not None:
            file_path = os.path.join(os.getcwd(), filepath)
            input_params = InputParamsParser()
            input_params.read_input_file(file_path, verbose=False)
            input_params.input_dict = validate_input_file(input_params.input_dict)

            self.input_parameters = input_params.export_input_dict()

        if input_parameters is not None:
            self.input_parameters = input_parameters

        if self.input_parameters is None:
            raise ValueError("No input parameters are given")

    def neo_setup(self):
        """
        Setup EXAFS run subroutine
        :return:
        """
        self.neo_pars.read_inputs(self.input_parameters)
        self.logger.initialize_logging(self.neo_pars.neoFilePars.log_path)
        self.neo_population.initialize(self.neo_pars)
        self.neo_population.initialize_populations()
        self.result.initialize(self.neo_pars)
        # Initialize all the operators
        self.selector.initialize(self.neo_pars)
        self.crossover.initialize(self.neo_pars)
        self.mutator.initialize(self.neo_pars)
        self.solver.initialize(self.neo_pars)

    def run(self):
        """
        Initialize a EXAFS Run
        :return: result class
        """
        STRColors.run_verbose_start(self.logger, self.neo_pars, verbose_lvl=self.verbose_lvl)

        for currGen in range(self.neo_pars.fixedPars.nGen):
            self.neo_pars.runPars.start_gen()

            self.solver.solve(self.neo_population, self.selector, self.crossover, self.mutator, self.neo_pars)

            # End of generation verbose
            STRColors.run_verbose_gen(self.logger, self.neo_pars, self.neo_population,
                                      verbose_lvl=self.verbose_lvl)
            self.result.collect(self.neo_population, self.neo_pars)

            # self.exafs_neo_pars.runPars.end_gen(self.neo_population)
            self.neo_pars.end_gen(self.neo_population)
        # End of run verbose
        STRColors.run_verbose_end(self.logger, self.neo_pars, verbose_lvl=self.verbose_lvl)
        self.neo_population.shutdown_process_pool()
        return self.result


if __name__ == "__main__":
    initializer_override = {
        'printGraph': False
    }

    astro_neo = AstroNeo(verbose_lvl=5)

    input_dict = {
        'data_dir': '/Users/andy/projects/Astro_Neo/input_files/astronomy_test 2/',
        'data_file': 'left_pha_grp.fits',
        'output_file': 'test_2',
        'bg_file': 'left_mbg.fits',
        'rsp_file': 'left_rmf.fits',
        'nGen': 20,
        'fits': 'XspecSpectrum',
        'solver_type': 2,
        'mut_options': 1,
        'distributed': 6,
        'nPops': 20
    }
    astro_neo.neo_read(input_parameters=input_dict)
    astro_neo.neo_setup()

    result = astro_neo.run()
    print(result)
