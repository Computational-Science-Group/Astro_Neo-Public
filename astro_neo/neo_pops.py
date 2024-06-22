import copy
import operator

import numpy as np
from attrs import define, field

from astro_neo.fitness import fitness
from astro_neo.individual import Individual
from astro_neo.neo_pars import NeoPars


#
# def fitness(astro_pars, astro_obj, return_tot=False):
#     """
#     Evaluate fitness of a individual
#     """
#     loss = 0
#     y_total = np.zeros(401)
#     intervalK = astro_pars.exafsPars.intervalK
#     larch = astro_pars.exafsPathPars.mylarch
#     kweight = astro_pars.exafsPars.kweight
#     for i in range(astro_pars.exafsPars.npath):
#         pathname = astro_pars.exafsPathPars.pathname[i]
#         pathdictionary = astro_pars.exafsPathPars.pathDictionary
#         path = pathdictionary.get(pathname)
#         path.e0 = astro_obj.get_e0()
#         path.s02 = astro_obj.get_path(i)[0]
#         path.sigma2 = astro_obj.get_path(i)[2]
#         path.deltar = astro_obj.get_path(i)[3]
#         y = path.chi
#         for k in intervalK:
#             y_total[int(k)] += y[int(k)]
#     # compute loss function
#     for j in intervalK:
#         loss = loss + (y_total[int(j)] * astro_pars.exafsPathPars.g.k[int(j)] ** kweight -
#                        astro_pars.exafsPathPars.exp[int(j)] * astro_pars.exafsPathPars.g.k[
#                            int(j)] ** kweight) ** 2
#     if return_tot:
#         return loss, y_total
#     else:
#         return loss


@define
class NeoPopulations:
    neo_pars: NeoPars = None
    population: list = field(factory=list)
    population_sorted: list = field(factory=list)
    population_score: list = field(factory=list)
    population_perf: dict = field(factory=dict)
    next_population: list = field(factory=list)

    def generate_individual(self):
        npaths = self.neo_pars.neo_paths.npath
        fits = self.neo_pars.neo_paths.fits
        center = self.neo_pars.neo_paths.center
        ind = Individual(npaths, fits, center)
        return ind

    def eval_population(self, replace=True, sorting=True):
        score = []
        population_perf = {}

        for i, individual in enumerate(self.population):
            temp_score = fitness(self.neo_pars, individual)
            score.append(temp_score)

            population_perf[individual] = temp_score
        if sorting:
            self.population_sorted = sorted(
                population_perf.items(), key=operator.itemgetter(1), reverse=False)
        if replace:
            # self.currBestFit = list(self.population_sorted[0])
            self.__replace_bestfit()
        return score

    def initialize_populations(self):
        """
        Initialize populations
        :return:
        """
        for i in range(self.neo_pars.fixedPars.nPops):
            self.population.append(self.generate_individual())

        self.eval_population()

    def __getitem__(self, item):
        return self.population_sorted[item]

    def __replace_bestfit(self):
        self.neo_pars.bestFitPars.currBestInd = self.population_sorted[0][0]
        self.neo_pars.bestFitPars.currBestVal = self.population_sorted[0][1]

        delta = np.abs(self.neo_pars.bestFitPars.currBestVal - self.neo_pars.bestFitPars.globBestVal)
        if delta > 0.01:
            self.neo_pars.bestFitPars.bestDiff = delta
        else:
            self.neo_pars.bestFitPars.bestDiff = 0

        if self.neo_pars.bestFitPars.currBestVal < self.neo_pars.bestFitPars.globBestVal:
            self.neo_pars.bestFitPars.globBestInd = self.neo_pars.bestFitPars.currBestInd
            self.neo_pars.bestFitPars.globBestVal = self.neo_pars.bestFitPars.currBestVal


if __name__ == "__main__":
    inputs_pars = {'data_file': '../path_files/Cu/cu_10k.xmu', 'output_file': '',
                   'feff_file': '../path_files/Cu/path_75/feff', 'kmin': 0.95,
                   'kmax': 9.775,
                   'kweight': 3.0, 'pathrange': [1, 2, 3, 4, 5],
                   'deltak': 0.05, 'rbkg': 1.1, 'bkgkw': 1.0, 'bkgkmax': 15.0}
    neo_pars = NeoPars()
    # neo_pars.read_inputs(inputs_pars)
    # neo_population = NeoPopulations(neo_pars)

    # neo_population.initialize_populations()
