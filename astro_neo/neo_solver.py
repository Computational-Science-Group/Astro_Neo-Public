import numpy as np

from astro_neo.neo_pops import NeoPopulations
from astro_neo.neo_pars import NeoPars


class NeoSolverBase:
    def __init__(self, exafs_pars, logger):
        """
        Initialize the selector base class
        :param exafs_pars:
        :param logger:
        """
        self.logger = logger
        self.exafs_pars = exafs_pars

        self.sol_list = []

    def solve(self, pops, selector, crossover, mutator, exafs_pars):
        pass

    def __str__(self):
        # return f"Top Percentage: {100 * self.nBest_Percent}%, Lucky: {100 * self.nLucky_Percent}%"
        return f"Neo Solver"


class NeoSolver_GA(NeoSolverBase):
    """
    Standard GA algorithm solver
    """

    def __init__(self, exafs_pars, logger):
        super().__init__(exafs_pars, logger)
        self.solver_type = 0
        self.solver_operator = "Genetic Algorithm"

    def solve(self, pops, selector, crossover, mutator, exafs_pars):
        selector.select(pops)
        crossover.crossover(pops, )
        mutator.mutate(pops)
        pops.eval_population()


class NeoSolverGARechenberg(NeoSolverBase):
    """
    Standard GA with Rechenberg addition
    """

    def __init__(self, exafs_pars, logger):
        super().__init__(exafs_pars, logger)
        self.solver_type = 1
        self.solver_operator = "Genetic Algorithm with Rechenberg"

    def solve(self, pops, selector, crossover, mutator, exafs_pars):
        selector.select(pops)
        crossover.crossover(pops, )
        self.rechenberg_mutation(exafs_pars)
        mutator.mutate(pops)
        pops.eval_population()

    def rechenberg_mutation(self, exafs_pars):
        # Recehenberg mutation
        diffCounter = exafs_pars.runPars.diffCounter
        if exafs_pars.runPars.currGen > 20:
            if diffCounter < 0.1:
                diffCounter += 1
            else:
                diffCounter -= 1

            if (abs(diffCounter) / float(exafs_pars.runPars.currGen)) > 0.2:
                exafs_pars.mutPars.mutChance += 0.025
                exafs_pars.mutPars.mutChance = abs(exafs_pars.mutPars.mutChance)
            elif (abs(diffCounter) / float(exafs_pars.runPars.currGen)) < 0.2:
                if (exafs_pars.mutPars.mutChance - 0.025) > 0:
                    exafs_pars.mutPars.mutChance -= 0.025
                    exafs_pars.mutPars.mutChance = abs(exafs_pars.mutPars.mutChance)

            # Clip between 0 and 100%
            exafs_pars.mutPars.mutChance = np.clip(exafs_pars.mutPars.mutChance, 0, 100)


class NeoSolverDE(NeoSolverBase):
    """
    Standard Differential Evolution
    """

    def __init__(self, exafs_pars, logger):
        super().__init__(exafs_pars, logger)
        self.solver_type = 2
        self.solver_operator = "Differential Evolution"

    def solve(self, pops, selector, crossover, mutator, exafs_pars):
        selector.select(pops)
        mutated_pops = mutator.mutate(pops)
        crossover.crossover(mutated_pops, pops)
        pops.eval_population()


class NeoSolverDEClustering(NeoSolverBase):
    """
    Differential Evolution with Clustering
    """

    def __init__(self, exafs_pars, logger):
        super().__init__(exafs_pars, logger)
        self.solver_type = 3
        self.solver_operator = "Differential Evolution with Clustering"

    def solve(self, pops, selector, crossover, mutator, exafs_pars):
        pass


class NeoSolver:

    def __init__(self, logger=None):
        """
        Neo Selector
        :param NeoLogger logger: logger for Neo
        """
        self.solver_operator = None
        self.logger = logger
        self.solver_type = None
        self.neo_pars = None

    def initialize(self, neo_pars):
        """
        Initialize the Selector
        :param neo_pars:
        :return:
        """
        self.neo_pars = neo_pars
        # self.solver_type = exafs_pars.selPars.selOpt
        self.solver_type = neo_pars.solPars.solOpt
        if self.solver_type == 0:
            self.solver_operator = NeoSolver_GA(neo_pars, logger=self.logger)
        elif self.solver_type == 1:
            self.solver_operator = NeoSolverGARechenberg(neo_pars, logger=self.logger)
        elif self.solver_type == 2:
            self.solver_operator = NeoSolverDE(neo_pars, logger=self.logger)
        else:
            self.solver_operator = NeoSolverBase(neo_pars, logger=self.logger)
            raise ValueError("Invalid selector type, returning standard selector type.")

    def solve(self, pops, selector, crossover, mutator, neo_pars):
        """
        Perform the actual selection
        :param neo_pars:
        :param selector:
        :param mutator:
        :param crossover:
        :param NeoPopulation pops:
        :return:
        """
        if self.solver_operator is None:
            raise ValueError("Solver is not initialized")
        else:
            return self.solver_operator.solve(pops, selector, crossover, mutator, neo_pars)

    def __str__(self):
        if self.solver_operator is None:
            return "None Mutator selected"
        else:
            return f"Selector Type: {self.solver_type}, {self.solver_operator}"


if __name__ == "__main__":
    inputs_pars = {'data_file': '../path_files/Cu/cu_10k.xmu', 'output_file': '',
                   'npath': 1, 'fits': ['XspecSpectrum'], 'center': [8.422],
                   'solver_type': 1}
    neoPars = NeoPars()
    neoPars.read_inputs(inputs_pars)

    neo_population = NeoPopulations(neo_pars=neoPars)
    neo_population.initialize_populations()

    exafs_solver = NeoSolver()
    exafs_solver.initialize(neo_pars=neoPars)
    # exafs_selector.solve(neo_population)
    print(exafs_solver)
