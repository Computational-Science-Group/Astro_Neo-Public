import operator

import numpy as np
from attrs import define, field
from loky import ProcessPoolExecutor

from astro_neo.fitness import fitness, init_process, temp_worker_function
from astro_neo.individual import Individual
from astro_neo.neo_pars import NeoPars
from astro_neo.utils import NeoLogger


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


@define(kw_only=True, slots=True)
class NeoPopulations:
    neo_pars: NeoPars = None
    population: list = field(factory=list)
    population_sorted: list = field(factory=list)
    population_score: list = field(factory=list)
    population_perf: dict = field(factory=dict)
    next_population: list = field(factory=list)
    num_distributed: int = None
    processPool: ProcessPoolExecutor = None
    num_pops: int = None
    logger: NeoLogger = None

    def initialize(self, neo_pars: NeoPars):
        self.neo_pars = neo_pars
        self.num_pops = neo_pars.fixedPars.nPops
        self.num_distributed = neo_pars.fixedPars.distributed
        self.initialize_process_pool(self.num_distributed)

    def generate_individual(self):
        npaths = self.neo_pars.neo_paths.npaths
        this_fits = self.neo_pars.neo_paths.fits
        # center = self.neo_pars.neo_paths.center
        # model = self.neo_pars.neo_paths.
        # print(npaths)
        # print(this_fits)
        ind = Individual(npaths=npaths, fits=this_fits)
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
            self.__replace_bestfit()
        return score

    def initialize_process_pool(self, num_distributed):
        if num_distributed > 1:
            file_pars = self.neo_pars.neoFilePars
            data_pack = (
                str(file_pars.data_dir), str(file_pars.data_file), str(file_pars.bg_file), str(file_pars.rsp_file))
            self.processPool = ProcessPoolExecutor(num_distributed, initializer=init_process,
                                                   initargs=(data_pack,))

        # self.processPool.submit(worker_function, [0, 1])

    def test_process_pool(self):
        """
        Test method for process pool ..., not used in production
        :return:
        """
        data = list(self.processPool.map(temp_worker_function, np.arange(16)))
        print(data)

    def initialize_populations(self):
        """
        Initialize populations
        :return:
        """
        for i in range(self.num_pops):
            self.population.append(self.generate_individual())

        # temporally stopping eval first...
        # self.eval_population()

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

    def shutdown_process_pool(self):
        if self.num_distributed > 1:
            self.processPool.shutdown()


if __name__ == "__main__":
    # /Users/andy/projects/Astro_Neo/input_files/astronomy_test 2/left_pha_grp.fits
    inputs_pars = {'data_dir': '/Users/andy/projects/Astro_Neo/input_files/astronomy_test 2/',
                   'data_file': 'left_pha_grp.fits',
                   'output_file': 'test',
                   'bg_file': 'left_mbg.fits', 'rsp_file': 'left_rmf.fits',
                   'npath': 1, 'fits': 'NGC_Test', 'center': [8.422],
                   'solver_type': 1, 'distributed': 4}
    neo_pars = NeoPars()
    neo_pars.read_inputs(inputs_pars)
    neo_population = NeoPopulations()

    neo_population.initialize(neo_pars=neo_pars)
    neo_population.test_process_pool()
    neo_population.initialize_populations()

    # neo_population.eval_population()

    neo_population.shutdown_process_pool()
