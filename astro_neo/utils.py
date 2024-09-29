import datetime
import logging
import pathlib
import sys

import numpy as np

from astro_neo.helper import time_call
from astro_neo.utils_mapping import neocrossover_int2str, neomutator_int2str, neoselector_int2str


def raise_error(msg='Error'):
    raise Exception(msg)


def checkKey(key, dictionary, alt_value=None, logger=None, verbose=False):
    # TODO: Raise checker for alternative response
    if key not in dictionary:
        if verbose:
            warn_str = f'{key} not found! Using default value of {key}: {alt_value}'
            if logger is None:
                print(warn_str)
            else:
                logger.warn(warn_str)
        return alt_value
    else:
        return dictionary[key]


class NeoLogger:
    def __init__(self):
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger('')
        # file_handler = logging.FileHandler()
        if self.logger.hasHandlers():
            self.logger.handlers.clear()
        self.log_path = None
        self.logging_level = logging.DEBUG

    def initialize_logging(self, log_path=None, log_format='%(message)s'):
        self.log_path = log_path
        formatter = logging.Formatter(log_format)

        if log_path is not None:
            file_handler = logging.FileHandler(
                self.log_path, mode='a+', encoding='utf-8')
            file_handler.setFormatter(formatter)
            file_handler.setLevel(self.logging_level)
            self.logger.addHandler(file_handler)

        stdout_handler = logging.StreamHandler(stream=sys.stdout)
        stdout_handler.setLevel(self.logging_level)
        stdout_handler.setFormatter(formatter)
        self.logger.addHandler(stdout_handler)
        self.logger.setLevel(self.logging_level)

    def set_loglevel(self, loglevel):
        # TODO: change each of the handler to the level
        self.logging_level = loglevel
        self.logger.setLevel(loglevel)

    def print(self, message: str):
        self.logger.debug(message)

    def __call__(self, message):
        self.logger.debug(message)


def check_if_exists(path_file):
    """
    Check if the directory exists
    """
    pathFile = pathlib.Path(path_file)
    if pathFile.is_file():
        pathFile.unlink()
    # Make Directory when its missing
    pathFile.parent.mkdir(parents=True, exist_ok=True)


class STRColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    @staticmethod
    def logger_print_based_on_verbose_lvl(logger,
                                          string: str,
                                          current_verbose_lvl: int,
                                          designated_verbose_lvl: int) -> None:
        if current_verbose_lvl >= designated_verbose_lvl:
            logger.print(string)

    # TODO: Implement verbose_lvl argument that detects if jupyter is running...
    @staticmethod
    def run_verbose_start(logger, neo_pars, verbose_lvl=5):
        """
        Visualize the verbose start place
        """
        # logger.print(banner())
        if neo_pars.fixedPars.debug_mode:
            STRColors.logger_print_based_on_verbose_lvl(logger, f"{STRColors.BOLD}DEBUG-MODE{STRColors.ENDC}",
                                                        verbose_lvl, 5)
        STRColors.logger_print_based_on_verbose_lvl(logger, "------------Inputs File Stats--------------",
                                                    verbose_lvl, 5)
        STRColors.logger_print_based_on_verbose_lvl(logger,
                                                    f"{STRColors.BOLD}Data File{STRColors.ENDC}: {neo_pars.neoFilePars.data_path}",
                                                    verbose_lvl, 5)
        STRColors.logger_print_based_on_verbose_lvl(logger,
                                                    f"{STRColors.BOLD}Output File{STRColors.ENDC}: {neo_pars.neoFilePars.output_path}",
                                                    verbose_lvl, 5)
        STRColors.logger_print_based_on_verbose_lvl(logger,
                                                    f"{STRColors.BOLD}Log File{STRColors.ENDC}: {neo_pars.neoFilePars.log_path}",
                                                    verbose_lvl, 5)
        STRColors.logger_print_based_on_verbose_lvl(logger, "--------------Populations------------------",
                                                    verbose_lvl, 5)
        STRColors.logger_print_based_on_verbose_lvl(logger,
                                                    f"{STRColors.BOLD}Population{STRColors.ENDC}: {neo_pars.fixedPars.nPops}",
                                                    verbose_lvl, 5)
        STRColors.logger_print_based_on_verbose_lvl(logger,
                                                    f"{STRColors.BOLD}Num Gen{STRColors.ENDC}: {neo_pars.fixedPars.nGen}",
                                                    verbose_lvl, 5)
        STRColors.logger_print_based_on_verbose_lvl(logger,
                                                    f"{STRColors.BOLD}Best Individuals{STRColors.ENDC}: {neo_pars.selPars.nBestSample}",
                                                    verbose_lvl, 5)
        STRColors.logger_print_based_on_verbose_lvl(logger,
                                                    f"{STRColors.BOLD}Lucky Survivor{STRColors.ENDC}: {neo_pars.selPars.nLuckSample}",
                                                    verbose_lvl, 5)
        STRColors.logger_print_based_on_verbose_lvl(logger, "-----------------Paths---------------------",
                                                    verbose_lvl, 5)
        STRColors.logger_print_based_on_verbose_lvl(logger, "-----------------Solvers-------------------",
                                                    verbose_lvl, 5)
        # STRColors.logger_print_based_on_verbose_lvl(logger,
        #                                             f"{STRColors.BOLD}Solver Options{STRColors.ENDC}: {exafs_NeoPars.mutPars.}",
        #                                             verbose_lvl, 5)
        STRColors.logger_print_based_on_verbose_lvl(logger, "----------------Mutations------------------",
                                                    verbose_lvl, 5)
        STRColors.logger_print_based_on_verbose_lvl(logger,
                                                    f"{STRColors.BOLD}Mutations{STRColors.ENDC}: {neo_pars.mutPars.mutChance}",
                                                    verbose_lvl, 5)
        STRColors.logger_print_based_on_verbose_lvl(logger,
                                                    f"{STRColors.BOLD}Mutation Options{STRColors.ENDC}: {neomutator_int2str(neo_pars.mutPars.mutOpt)}",
                                                    verbose_lvl, 5)
        STRColors.logger_print_based_on_verbose_lvl(logger,
                                                    f"{STRColors.BOLD}Selection Options{STRColors.ENDC}: {neoselector_int2str(neo_pars.selPars.selOpt)}",
                                                    verbose_lvl, 5)
        STRColors.logger_print_based_on_verbose_lvl(logger,
                                                    f"{STRColors.BOLD}Crossover Options{STRColors.ENDC}: {neocrossover_int2str(neo_pars.crossPars.croOpt)}",
                                                    verbose_lvl, 5)
        STRColors.logger_print_based_on_verbose_lvl(logger, "-------------------------------------------", verbose_lvl,
                                                    5)
        STRColors.logger_print_based_on_verbose_lvl(logger,
                                                    f"{STRColors.BOLD}Steady State{STRColors.ENDC}: {neo_pars.fixedPars.steadyState}",
                                                    verbose_lvl, 5)
        STRColors.logger_print_based_on_verbose_lvl(logger,
                                                    f"{STRColors.BOLD}Print Graph{STRColors.ENDC}: {neo_pars.fixedPars.printGraph}",
                                                    verbose_lvl, 5)
        STRColors.logger_print_based_on_verbose_lvl(logger, "-------------------------------------------", verbose_lvl,
                                                    5)

    @staticmethod
    def run_verbose_gen(logger, neo_pars, neo_population, verbose_lvl=5):
        """
        Verbose generation
        """
        st = time_call()
        score_sorted = neo_population.score_sorted
        STRColors.logger_print_based_on_verbose_lvl(logger, "---------------------------------------------------------",
                                                    verbose_lvl, 1)
        STRColors.logger_print_based_on_verbose_lvl(logger, datetime.datetime.fromtimestamp(st).strftime(
            '%H:%M:%S') + f"{STRColors.BOLD} Gen: {STRColors.ENDC}{neo_pars.runPars.currGen}", verbose_lvl, 1)
        STRColors.logger_print_based_on_verbose_lvl(logger,
                                                    f"Best Fit: {STRColors.BOLD}{round(score_sorted[0],3)}{STRColors.ENDC}",
                                                    verbose_lvl, 5)
        STRColors.logger_print_based_on_verbose_lvl(logger,
                                                    f"2nd Fit: {STRColors.BOLD}{round(score_sorted[1],3)}{STRColors.ENDC}",
                                                    verbose_lvl, 5)
        STRColors.logger_print_based_on_verbose_lvl(logger,
                                                    f"3rd Fit: {STRColors.BOLD}{round(score_sorted[2],3)}{STRColors.ENDC}",
                                                    verbose_lvl, 5)
        STRColors.logger_print_based_on_verbose_lvl(logger,
                                                    f"4th Fit: {STRColors.BOLD}{round(score_sorted[3],3)}{STRColors.ENDC}",
                                                    verbose_lvl, 5)
        STRColors.logger_print_based_on_verbose_lvl(logger,
                                                    f"Last Fit: {STRColors.BOLD}{round(score_sorted[-1],3)}{STRColors.ENDC}",
                                                    verbose_lvl, 5)
        STRColors.logger_print_based_on_verbose_lvl(logger,
                                                    f"Different from last best fit: {neo_pars.bestFitPars.bestDiff:.4f}",
                                                    verbose_lvl, 5)
        STRColors.logger_print_based_on_verbose_lvl(logger, STRColors.BOLD + "Best fit: " + STRColors.OKBLUE + str(
            np.round(neo_pars.bestFitPars.currBestVal, 3)) + STRColors.ENDC, verbose_lvl, 5)
        STRColors.logger_print_based_on_verbose_lvl(logger, STRColors.BOLD + "History Best: " + STRColors.OKBLUE + str(
            np.round(neo_pars.bestFitPars.globBestVal, 4)) + STRColors.ENDC, verbose_lvl, 1)
        STRColors.logger_print_based_on_verbose_lvl(logger, "DiffCounter: " + str(neo_pars.runPars.diffCounter),
                                                    verbose_lvl, 5)
        STRColors.logger_print_based_on_verbose_lvl(logger,
                                                    f"Diff %: {(neo_pars.runPars.diffCounter / neo_pars.runPars.currGen):.3f}",
                                                    verbose_lvl, 5)
        STRColors.logger_print_based_on_verbose_lvl(logger,
                                                    f"Mutation Chance: {100 * neo_pars.mutPars.mutChance:.2f}%",
                                                    verbose_lvl, 5)
        # if exafs_NeoPars.mutPars.mutOpt == 4:
        #     STRColors.logger_print_based_on_verbose_lvl(logger, "Mutation Percentage" + str(np.round(exafs_NeoPars.self.nmutate_success / self.nmutate, 4)),verbose_lvl,5)

        STRColors.logger_print_based_on_verbose_lvl(logger,
                                                    "Time: " + str(round(neo_pars.runPars.currGen_tt, 5)) + "s",
                                                    verbose_lvl, 5)

    @staticmethod
    def run_verbose_end(logger, neo_pars, verbose_lvl=5):
        """
        Verbose end
        """

        STRColors.logger_print_based_on_verbose_lvl(logger, "-----------Output Stats---------------", verbose_lvl, 1)
        STRColors.logger_print_based_on_verbose_lvl(logger,
                                                    f"{STRColors.BOLD}Total Time(s){STRColors.ENDC}: {round(neo_pars.runPars.tt, 4)}",
                                                    verbose_lvl, 1)
        STRColors.logger_print_based_on_verbose_lvl(logger,
                                                    f"{STRColors.BOLD}File{STRColors.ENDC}: {neo_pars.neoFilePars.data_path}",
                                                    verbose_lvl, 1)
        STRColors.logger_print_based_on_verbose_lvl(logger,
                                                    f"{STRColors.BOLD}Final Fittness Score{STRColors.ENDC}: {neo_pars.bestFitPars.globBestVal:.2f}",
                                                    verbose_lvl, 1)
        STRColors.logger_print_based_on_verbose_lvl(logger, "-------------------------------------------", verbose_lvl,
                                                    1)
        if neo_pars.fixedPars.printGraph:
            # TODO: Reimplement this
            pass
            # self.verbose_graph()


if __name__ == "__main__":
    # Testing Logger
    logger = NeoLogger()
    logger.initialize_logging('Test.csv')
    logger.set_loglevel(logging.DEBUG)

    # Test Str Print
    pass
