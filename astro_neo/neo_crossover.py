import numpy as np

from astro_neo.individual import Individual
from astro_neo.neo_pops import NeoPopulations
from astro_neo.neo_pars import NeoPars


class NeoCrossOverBase:
    def __init__(self, neo_pars, logger=None):
        self.logger = logger
        self.neo_pars = neo_pars
        self.croOpt = self.neo_pars.crossPars.croOpt
        self.croType = None

    def crossover(self, pops, individual1, individual2):
        pass

    def __str__(self):
        return f"Crossover Option: {self.croType}"

    def _generate_individual(self):
        npaths = self.neo_pars.neo_paths.npaths
        this_fits = self.neo_pars.neo_paths.fits[0]
        ind = Individual(npaths=npaths, fits=this_fits)
        return ind


class NeoUniCrossOver(NeoCrossOverBase):
    def __init__(self, neo_pars, logger):
        super().__init__(neo_pars, logger)
        self.croOpt = 0
        self.croType = "Uniform Crossover"

    def crossover(self, pops, individual1, individual2):
        child = pops.generate_individual()

        ind1_dict = individual1.get_model().get_func()
        ind2_dict = individual2.get_model().get_func()

        keys = sorted(ind1_dict.keys())
        new_keys_dict = {}
        for key in keys:
            if np.random.randint(0, 2):
                new_keys_dict[key] = ind1_dict[key]
            else:
                new_keys_dict[key] = ind2_dict[key]
        child.set_pars(new_keys_dict)
        return child


class NeoSPCrossOver(NeoCrossOverBase):
    def __init__(self, neo_pars, logger):
        super().__init__(neo_pars, logger)
        self.croOpt = 1
        self.croType = 'Single Point Crossover'

    def crossover(self, pops, individual1, individual2, co_point=1):
        # prevent overflow by clipping to 0 and 3 for the path
        co_point = np.clip(co_point, 0, 3)
        child = pops.generate_individual()

        if np.random.randint(0, 1):
            child.set_e0(individual1.get_e0())
        else:
            child.set_e0(individual2.get_e0())

        for i in range(self.neo_pars.exafsPathPars.npaths):
            individual1_path = individual1.get_path(i)
            individual2_path = individual2.get_path(i)

            temp_path = []
            for j in range(4):
                if j < co_point:
                    temp_path.append(individual1_path[j])
                else:
                    temp_path.append(individual2_path[j])

            child.set_path(i, temp_path[0], temp_path[2], temp_path[3])

        return child


class NeoDPCrossOver(NeoCrossOverBase):
    def __init__(self, neo_pars, logger):
        super().__init__(neo_pars, logger)
        self.croOpt = 2
        self.croType = 'Dual Point Crossover'

    def crossover(self, pops, individual1, individual2):
        pass


class NeoArithmeticCrossOver(NeoCrossOverBase):
    def __init__(self, neo_pars, logger):
        super().__init__(neo_pars, logger)
        self.croOpt = 3
        self.croType = 'Arithmetic Crossover'

    def crossover(self, pops, individual1, individual2):
        child = pops.generate_individual()
        if np.random.randint(0, 1):
            child.set_e0(individual1.get_e0())
        else:
            child.set_e0(individual2.get_e0())

        for i in range(self.neo_pars.exafsPathPars.npaths):
            individual1_path = individual1.get_path(i)
            individual2_path = individual2.get_path(i)

            temp_path = []
            for j in range(4):
                ind_1 = np.random.randint(0, 2)
                ind_2 = np.random.randint(0, 2)
                if np.logical_and(ind_1, ind_2):
                    temp_path.append(individual1_path[j])
                else:
                    temp_path.append(individual2_path[j])

            child.set_path(i, temp_path[0], temp_path[2], temp_path[3])

        return child


class NeoOrCrossOver(NeoCrossOverBase):
    def __init__(self, neo_pars, logger):
        super().__init__(neo_pars, logger)
        self.croOpt = 4
        self.croType = 'Or Crossover'

    def crossover(self, pops, individual1, individual2):
        child = pops.generate_individual()
        if np.random.randint(0, 1):
            child.set_e0(individual1.get_e0())
        else:
            child.set_e0(individual2.get_e0())

        for i in range(self.neo_pars.exafsPathPars.npaths):
            individual1_path = individual1.get_path(i)
            individual2_path = individual2.get_path(i)

            temp_path = []
            for j in range(4):
                ind_1 = np.random.randint(0, 2)
                ind_2 = np.random.randint(0, 2)
                if np.logical_or(ind_1, ind_2):
                    temp_path.append(individual1_path[j])
                else:
                    temp_path.append(individual2_path[j])

            child.set_path(i, temp_path[0], temp_path[2], temp_path[3])

        return child


class NeoAverageCrossOver(NeoCrossOverBase):
    def __init__(self, neo_pars, logger):
        super().__init__(neo_pars, logger)
        self.croOpt = 5
        self.croType = 'Average Crossover'

    def crossover(self, pops, individual1, individual2):
        child = pops.generate_individual()
        if np.random.randint(0, 1):
            child.set_e0(individual1.get_e0())
        else:
            child.set_e0(individual2.get_e0())

        for i in range(self.exafs_pars.exafsPathPars.npaths):
            individual1_path = individual1.get_path(i)
            individual2_path = individual2.get_path(i)

            temp_path = []
            for j in range(4):
                temp_path.append((individual1_path[j] + individual2_path[j]) / 2)

            # TODO check if this values goes out of bound
            child.set_path(i, temp_path[0], temp_path[2], temp_path[3])

        return child


class NeoDECrossOver(NeoCrossOverBase):
    def __init__(self, neo_pars, logger):
        super().__init__(neo_pars, logger)
        self.croOpt = 6
        self.croType = 'DE Crossover'

    def crossover(self, pops: NeoPopulations, **kwargs):
        trial_pops = []
        mut_pops = pops.mut_pops
        curr_pops = pops.population
        for this_mut_pop, this_curr_pop in zip(mut_pops, curr_pops):
            trial_pops.append(self._crossover_DE(this_mut_pop, this_curr_pop, self.neo_pars.crossPars.cR))

    def _crossover_DE(self, mutate_ind, pop_ind, cR: int):
        p = np.random.rand(len(mutate_ind))
        # temp_pars = self.generative
        temp_ind = self._generate_individual()
        mutate_Pars = mutate_ind.get()
        pop_Pars = pop_ind.get()[0]
        temp_Pars = []
        for i in range(len(mutate_ind)):
            if p[i] < cR:
                temp_Pars.append(mutate_Pars[i])
            else:
                temp_Pars.append(pop_Pars[i])

        temp_ind.set_path(temp_Pars)
        return temp_ind


class NeoCrossover:
    def __init__(self, logger=None):
        self.logger = logger
        self.neo_pars = None
        self.crossover_type = None
        self.crossover_operator = None
        self.crossover_score = 0  # TODO: maybe implement this?

    def initialize(self, neo_pars):
        self.neo_pars = neo_pars

        self.crossover_type = neo_pars.crossPars.croOpt
        if self.crossover_type == 0:
            self.crossover_operator = NeoUniCrossOver(neo_pars, logger=self.logger)
        elif self.crossover_type == 1:
            self.crossover_operator = NeoSPCrossOver(neo_pars, logger=self.logger)
        elif self.crossover_type == 2:
            self.crossover_operator = NeoDPCrossOver(neo_pars, logger=self.logger)
        elif self.crossover_type == 3:
            self.crossover_operator = NeoArithmeticCrossOver(neo_pars, logger=self.logger)
        elif self.crossover_type == 4:
            self.crossover_operator = NeoOrCrossOver(neo_pars, logger=self.logger)
        elif self.crossover_type == 5:
            self.crossover_operator = NeoAverageCrossOver(neo_pars, logger=self.logger)
        elif self.crossover_type == 6:
            self.crossover_operator = NeoDECrossOver(neo_pars, logger=self.logger)
        else:
            self.crossover_operator = NeoCrossOverBase(neo_pars, logger=self.logger)
            raise ValueError("Invalid crossover type, returning standard crossover type.")

        return self.crossover_operator

    def __str__(self):
        if self.crossover_operator is None:
            return "Crossover is not selected"
        else:
            return f"Crossover Type: {self.crossover_type}, {self.crossover_operator}"

    def crossover(self, pops):
        if self.crossover_operator is None:
            raise ValueError("Crossover is not initialized")
        else:
            temp_population = []
            if self.crossover_type != 6:
                if len(pops.next_population) > 2:
                    for _ in range(self.neo_pars.selPars.nCross):
                        par_ind = np.random.choice(len(pops.next_population), size=2, replace=False)
                        ind1 = pops.next_population[par_ind[0]]
                        ind2 = pops.next_population[par_ind[1]]
                        child = self.crossover_operator.crossover(pops, ind1)
                        temp_population.append(child)

                    pops.next_population.extend(temp_population)
                    pops.population = pops.next_population
            else:
                # DE
                self.crossover_operator.crossover(pops)
                return

    def crossover_single(self, pops, ind1, ind2):
        if self.crossover_operator is None:
            raise ValueError("Crossover is not initialized")
        else:
            return self.crossover_operator.crossover(pops, ind1)


if __name__ == "__main__":
    # inputs_pars = {'data_file': '../path_files/Cu/cu_10k.xmu', 'output_file': '',
    #                'feff_file': '../path_files/Cu/path_75/feff', 'kmin': 0.95,
    #                'kmax': 9.775,
    #                'kweight': 3.0, 'pathrange': [1, 2, 3, 4, 5],
    #                'deltak': 0.05, 'rbkg': 1.1, 'bkgkw': 1.0, 'bkgkmax': 15.0,
    #                'mut_options': 1,
    #                'croOpt': 1}
    # exafs_Pars = NeoPars()
    # exafs_Pars.read_inputs(inputs_pars)
    #
    # neo_population = NeoPopulations(exafs_Pars)
    # neo_population.initialize_populations()
    # print(neo_population.population[0].get_var())
    #
    # crossover_operator = NeoCrossover()
    # crossover_operator.initialize(exafs_pars=exafs_Pars)
    # crossover_operator.crossover(neo_population)
    # print(crossover_operator)

    individual1 = Individual(npaths=1, fits="XspecSpectrum")
    individual2 = Individual(npaths=1, fits="XspecSpectrum")
    # params_list = [2, 3, 4, 7, 9, 10, 11, 12, 13, 19, 22, 23, 38, 41, 60]
    # print(individual.get_model().get_pars_dicts(params_list))
    ind1_dict = individual1.get_model().get_func()
    ind2_dict = individual2.get_model().get_func()
    print(ind1_dict)
    print(ind2_dict)
