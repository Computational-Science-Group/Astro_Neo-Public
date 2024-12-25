import numpy as np
from sklearn.cluster import KMeans

from astro_neo.neo_pops import NeoPopulations
from astro_neo.neo_pars import NeoPars


class NeoSolverGABase:
    def __init__(self, neo_pars, logger):
        """
        Initialize the selector base class
        :param neo_pars:
        :param logger:
        """
        self.logger = logger
        self.neo_pars = neo_pars

        self.sol_list = []

    def solve(self, pops, selector, crossover, mutator, exafs_pars):
        pass

    def __str__(self):
        # return f"Top Percentage: {100 * self.nBest_Percent}%, Lucky: {100 * self.nLucky_Percent}%"
        return f"Neo Solver GA"


class NeoSolverGA(NeoSolverGABase):
    """
    Standard GA algorithm solver
    """

    def __init__(self, neo_pars, logger):
        super().__init__(neo_pars, logger)
        self.solver_type = 0
        self.solver_operator = "Genetic Algorithm"

    def solve(self, pops, selector, crossover, mutator, exafs_pars):
        selector.select(pops)
        crossover.crossover(pops)
        mutator.mutate(pops)
        pops.eval_population()


class NeoSolverGARechenberg(NeoSolverGABase):
    """
    Standard GA with Rechenberg addition
    """

    def __init__(self, neo_pars, logger):
        super().__init__(neo_pars, logger)
        self.solver_type = 1
        self.solver_operator = "Genetic Algorithm with Rechenberg"

    def solve(self, pops, selector, crossover, mutator, exafs_pars):
        selector.select(pops)
        crossover.crossover(pops, )
        self._rechenberg_mutation(exafs_pars)
        mutator.mutate(pops)
        pops.eval_population()

    def _rechenberg_mutation(self, exafs_pars):
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


class NeoSolverDEBase:
    def __init__(self, neo_pars, logger):
        """
        Initialize the selector base class
        :param neo_pars:
        :param logger:
        """
        self.logger = logger
        self.neo_pars = neo_pars

        self.sol_list = []

    def solve(self, pops, selector, crossover, mutator, exafs_pars):
        pass

    def __str__(self):
        # return f"Top Percentage: {100 * self.nBest_Percent}%, Lucky: {100 * self.nLucky_Percent}%"
        return f"Neo Solver DE"


class NeoSolverDE(NeoSolverDEBase):
    """
    Standard Differential Evolution
    """

    def __init__(self, neo_pars, logger):
        super().__init__(neo_pars, logger)
        self.solver_type = 2
        self.solver_operator = "Differential Evolution"

    def solve(self, pops, selector, crossover, mutator, neo_pars):

        # print(crossover)
        # print(crossover.crossover)

        # print("This is before selector")

        selector.select(pops)
        # print("This is before mutator")
        mutator.mutate(pops)
        # print("This is before crossover")
        crossover.crossover(pops)
        # print("This is before eval")
        self._adjust_de_parameters()
        pops.eval_population_compared()

    def _adjust_de_parameters(self):
        """Adjust the DE parameters
        """
        # self.F =
        rand_val = np.random.rand(4)
        tau_1 = 0.1
        tau_2 = 0.1
        if rand_val[1] < tau_1:
            F = 0.1 + rand_val[0] * 0.9
            self.neo_pars.mutPars.mutF = F

            self.logger.print(f"F has been adjusted to {np.round(F, 4)}")

        if rand_val[3] < tau_2:
            cR = rand_val[2]
            self.neo_pars.crossPars.cR = cR
            self.logger.print(f"Cr has been adjusted to {np.round(cR, 4)}")


class NeoSolverDEClustering(NeoSolverDEBase):
    """
    Differential Evolution with Clustering
    """

    def __init__(self, neo_pars, logger):
        super().__init__(neo_pars, logger)
        self.solver_type = 3
        self.solver_operator = "Differential Evolution with Clustering"

    def solve(self, pops, selector, crossover, mutator, neo_pars):

        selector.select(pops)
        # print("This is before mutator")
        mutator.mutate(pops)
        # print("This is before crossover")
        crossover.crossover(pops)
        # print("This is before eval")
        self._adjust_de_parameters()
        pops.eval_population_compared()
        self._cluster_generation(pops)

    def _cluster_generation(self,pops, num_cluster_factors=4):
        num_cluster = num_cluster_factors * pops.population[0].model.get_indept()

        # Create a matrix of the data with [samples, features]
        combined_pars = np.zeros((100, 15))
        for i, individual in enumerate(pops):
            combined_pars[i, :] = individual.get_model_params()
        # Perform cluster
        kmeans = KMeans(n_clusters=num_cluster, n_init=10, random_state=42)
        kmeans.fit(combined_pars)

        c_kmeans = kmeans.predict(combined_pars)
        centers = kmeans.cluster_centers_
        clabels = c_kmeans

        # c_kmeans = kmeans.predict(X)
        centers = kmeans.cluster_centers_
        # clabels = c_kmeans

        # Testing - find num_replace lowest fitness values for generation

        # idx = np.argpartition(gen_function_value, num_replace)
        # idx = idx[:num_replace]

        # Find worst vector and replace with center

        # max_value = np.amax(gen_function_value)
        # resultm = np.where(gen_function_value == np.amax(gen_function_value))
        # resultm = resultm[0][0]  # index integer

        # Find minimum center value

        # center_function_value = test_function_evaluation(centers.T, d)
        # center_result = np.where(center_function_value == np.amin(center_function_value))
        # center_result = center_result[0][0]  # index integer

        # Testing - find k highest fitness values for centers

        # center_function_value = test_function_evaluation(centers.T, d)
        # cidx = np.argpartition(center_function_value, num_replace)
        # cidx = cidx[:num_replace]

        # gen worst index, center points, center best index

        # return idx, centers, cidx


    def _adjust_de_parameters(self):
        """Adjust the DE parameters
        """
        # self.F =
        rand_val = np.random.rand(4)
        tau_1 = 0.1
        tau_2 = 0.1
        if rand_val[1] < tau_1:
            F = 0.1 + rand_val[0] * 0.9
            self.neo_pars.mutPars.mutF = F

            self.logger.print(f"F has been adjusted to {np.round(F, 4)}")

        if rand_val[3] < tau_2:
            cR = rand_val[2]
            self.neo_pars.crossPars.cR = cR
            self.logger.print(f"Cr has been adjusted to {np.round(cR, 4)}")


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
            self.solver_operator = NeoSolverGA(neo_pars, logger=self.logger)
        elif self.solver_type == 1:
            self.solver_operator = NeoSolverGARechenberg(neo_pars, logger=self.logger)
        elif self.solver_type == 2:
            self.solver_operator = NeoSolverDE(neo_pars, logger=self.logger)
        else:
            self.solver_operator = NeoSolverGABase(neo_pars, logger=self.logger)
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
