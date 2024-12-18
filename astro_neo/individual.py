import sys

from attr import define

from astro_neo.pathObj import XspecSpectrum, NgcPar, BaseObj


def shape_function_parser(shape_fit, *args):
    if isinstance(shape_fit, list):
        shape_fit = shape_fit[0]
    switch = {
        "XspecSpectrum": XspecSpectrum(*args),
        "NGC_Test": NgcPar(*args),
        # "Sherpa_APEC_BG": Sherpa_APEC_BG()
    }
    return switch.get(shape_fit, "Invalid")


class BackgroundObj:
    # TODO: Need to rebuild this function
    def __init__(self, nfuncs, fits, center):
        self.nfuncs = nfuncs
        self.fits = fits
        self.Population = [None] * self.nfuncs

        for i in range(nfuncs):
            obj = shape_function_parser(self.fits[i], center[i])
            if obj == 'Invalid':
                print("Invalid Fits selection")
                sys.exit()
            self.Population[i] = obj

    def get_func(self, x, y):
        for i in range(self.nfuncs):
            background = self.Population[i].get_func(x, y)

        return y


@define(kw_only=True)
class Individual:
    """

    """
    npaths: int = None
    fits: str = ""
    model: BaseObj = None

    def __attrs_post_init__(self):
        """
        post Init to determine the value
        :return:
        """
        self.model = shape_function_parser(self.fits)
        if self.model == 'Invalid':
            print("Invalid Fits selection: " + str(self.fits))
            sys.exit()

    def get_model_params(self):
        """
        Get the desired func back from xspec

        :return:
        """

        return self.model.get()

    def set_pars(self, pars: dict):
        self.model.set(pars)

    def mutate(self):
        self.model.mutate()

    def get_params(self):
        return self.model.get_params()

    def get_bounds(self):
        return self.model.get_bounds()

    def get_pars_bounds(self, pars):
        pass

    def set_path(self, params: list):
        params_names = self.model.get_params_names()
        dicts = {}
        for j, key in enumerate(params_names):
            dicts[key] = params[j]
        self.model.set(dicts)

    def __len__(self):
        return len(self.model)


class Old_Individual:
    def __init__(self, npaths, fits, center):
        """_summary_

        Args:
            npaths (_type_): _description_
            fits (_type_): _description_
            center (_type_): _description_
        """
        self.npaths = npaths
        self.population = [None] * self.npaths
        self.center = center
        self.fits = fits

        for i in range(self.npaths):

            obj = shape_function_parser(self.fits[i], self.center[i])
            if obj == 'Invalid':
                print("Invalid Fits selection: " + str(self.fits[i]))
                sys.exit()
            self.population[i] = obj

    def get(self):
        population = []
        for i in range(self.npaths):
            population.append(self.population[i].get())
        return population

    def get_func(self):
        population = []
        for i in range(self.npaths):
            population.append(self.population[i])
        return population

    def get_path(self, i):
        return self.population[i].get()

    def set_path(self, i: int, params: list):
        params_names = self.population[i].get_params_names()
        dicts = {}
        for j, key in enumerate(params_names):
            dicts[key] = params[j]

        self.population[i].set(dicts)

    def mutate(self):
        for i in range(self.npaths):
            # self.Population[i].mutate()
            params_names = self.population[i].mutate()

    def get_bounds(self, i: int) -> tuple:
        """Get the bounds of the individual

        Args:
            i (int): integer of the path to get bounds

        Returns:
            tuple: bounds of the individual
        """

        return self.population[i].get_bounds()

    def __len__(self):
        return len(self.population[0])


if __name__ == "__main__":
    individual = Individual(npaths=1, fits="XspecSpectrum")
    # print(len(individual))
    print(individual.get_model_params())
    print(individual.model.get_params_names())
    # params_list = [2, 3, 4, 7, 9, 10, 11, 12, 13, 19, 22, 23, 38, 41, 60]
    # print(individual.get_model().get_pars_dicts(params_list))
    # print(individual.get_model().get_func())
