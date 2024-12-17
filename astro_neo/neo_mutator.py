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
                og_score = fitness(og_indi)
                mut_indi = copy.deepcopy(indi)
                mut_indi.mutate_paths(self.mutChance)
                mut_score = fitness(mut_indi)
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
    """Mutator class that uses Differential Evolution (DE) for mutation."""

    def __init__(self, neo_pars, logger):
        """Initializes the mutator with parameters and logger.

        Args:
            neo_pars: Parameters for the mutation process.
            logger: Logger for logging information.
        """
        super().__init__(neo_pars, logger)
        self.mutOpt = 4
        self.mutType = "Mutate DE"

    def mutate(self, pops):
        """Mutates individuals in the population using Differential Evolution.

        Args:
            pops: Population to mutate.

        Returns:
            list: List of mutated populations.
        """
        mutated_Populations = []
        for i, indi in enumerate(pops):
            candidates = [candidate for candidate in range(len(pops)) if candidate != i]
            a, b, c = np.random.choice(candidates, 3, replace=False)
            mutation_vectors = [pops[a], pops[b], pops[c]]
            temp_individual = self._mutate_DE(mutation_vectors, self.neo_pars.mutPars.mutF)
            temp_individual = self._check_for_bound(temp_individual)
            mutated_Populations.append(temp_individual)

        return mutated_Populations
    def _mutate_DE(self, mutation_vectors, F):
        """Performs the mutation operation for Differential Evolution.

        Args:
            mutation_vectors: Vectors used for mutation.
            F: Mutation factor.

        Returns:
            Individual: Mutated individual.
        """

        x_list = np.array(mutation_vectors[0].get_model_params())
        y_list = np.array(mutation_vectors[1].get_model_params())
        z_list = np.array(mutation_vectors[2].get_model_params())

        new_Pars = x_list + F * (y_list - z_list)
        temp_individual = self._generate_individual()
        temp_individual.set_path(new_Pars)
        return temp_individual

    def _generate_individual(self):
        npaths = self.neo_pars.neo_paths.npaths
        this_fits = self.neo_pars.neo_paths.fits[0]
        ind = Individual(npaths=npaths, fits=this_fits)
        return ind

    def _check_for_bound(self, individual):
        """Checks if the mutated individual is within the bounds.

        Args:
            individual: Mutated individual.

        Returns:
            Individual: Mutated individual within bounds.
        """
        pars = individual.get_params()
        bounds = individual.get_bounds()
        temp_pars = []
        for i, (par, value) in enumerate(pars.items()):
            temp_pars.append(np.clip(value, bounds[par][0], bounds[par][1]))

        individual.set_path(temp_pars)
        return individual


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


if __name__ == "__main__":
    individual = Individual(npaths=1, fits="XspecSpectrum")
    mutator = NeoMutatorDE(neo_pars=None, logger=None)
