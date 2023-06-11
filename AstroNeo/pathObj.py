import numpy as np
import os
from scipy import integrate
from scipy.special import gammaln, wofz
import xspec
# from sherpa.astro.ui import create_model_component, set_par, set_source, get_data, get_fit_plot

# ----
# DEBUG:
##
import sys
"""
Author: Andy Lau
"""

# Setup some default constraints
tiny = 1.0e-15
MAX = 3.40282e+38
MIN = 1.17549e-38
c = 299792.458  # Speed of light in km/s


def not_zero(value):
    """Return value with a minimal absolute size of tiny, preserving the sign.
    This is a helper function to prevent ZeroDivisionError's.
    Parameters
    ----------
    value : scalar
        Value to be ensured not to be zero.
    Returns
    -------
    scalar
        Value ensured not to be zero.
    """
    return float(np.copysign(np.max(tiny, abs(value)), value))


def combine_params(prefix, params):
    out_params = []
    if prefix == '':
        out_params = params
    else:
        for i in params:
            # print(i)
            out_params.append(prefix + "_" + str(i))
    return out_params


def separate_dicts(source_dict, prefixs):
    """
    Separate out dictionary into separete folder based on their prefix
    """
    assert len(prefixs) > 1
    out_dict = {}
    for i in prefixs:
        out_dict[i] = {}
    for i, value in enumerate(source_dict.keys()):
        for j, key in enumerate(out_dict.keys()):
            # print(j)
            val_split = value.split("_")
            # print(key,val_split)
            if key == val_split[0]:
                out_dict[key][val_split[1]] = source_dict[value]

    return out_dict


class ParamsDict:
    def __init__(self, params):
        self.params = params
        self.nparams = len(params)
        self.dicts = {}
        # Initalize the whole dictionary first
        for i in range(self.nparams):
            self.dicts[self.params[i]] = None

    def update_val(self, val, key):
        self.dicts[val] = key

    def set(self, params):
        for i in self.params:
            self.dicts[i] = params[i]

    def get(self):
        return self.dicts

    def initialize_range(self, range_dicts):
        self.range_dicts = range_dicts
        for i in range(self.nparams):
            limits = self.range_dicts[self.params[i]]
            if type(limits) == int or type(limits) == float:
                self.dicts[self.params[i]] = limits
            else:
                try:
                    limits[3]
                except:
                    limits = limits + ('',)

                if limits[3] == 'number':
                    limits_range = np.linspace(limits[0], limits[1], int(limits[2]))
                else:
                    limits_range = np.arange(limits[0], limits[1], limits[2])

                self.dicts[self.params[i]] = np.random.choice(limits_range)

    def random_pars(self, pars):
        """Randomized specific paras

        Args:
            pars (_type_): _description_

        Returns:
            _type_: _description_
        """
        limits = self.range_dicts[pars]
        try:
            limits[3]
        except:
            limits = limits + ('',)
        if limits[3] == 'number':
            limits_range = np.linspace(limits[0], limits[1], int(limits[2]))
        else:
            limits_range = np.arange(limits[0], limits[1], limits[2])

        self.dicts[pars] = np.random.choice(limits_range)

class BaseObj:
    """
    Each Base Objects requires the following methods and var:
    Var:
    # Number of independent variables (ex, gaussian: 3, voigt, 4)
    Methods:

    """

    def __init__(self, center=None, _prefix=''):
        self._prefix = _prefix
        self._indep = 1
        self._params_names = ['None']
        self._indep = 1
        self.range_dicts = {
            'None': (0, 1, 10, 'number')
        }

        self._Params = ParamsDict(self._params_names)
        self._Params.initialize_range(self.range_dicts)

    def set(self, param_dicts):

        self._Params.set(param_dicts)

    def get(self):
        params_list = []
        params = self._Params.get()
        for i in self._params_names:
            params_list.append(params[i])

        return params_list

    def get_indept(self):
        """Return the number of indepedent variable
        :return x: return a list of independent var
        :rtype: list
        """
        return self._indep

    def get_func(self, x, *args):
        """Return the list of value using the model shape function
        :param x: x value
        :type x: int, list, nparray
        :returns: the list of value under the shape function
        :rtype: int, nparray
        """
        return None


    def get_params_names(self):
        """Get the parametes name

        Returns:
            _type_: _description_
        """
        return combine_params(self._prefix, self._params_names)

    def mutate(self):
        self._Params.initialize_range(self.range_dicts)

    # def verbose(self):
    #     return self._params.pretty_print()


class GaussianObj(BaseObj):
    def __init__(self, center=None, amplitude=None, sigma=None, prefix=''):
        self._prefix = prefix
        self._params_names = ['amplitude', 'center', 'sigma']
        self._indep = 3

        self.range_dicts = {
            'amplitude': (0.00, 1.5, 0.001),
            'center': (center, center+1, 0.01),
            'sigma': (0, 1.5, 0.001)
        }

        self._Params = ParamsDict(self._params_names)
        self._Params.initialize_range(self.range_dicts)

    def get_func(self, x, *args):
        """Return the list of value using the model shape function
        :param x: x value
        :type x: int, list, nparray
        :returns: the list of value under the shape function
        :rtype: int, nparray
        """

        Params = self._Params.get()
        amplitude = Params['amplitude']
        center = Params['center']
        sigma = Params['sigma']

        return ((amplitude/(max(tiny, np.sqrt(2*np.pi)*sigma)))
                * np.exp(-(1.0*x-center)**2 / max(tiny, (2*sigma**2))))


class VoigtObj(BaseObj):
    def __init__(self, center=None, amplitude=None, gamma=None, sigma=None, prefix=''):
        self._prefix = prefix
        self._params_names = ['amplitude', 'center', 'gamma', 'sigma']
        self._indep = 4
        self.range_dicts = {
            'amplitude': (0.00, 10, 0.001),
            'sigma': (0.0, 10, 0.001),
            'gamma': (0.0, 10, 0.001),
            'center': (center-1, center+1, 0.01)
        }

        self._Params = ParamsDict(self._params_names)
        self._Params.initialize_range(self.range_dicts)

    def get_func(self, x, *args):
        Params = self._Params.get()
        amplitude = Params['amplitude']
        center = Params['center']
        gamma = Params['gamma']
        sigma = Params['sigma']

        return amplitude*np.real(wofz((x - center + 1j*gamma)/max(tiny, sigma)/np.sqrt(2))) / max(tiny, sigma)\
            / max(tiny, np.sqrt(2*np.pi))


class DoubleVoigtObj(VoigtObj):
    def __init__(self, center=None):
        # voigt function
        self._model1 = VoigtObj(center)
        orbit_split = 5
        self._model2 = VoigtObj(center - orbit_split)

    def get_func(self, x):
        return self._model1.get_func(x) + self._model2.get_func(x)


class DoubleVoigtObj_fix(VoigtObj):
    def __init__(self, center=None):
        # voigt function
        self._model1 = VoigtObj(center)
        orbit_split = 5
        params = self._model1.get()
        # self.Bg_obj = Background_Obj(1,'ShirleyExp')

        self._model2 = VoigtObj(center-orbit_split, amplitude=params[0]/2,
                                gamma=params[2],
                                sigma=params[3])

    def get_func(self, x):
        return self._model1.get_func(x) + self._model2.get_func(x)


class DoniachObj(BaseObj):
    def __init__(self, center=None, amplitude=None, gamma=None, sigma=None, prefix=''):
        self._prefix = prefix
        self._params_names = ['amplitude', 'center', 'gamma', 'sigma']
        self._indep = 4
        # self._model = DoniachModel(['x'])
        self.range_dicts = {
            'amplitude': (0.00, 1.5, 0.001),
            'center': (center-20, center+20, 0.01),
            'sigma': (0, 1.0, 0.001),
            'gamma': (0, 1.5, 0.001)
        }

        self._Params = ParamsDict(self._params_names)
        self._Params.initialize_range(self.range_dicts)

    def get_func(self, x, *args):
        Params = self._Params.get()
        amplitude = Params['amplitude']
        center = Params['center']
        gamma = Params['gamma']
        sigma = Params['sigma']

        arg = (x-center)/max(tiny, sigma)
        gm1 = (1.0 - gamma)
        scale = amplitude/max(tiny, (sigma**gm1))
        return scale*np.cos(np.pi*gamma/2 + gm1*np.arctan(arg))/(1 + arg**2)**(gm1/2)


class DoniachObj_Test(BaseObj):
    def __init__(self, center=None, amplitude=None, gamma=None, sigma=None, prefix=''):
        self._prefix = prefix
        self._params_names = ['amplitude', 'asymmetry', 'center', 'F']
        self._indep = 4
        # self._model = DoniachModel(['x'])
        self.range_dicts = {
            'amplitude': (0.00, 1.5, 0.001),
            'asymmetry': (0.00, 0.5, 0.01),
            'center': (center-20, center+20, 0.01),
            'F': (0, 1.0, 0.001)
        }

        self._Params = ParamsDict(self._params_names)
        self._Params.initialize_range(self.range_dicts)

    def get_func(self, x, *args):
        Params = self._Params.get()
        amplitude = Params['amplitude']
        asymmetry = Params['asymmetry']
        center = Params['center']
        F = Params['F']

        arg = (x-center)/max(tiny, F)
        # gm1 = (1.0 - gamma)
        # scale = amplitude/max(tiny, (sigma**gm1))
        top = np.cos(((np.pi*asymmetry)/2) + (1-asymmetry)*np.arctan(arg))
        bot = (F**2 + (x-center)**2)**((1-asymmetry)/2)

        return amplitude * top/bot

    def calculate_fhwm(self):
        fg = 2*self._params['sigma']*np.sqrt(2*np.log(2))
        fl = 2*self._params['gamma']
        return (fg, fl)


class DoniachObjGauss(DoniachObj, GaussianObj):
    def __init__(self, center=None, prefix=''):
        self._prefix_1 = 'DH'
        self._prefix_2 = 'Gauss'
        self._params_names = ['amplitude', 'center', 'gamma', 'sigma']
        self._params2_names = ['amplitude', 'center', 'sigma']
        self._model1 = DoniachObj(center, prefix=self._prefix_1)
        params = self._model1.get()
        # self._model2 = GaussianObj(center = params[1],
        #                 amplitude=params[0],
        #                 sigma = params[3])
        self._model2 = GaussianObj(center=params[1], prefix=self._prefix_2)

    def set(self, dicts):
        dicts = separate_dicts(dicts, [self._prefix_1, self._prefix_2])
        self._model1.set(dicts[self._prefix_1])
        dicts[self._prefix_2]['center'] = dicts[self._prefix_1]['center']
        self._model2.set(dicts[self._prefix_2])

    def get(self):
        return self._model1.get() + self._model2.get()

    def get_func(self, x, *args):
        # return np.convolve(self._model1.get_func(x),self._model2.get_func(x),'same')
        # return self._model1.get_func(x) +self._model2.get_func(x)

        total = np.convolve(self._model1.get_func(
            x), self._model2.get_func(x), mode='same')
        return total
        # return np.convolve(self._model1)

    def verbose(self):
        self._model1.verbose()
        print("------------------------------------------------")
        self._model2.verbose()
    #
    # def get_indept(self):
    #     return self._model1.get_indept() + self._model2.get_indept()

    def get_params_names(self):
        # print(self._model1.get_params_names())
        return self._model1.get_params_names() + self._model2.get_params_names()


class DoubletDoniachObj(DoniachObj):
    def __init__(self, center=None):
        # voigt function
        self._model1 = DoniachObj(center)
        orbit_split = 5
        params = self._model1.get()

        self._model2 = DoniachObj(center-orbit_split, amplitude=params[0]/2,
                                  gamma=params[2],
                                  sigma=params[3])

    def get_func(self, x):
        return self._model1.get_func(x) + self._model2.get_func(x)


class ExponentialObj(BaseObj):
    def __init__(self, center=None, prefix=''):
        self._prefix = ''
        self._params_names = ['amplitude', 'decay']
        self._indep = 2

        amp_range = np.arange(50, 100, 0.05)
        decay_range = np.arange(0.8, 15, 0.001)
        self.range_dicts = {
            'amplitude': (0.00, 100, 0.05),
            'decay': (0.8, 15, 0.001),
        }

        self._Params = ParamsDict(self._params_names)
        self._Params.initialize_range(self.range_dicts)

    def get_func(self, x, *args):
        Params = self._Params.get()
        amplitude = Params['amplitude']
        decay = Params['decay']

        return amplitude*np.exp(-x/decay)

# Gaussian Lorentization Product Form


class GLPObj(BaseObj):
    def __init__(self, center=None):
        """
        A - 0.1
        center
        m - percentage of gaussian/lorentization
        """
        self._params_names = ['A', 'center', 'm', 'F']
        self._indep = 4

        def func(x, center, A, m, F):
            first_term = A*np.exp(-4*np.log(2)*(1-m)*(x-center)**2/(F**2))
            second_term = 1/(1+4*m*(x-center)**2/(F**2))
            return first_term*second_term
        self._model = Model(func)

        A_range = np.arange(0, 1.5, 0.05)
        m_range = np.arange(0.00, 1.001, 0.001)
        center_range = np.arange(center-0.5, center+0.5, 0.01)
        F_range = np.arange(0.0, 1, 0.01)

        self._model.set_param_hint('A',
                                   vary=True,
                                   expr=None,
                                   value=np.random.choice(A_range))

        self._model.set_param_hint('center',
                                   vary=True,
                                   expr=None,
                                   value=np.random.choice(center_range))

        self._model.set_param_hint('m',
                                   vary=True,
                                   expr=None,
                                   value=np.random.choice(m_range),
                                   min=0.0, max=1.0)

        self._model.set_param_hint('F',
                                   vary=True,
                                   expr=None,
                                   value=np.random.choice(F_range),
                                   min=0.0, max=1.0)

        self._params = self._model.make_params()

# Temp Shirley Exponential Obj


class ShirleyExpObj(BaseObj):

    def __init__(self, center=None):
        self._params_names = ['amplitude', 'decay']
        self._indep = 2
        amp_range = np.arange(0, 100, 0.05)
        decay_range = np.arange(0.8, 15, 0.001)
        # center_range = np.arange(center-20,center+20,0.01)

        self.range_dicts = {
            'amplitude': (0.00, 100, 0.05),
            'decay': (0.0, 1.5, 0.001)
        }

        self._Params = ParamsDict(self._params_names)
        self._Params.initialize_range(self.range_dicts)

    def get_func(self, x, *args):
        Params = self._Params.get()
        amplitude = Params['amplitude']
        decay = Params['decay']

        background_y = shirley(x, args[0])
        exp_y = amplitude*np.exp(-x/decay)
        total = exp_y + background_y
        return total


class ShirleyBG_Obj(BaseObj):
    def __init__(self, center=None):
        self._params_names = ['gwid', 'lwid', 'center', 'amplitude']
        self._indep = 4

        self.range_dicts = {
            'amplitude': (0.00, 1.0, 0.001),
            'center': center,
            'gwid': (0, 1.0, 0.001),
            'lwid': (0, 1.0, 0.001)
        }

        self._Params = ParamsDict(self._params_names)
        self._Params.initialize_range(self.range_dicts)

    def get_func(self, x, *args):
        """Return the list of value using the model shape function
        :param x: x value
        :type x: int, list, nparray
        :returns: the list of value under the shape function
        :rtype: int, nparray
        """
        Params = self._Params.get()
        amplitude = Params['amplitude']
        gwid = Params['gwid']
        lwid = Params['lwid']
        center = Params['center']

        thewid_1 = np.sqrt((gwid/2)**2+np.sqrt(lwid*1.233)**2)
        thewid_2 = (gwid/2) + (lwid*1.233)
        comb_thewid = (thewid_1 + thewid_2)/2
        return amplitude*(1-(1-1/(1+np.exp((x-center)/comb_thewid))))


class DS_Jeff(BaseObj):
    """
    Calculate DoniachSunjic convoluted with Gaussian Width


    """

    def __init__(self, center=None):
        """
        :param center: inital center
        :type center: float

        """
        self._params_names = ['alpha', 'lwid', 'center']
        self._indep = 3

        self.range_dicts = {
            'alpha': (0.00, 1.5, 0.001),
            'center': (center-20, center+20, 0.01),
            'lwid': (0, 1.0, 0.001),
        }

        self._Params = ParamsDict(self._params_names)
        self._Params.initialize_range(self.range_dicts)

    def get_func(self, x, *args):
        Params = self._Params.get()
        alpha = Params['alpha']
        center = Params['center']
        lwid = Params['lwid']

        top = gammaln(1-alpha)*np.cos(np.pi*(alpha/2) +
                                      (1-alpha)*np.arctan((x-center)/lwid))
        bot = ((lwid * lwid) + ((x-center)*(x-center)))**((1-alpha)/2)
        return top/bot


class Thermal(BaseObj):
    """
    Bose form Thermal
    """

    def __init__(self, center=None, _prefix=''):
        """
        :param center: inital center
        :type center: float

        """
        self._prefix = ''
        self._params_names = ['amplitude', 'kt', 'center']
        self._indep = 3

        self.range_dicts = {
            'amplitude': (0.00, 1.5, 0.001),
            'center': (center-20, center+20, 0.01),
            'kt': (0, 1.0, 0.001),
        }

        self._Params = ParamsDict(self._params_names)
        self._Params.initialize_range(self.range_dicts)

    def get_func(self, x, *args):
        Params = self._Params.get()
        amplitude = Params['amplitude']
        center = Params['center']
        kt = Params['kt']
        # print(kt)
        # sys.exit()
        offset = -1
        # test_no_zero = not_zero(kt)
        return 1/(amplitude*np.exp((x - center)/kt) + offset)


class Eggholder:
    def __init__(self, center=None, _prefix=''):
        """
        :param center: inital center
        :type center: float

        """
        self._prefix = ''
        self._params_names = ['y']
        self._indep = 1

        self.range_dicts = {
            # 'x':(0.00,512,0.0001),
            'y': (0.00, 512, 0.0001),
        }

        self._Params = ParamsDict(self._params_names)
        self._Params.initialize_range(self.range_dicts)

    def get_func(self, x, *args):
        Params = self._Params.get()
        y = Params['y']

        return -(y+47) * np.sin(np.sqrt(np.abs(y + 0.5*x + 47))) - x*np.sin(np.sqrt(np.abs(x-(y+47))))


class Gaussian_Abs(BaseObj):
    def __init__(self, center=None, _prefix=''):

        self._prefix = ''
        self._params_names = ['center', 'par2', 'par3']
        self._indep = 3

        self.range_dicts = {
            'center': (center, center+1, 0.01),
            'par2': (0.00, 1500, 0.01),
            'par3': (0.00, 1500, 0.01)
        }

        self._Params = ParamsDict(self._params_names)
        self._Params.initialize_range(self.range_dicts)

    def get_func(self, x, *args):
        Params = self._Params.get()
        center = Params['center']
        par2 = Params['par2']
        par3 = Params['par3']

        term_1 = -(par3/np.sqrt(2*np.pi)*par2)
        term_2 = np.exp(-0.5*((x-center)/par2)**2)
        return np.exp(term_1*term_2)


class EmissionLorentz(BaseObj):

    def __init__(self, center=None, fwhm=None, flux=None, kurt=None, _prefix=''):
        """Lorentz function for modeling emission.

        It is for use when the independent axis is in Angstroms.

        Source: https://sherpa.readthedocs.io/en/latest/model_classes/api/sherpa.astro.optical.EmissionLorentz.html
        Args:
            center (_type_, optional): Center Range (Angstroms). Defaults to None.
            fwhm (_type_, optional): Full width half maximum (km/s). Defaults to None.
            flux (_type_, optional): Flux (normalisation of lorentzian). Defaults to None.
            kurt (_type_, optional): Kurt (kurtosis of the lorentzian). Defaults to None.
            _prefix (str, optional): Prefix for duplicates. Defaults to ''.
        """
        super().__init__(center, _prefix)
        self._params_names = ['center', 'fwhm', 'flux', 'kurt']
        self._indep = 4

        self.range_dicts = {
            'center': (center-0.5, center+0.5, 0.001),
            'fwhm': (0, 1e6, 1e-2),
            'flux': (0, 1, 1e-4),
            'kurt': (0, 2, 1e-3)
        }

        self._Params = ParamsDict(self._params_names)
        self._Params.initialize_range(self.range_dicts)

    def get_func(self, x, *args):
        Params = self._Params.get()
        center = Params['center']
        fwhm = Params['fwhm']
        flux = Params['flux']
        kurt = Params['kurt']

        s = center * fwhm/c
        l = np.abs(x - center)**kurt + (0.5*s)**2

        return flux * 2 * np.pi * s / l


class XStabsBG(BaseObj):
    def __init__(self, m1=None, m2=None, m3_Pho_index=None, m3_norm=None, prefix=""):
        self._prefix = prefix
        self._params_names = ['m1_h', 'm2_h', 'm3_pho', 'm3_norm']
        self._indep = 4

        self.range_dicts = {
            'm1_h': (0.00, 1.5, 0.001),
            # 'center':(center,center+1,0.01),
            'm2_h': (0, 1.5, 0.001),
            'm3_pho': (0, 1.5, 0.001),
            'm3_norm': (0.1, 1.5, 0.001)
        }

        self._Params = ParamsDict(self._params_names)
        self._Params.initialize_range(self.range_dicts)

    def get_func(self, x, *args):
        """Return the list of value using the model shape function
        :param x: x value
        :type x: int, list, nparray
        :returns: the list of value under the shape function
        :rtype: int, nparray
        """
        Params = self._Params.get()
        m1_h = Params['m1_h']
        m2_h = Params['m2_h']
        m3_pho = Params['m3_pho']
        m3_norm = Params['m3_norm']

        # Intgreate with Sherpa
        self.m1 = create_model_component('xstbabs', 'm1')
        self.m2 = create_model_component('xstbabs', 'm2')
        self.pl = create_model_component('xspowerlaw', 'm3')

        set_par(self.m1.nH, 0.0279, max=100000, frozen=True)
        set_par(self.m2.nH, 1.25492e-08, max=100000)
        set_par(self.pl.PhoIndex, 0.98279, min=-2, max=9)
        set_par(self.pl.norm, 0.000630890, max=1e+20)

        # set_par(self.m1.nH, m1_h, max=100000, frozen=True)
        # set_par(self.m2.nH, m2_h, max=100000)
        # set_par(self.pl.PhoIndex, m3_pho, min=-2, max=9)
        # set_par(self.pl.norm, m3_norm, max=1e+20)

        # construct the final model
        self.model = self.m1 * (self.m2 * self.pl)
        self_path = 1
        # self.eval_func(x)
        set_source(self_path, self.model)
        data = get_data(self_path)
        xm = get_fit_plot(1).modelplot.x
        ym = get_fit_plot(1).modelplot.y
        return ym


class Test_NGC_Model(BaseObj):
    def __init__(self, center=None, prefix=''):
        self._prefix = prefix
        self._params_names = ['m1_h', 'm2_h', 'm3_pho', 'm3_norm']
        self._indep = 4

        self.range_dicts = {
            'm1_h': (0.00, 1.5, 0.001),
            # 'center':(center,center+1,0.01),
            'm2_h': (0, 1.5, 0.001),
            'm3_pho': (0, 1.5, 0.001),
            'm3_norm': (0.1, 1.5, 0.001)
        }

        self._Params = ParamsDict(self._params_names)
        self._Params.initialize_range(self.range_dicts)


# class Sherpa_APEC(BaseObj):
    """Calculate the model response for APEC model

    Tbabs(lsmooth*vapec)

    """

    def __init__(self, _prefix=''):
        self._prefix = _prefix
        self._params_names = [
            'm3_kT', 'm3_C', 'm3_N', 'm3_O', 'm3_Ne', 'm3_Mg', 'm3_Fe', 'm3_norm'
        ]
        self._indep = len(self._params_names)

        self.m1 = create_model_component('xstbabs', 'm1')
        self.m2 = create_model_component('xslsmooth', 'm2')
        self.m3 = create_model_component('xsvapec', 'm3')

        self.range_dicts = {
            'm3_kT': (0.1, 10, 0.001),
            'm3_C': (0, 10, 0.001),
            'm3_N': (0, 10, 0.001),
            'm3_O': (0, 10, 0.001),
            'm3_Ne': (0, 10, 0.001),
            'm3_Mg': (0, 10, 0.001),
            'm3_Fe': (0, 1, 0.001),
            'm3_norm': (1e-4, 1.5, 0.001)
        }

        self._Params = ParamsDict(self._params_names)
        self._Params.initialize_range(self.range_dicts)

        set_par(self.m1.nH, 0.0279, max=100000, frozen=True)
        set_par(self.m2.Sig_6keV, 0.02, max=10, frozen=True)
        set_par(self.m2.Index, 1, frozen=True)
        # set_par(m3.kT, 0.502421)
        set_par(self.m3.He, 1, frozen=True)
        # set_par(m3.C, 5.5039)
        # set_par(m3.N, 0.990385)
        # set_par(m3.O, 6.48552e-18)
        # set_par(m3.Ne, 0.839257)
        # set_par(m3.Mg, 1.53165)
        set_par(self.m3.Al, 1, frozen=True)
        set_par(self.m3.Si, 1, frozen=True)
        set_par(self.m3.S, 1, frozen=True)
        set_par(self.m3.Ar, 1, frozen=True)
        set_par(self.m3.Ca, 1, frozen=True)
        # set_par(m3.Fe, 0.179656)
        set_par(self.m3.Ni, 1, frozen=True)
        set_par(self.m3.redshift, 0.00081, frozen=True)
        # set_par(self.m3.norm, 0.000908296, max=1e+20)

    def get_func(self):
        Params = self._Params.get()
        set_par(self.m3.kT, Params['m3_kT'])
        set_par(self.m3.C, Params['m3_C'])
        set_par(self.m3.N, Params['m3_N'])
        set_par(self.m3.O, Params['m3_O'])
        set_par(self.m3.Ne, Params['m3_Ne'])
        set_par(self.m3.Mg, Params['m3_Mg'])
        set_par(self.m3.Fe, Params['m3_Fe'])
        set_par(self.m3.norm, Params['m3_norm'])

        model = self.m1*(self.m2(self.m3))
        return model


# class Sherpa_APEC_BG(BaseObj):
    """Calculate the model response for APEC model

    TBabs(TBabs*powerlaw + lsmooth(vapec))

    self.m1(self.m5*self.m4 + self.m2(self.m3))
    """

    def __init__(self, _prefix=''):
        self._prefix = _prefix
        self._params_names = [
            'm3_kT', 'm3_C', 'm3_N', 'm3_O', 'm3_Ne', 'm3_Mg', 'm3_Fe', 'm3_norm',
            'm4_PhoIndex', 'm4_norm'
        ]
        self._indep = len(self._params_names)

        self.m1 = create_model_component('xstbabs', 'm1')
        self.m2 = create_model_component('xslsmooth', 'm2')
        self.m3 = create_model_component('xsvapec', 'm3')
        self.m4 = create_model_component('xspowerlaw', 'm4')
        self.m5 = create_model_component('xstbabs', 'm5')

        self.range_dicts = {
            'm3_kT': (0.1, 10, 0.001),
            'm3_C': (0, 10, 0.001),
            'm3_N': (0, 10, 0.001),
            'm3_O': (0, 10, 0.001),
            'm3_Ne': (0, 10, 0.001),
            'm3_Mg': (0, 10, 0.001),
            'm3_Fe': (0, 1, 0.001),
            'm3_norm': (1e-4, 1.5, 0.001),
            'm4_PhoIndex': (-2, 9, 0.001),
            'm4_norm': (0.0, 100, 0.001),
            # 'm5_nH': (0.0, 1.0, 1e-4)
        }

        self._Params = ParamsDict(self._params_names)
        self._Params.initialize_range(self.range_dicts)

        set_par(self.m1.nH, 0.0279, max=100000, frozen=True)
        set_par(self.m2.Sig_6keV, 0.02, max=10, frozen=True)
        set_par(self.m2.Index, 1, frozen=True)
        # set_par(m3.kT, 0.502421)
        set_par(self.m3.He, 1, frozen=True)
        # set_par(m3.C, 5.5039)
        # set_par(m3.N, 0.990385)
        # set_par(m3.O, 6.48552e-18)
        # set_par(m3.Ne, 0.839257)
        # set_par(m3.Mg, 1.53165)
        set_par(self.m3.Al, 1, frozen=True)
        set_par(self.m3.Si, 1, frozen=True)
        set_par(self.m3.S, 1, frozen=True)
        set_par(self.m3.Ar, 1, frozen=True)
        set_par(self.m3.Ca, 1, frozen=True)
        # set_par(m3.Fe, 0.179656)
        set_par(self.m3.Ni, 1, frozen=True)
        set_par(self.m3.redshift, 0.00081, frozen=True)
        set_par(self.m5.nH, 1.25492e-08, frozen=True)
        # set_par(self.m3.norm, 0.000908296, max=1e+20)

    def get_func(self):
        Params = self._Params.get()
        set_par(self.m3.kT, Params['m3_kT'])
        set_par(self.m3.C, Params['m3_C'])
        set_par(self.m3.N, Params['m3_N'])
        set_par(self.m3.O, Params['m3_O'])
        set_par(self.m3.Ne, Params['m3_Ne'])
        set_par(self.m3.Mg, Params['m3_Mg'])
        set_par(self.m3.Fe, Params['m3_Fe'])
        set_par(self.m3.norm, Params['m3_norm'])

        set_par(self.m4.PhoIndex, Params['m4_PhoIndex'])
        set_par(self.m4.norm, Params['m4_norm'])

        # set_par(self.m5.nH, Params['m5_nH'])

        model = self.m1*(self.m5*self.m4 + self.m2(self.m3))
        return model


class XspecSpectrum(BaseObj):
    def __init__(self, src__prefix=''):
        """
        :param center: inital center
        :type center: float

        """
        self._prefix = ''


        self._params_names = [
            'TBabs_2_nH',
            'PhoIndex', 'Pl_norm',
            'vapec_kT','vapec_C','vapec_N','vapec_O','vapec_Ne','vapec_Mg','vapec_Fe','vapec_norm',
            'vapec_6_kT','vapec_6_norm',
            'vacx2_collnpar','vacx2_norm'
        ]
        # self._pars_
        self._indep = 15
        # initalize parameters
        self.xspec = xspec
        # self.xspec.Plot.device = "/null"
        # self.xspec.Plot.xAxis = "angstrom"
        # self.xspec.Plot.xLog = False
        # self.xspec.Plot.yLog = False
        # self.xspec.Plot.perHz = False
        # self.xspec.Plot.area = True
        # self.xspec.Plot.background = True
        # print(os.getcwd())

        # fits_path = '/Users/andy/projects/Astro_Neo/input_files/astronomy_test/'
        # fits_file = 'left_pha_grp.fits'

        # fits_full_path = os.path.join(os.getcwd(), str(fits_file))
        # print(fits_full_path)
        # sys.exit()
        # Standard paramters:

        # old_dir = os.getcwd()
        # file_dir = os.chdir(fits_path)
        # self.l_src = self.xspec.Spectrum(fits_file)
        # self.l_src.ignore("**-7.0 30.0-**")
        # os.chdir(old_dir)
        # self.xspec.AllData.show()
        # sys.exit()
        """
        self.model = xspec.Model("TBabs(TBabs*powerlaw + lsmooth(vapec + zashift*vacx2))")

        # Model

        # Tbabs <1>
        self.model.TBabs.nH.frozen = True
        self.model.TBabs.nH = 0.0279

        # Tbabs <2>

        # Powerlaw <3>

        # lsmooth <4>
        self.model.lsmooth.Sig_6keV.frozen = True
        self.model.lsmooth.Sig_6keV = 0.02
        self.model.lsmooth.Index.frozen = True
        self.model.lsmooth.Index = 1

        # vapec <5>
        self.model.vapec.C.frozen = False
        self.model.vapec.N.frozen = False
        self.model.vapec.O.frozen = False
        self.model.vapec.Ne.frozen = False
        self.model.vapec.Mg.frozen = False
        self.model.vapec.Fe.frozen = False
        # self.model.vapec.Redshift.frozen = True
        self.model.vapec.Redshift = 0.00081

        # zashift <6>
        self.model.zashift.Redshift.frozen = True
        self.model.zashift.Redshift = 0.00081

        # vacx2 <7>
        self.model.vacx2.temperaturekeV = self.model.vapec.kT
        self.model.vacx2.collnpar = 280
        self.model.vacx2.collntype = 4
        self.model.vacx2.acxmodel = 2
        self.model.vacx2.recombtype = 2
        self.model.vacx2.C.frozen = False
        self.model.vacx2.N.frozen = False
        self.model.vacx2.O.frozen = False
        self.model.vacx2.Ne.frozen = False
        self.model.vacx2.Mg = self.model.vapec.Mg
        self.model.vacx2.Ni = self.model.vapec.Fe
        """

        self.range_dicts = {
            # TBabs <1>
            # 'nH': (0.00, 0.03, 0.001),
            # TBabs_2 <2>
            'TBabs_2_nH': (0.00,0.03,0.0001),
            # Powerlaw
            'PhoIndex': (0.05, 1.1, 0.0001),
            'Pl_norm': (0.0005, 0.0007, 1e-6),
            # lsmooth
            # 'Sig_6keV': (0.001, 0.1, 0.001),
            # vapec <5>
            'vapec_kT': (0.0808, 0.6, 0.001),
            'vapec_C': (0.00, 1.00, 0.001),
            'vapec_N': (0.00, 1.50, 0.001),
            'vapec_O': (0.0, 1.00, 0.001),
            'vapec_Ne': (0.8, 1.00, 1e-5),
            'vapec_Mg': (0.0, 2.00 , 0.0001),
            'vapec_Fe': (0.0, 1.00, 1e-4),
            # 'Redshift': (0.0001, 0.00081, 1e-5),
            'vapec_norm': (0.0008, 0.0010, 1e-5),
            'vapec_6_kT': (0.0808, 0.75, 0.001),
            'vapec_6_norm': (0.0008, 0.0010, 1e-5),
            # zashift <6>
            # vacx2 <7>
            'vacx2_collnpar': (0.01, 1000, 0.01),
            # 'vacx2_C': (0, 0.005, 1e-5),
            # 'vacx2_N': (0, 10, 0.01),
            # 'vacx2_O': (0, 10, 0.01),
            # 'vacx2_Ne': (0, 10, 0.01),
            'vacx2_norm': (0,1e-4,10000,'number'),
        }
        self._Params = ParamsDict(self._params_names)
        self._Params.initialize_range(self.range_dicts)

    def get_func(self,*args):
        Params = self._Params.get()

        return Params

    def get_pars_dicts(self,pars_list):
        """Get parameters list in xspec dictionary form
        """

        Params = self._Params.get()

        assert len(pars_list) == len(Params), "Length of pars_list must be equal to length of Params"
        xspec_dicts = {}
        for i,(k,v) in enumerate(Params.items()):
            xspec_dicts[pars_list[i]] = v

        return xspec_dicts

    def mutate(self):
        self._Params.initialize_range(self.range_dicts)

    def mutate_par(self,par):
        """Mutate specfic parameters

        Args:
            pars (str): parameters strength
        """

        self._Params.random_pars(par)


