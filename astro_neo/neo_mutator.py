# mutator:
import copy

import numpy as np
from astro_neo.individual import Individual
from astro_neo.fitness import fitness

class NeoMutatorBase:
    """Base class for mutator class in astro_neo.
  """

    def __init__(self, neo_pars, logger):
        self.logger = logger
        self.neo_pars = neo_pars
        self.mutOpt = self.neo_pars.mutPars.mutOpt
        self.mutChance = self.neo_pars.mutPars.mutChance
        self.mutChanceE0 = self.neo_pars.mutPars.mutChanceE0
        self.mutType = None

    def mutate(self, pops):
        pass

    def __str__(self):
        return f"mutation chance: {self.mutChance}%, mutation chance E0: {self.mutChanceE0}%"


class NeoMutatorPerIndividual(NeoMutatorBase):
    def __init__(self, neo_pars, logger):
        super().__init__(neo_pars, logger)
        self.mutOpt = 1
        self.mutType = "Mutate Per Individual"

    def mutate(self, pops):
        for i, _ in enumerate(pops.population):
            if np.random.random() < self.mutChance:
                new_ind = pops.generate_individual()
                pops.population[i] = new_ind
                self.neo_pars.mutPars.nmut += 1


class NeoMutatorPerPars(NeoMutatorBase):
    def __init__(self, neo_pars, logger):
        super().__init__(neo_pars, logger)
        self.mutOpt = 2
        self.mutType = "Mutate Per Parameters"

    def mutate(self, pops):
        # for i, pop in enumerate(pops.population):
        #     for j, trait in enumerate(pop):
        #         if np.random.random() < self.mutChance:
        #             pops.population[i].mutate_pars(self.mutChance)
        for i, individual in enumerate(pops.population):
            if np.random.random() < self.mutChance:
                individual.mutate()

class NeoMutatorMetropolis(NeoMutatorBase):
    def __init__(self, neo_pars, logger):
        super().__init__(neo_pars, logger)
        self.mutOpt = 3
        self.mutType = "Mutate Metropolis"

    def mutate(self, pops):
        for i, indi in enumerate(pops.population):
            if np.random.random() < self.mutChance:
                nmutate_success = 0

                og_indi = copy.deepcopy(indi)
                og_score = fitness(self.neo_pars, og_indi)
                mut_indi = copy.deepcopy(indi)
                mut_indi.mutate_paths(self.mutChance)
                mut_score = fitness(self.neo_pars, mut_indi)
                # T = - self.bestDiff / np.log(1 - (self.genNum / self.ngen))
                T = - self.neo_pars.bestFitPars.bestDiff / np.log(
                    1 - (self.neo_pars.runPars.currGen / self.neo_pars.fixedPars.nGen))
                if mut_score < og_score:
                    nmutate_success += 1
                    newIndi = mut_indi
                elif np.exp(-(mut_score - og_score) / T) > np.random.uniform():
                    nmutate_success += 1
                    newIndi = mut_indi
                else:
                    newIndi = og_indi

                pops.population[i] = newIndi


class NeoMutatorDE(NeoMutatorBase):
    def __init__(self, neo_pars, logger):
        super().__init__(neo_pars, logger)
        self.mutOpt = 4
        self.mutType = "Mutate DE"

    def mutate(self, pops) -> list:
        pass


class NeoMutator:
    def __init__(self, logger=None):
        self.mutator = None
        self.logger = logger
        self.mutator_type = None
        self.neo_pars = None
        self.mutator_score = 0  # TODO: need to check if this is needed

    def initialize(self, neo_pars):
        self.neo_pars = neo_pars

        self.mutator_type = neo_pars.mutPars.mutOpt
        if self.mutator_type == 0:
            self.mutator = NeoMutatorPerIndividual(self.neo_pars, logger=self.logger)
        elif self.mutator_type == 1:
            self.mutator = NeoMutatorPerPars(self.neo_pars, logger=self.logger)
        elif self.mutator_type == 2:
            self.mutator = NeoMutatorMetropolis(self.neo_pars, logger=self.logger)
        elif self.mutator_type == 3:
            pass
        elif self.mutator_type == 4:
            self.mutator = NeoMutatorDE(self.neo_pars, logger=self.logger)
        else:
            self.mutator = NeoMutatorBase(self.neo_pars, logger=self.logger)
            raise ValueError("Invalid mutator type")

        return self.mutator

    def __str__(self):
        if self.mutator is None:
            return "None Mutator selected"
        else:
            return f"Mutator Type: {self.mutator.mutType}, {self.mutator}"

    def mutate(self, pops):
        if self.mutator is None:
            raise ValueError("Mutator is not initialized")
        else:
            self.mutator.mutate(pops)


class Mutator:
    """Mutator class for astro_neo.
  """

    def __init__(self, mutate_type) -> None:
        self.mutate_type = mutate_type

    def mutate_type_selector(self):
        pass

    def mutate(self, Individuals: list, temp_Individual: Individual, F: float):
        """_summary_

    Args:
        individual (_type_): _description_
        F (_type_): _description_
    """
        length = len(Individuals[0])
        assert all(len(lst) == length for lst in Individuals)

    def mutate_1(self, individuals: list, temp_Individual: Individual, F: float):
        """_summary_

    Args:
        individuals (list): _description_
        temp_Individual (individual.Individual): _description_
        F (float): _description_

    Returns:
        _type_: _description_
    """

        length = len(individuals[0])

        assert all(len(lst) == length for lst in individuals)
        r1_list = np.array(individuals[0].get())[0]
        r2_list = np.array(individuals[1].get())[0]
        r3_list = np.array(individuals[2].get())[0]

        new_Pars = r1_list + F * (r2_list - r3_list)

        temp_Individual.set_path(0, new_Pars)

        return temp_Individual

    def mutate_2(self, individuals: list, temp_Individual: Individual, F: float):
        """_summary_

    Args:
        individuals (list): _description_
        temp_Individual (individual.Individual): _description_
        F (float): _description_
    """


if __name__ == "__main__":
    center = [0]
    x = Individual(1, ['XspecSpectrum'], center)
