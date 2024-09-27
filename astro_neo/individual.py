import sys

from attr import define

from astro_neo.pathObj import XspecSpectrum, NgcPar


def shape_function_parser(shape_fit, *args):
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


@define(kw_only=True, slots=True)
class Individual:
    """

    """
    npaths: int = None
    fits: str = ""
    model: object = None

    def __attrs_post_init__(self):
        """
        post Init to determine the value
        :return:
        """
        self.model = shape_function_parser(self.fits)
        if self.model == 'Invalid':
            print("Invalid Fits selection: " + str(self.fits))
            sys.exit()

    def get_model(self):
        """
        Get the desired func back from xspec

        :return:
        """

        return self.model

    def set_single_pars(self, par: str):
        self.model.set_par()

    def mutate_individual(self):
        pass

    def get_bound(self):
        pass

    def get_pars_bounds(self, pars):
        pass


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
