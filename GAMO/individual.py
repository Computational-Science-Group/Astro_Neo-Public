from .pathObj import GaussianObj,VoigtObj,DoniachObj,ShirleyBG_Obj,ShirleyExpObj,\
        ExponentialObj,DoniachObjGauss,DoniachObj_Test,DS_Jeff,Thermal

from .pathObj import Eggholder
# from pathObj import VoigtObj,DoniachObj,GaussianObj,ExponentialObj,ShirleyExpObj

import sys

def shape_function_parser(Fit,center_range=0,*args):
    switch = {
        "Gaussian": GaussianObj(center_range),
        "Voigt": VoigtObj(center_range),
        "DoniachSunjic": DoniachObj(center_range),
        "Exponential": ExponentialObj(center_range),
        # "ShirleyExp": ShirleyExpObj(center_range),
        "DoniachObjGauss": DoniachObjGauss(center_range),
        "DoniachObj_Test": DoniachObj_Test(center_range),
        # "GLP": GLPObj(center_range),
        "ShirleyBG": ShirleyBG_Obj(center_range),
        "ShirleyExp": ShirleyExpObj(center_range),
        "DS_Jeff": DS_Jeff(center_range),
        "Thermal": Thermal(center_range),
        "EggHolder": Eggholder(center_range),
        # "XspecSpectrum": XspecSpectrum(center_range,args[2])
    }
    return switch.get(Fit,"Invalid")


class BackgroundObj():
    def __init__(self,nfuncs,fits,center):
        self.nfuncs = nfuncs
        self.fits = fits
        self.Population = [None]* self.nfuncs

        for i in range(nfuncs):
            obj = shape_function_parser(self.fits[i],center[i])
            # print(obj)
            if obj == 'Invalid':
                print("Invalid Fits selection")
                sys.exit()
            self.Population[i] = obj

    def get_func(self,x,y):
        for i in range(self.nfuncs):
            background = self.Population[i].get_func(x,y)

        return y
class Individual():
    def __init__(self,npaths,fits,center):
        self.npaths = npaths
        self.Population = [None]* self.npaths
        self.center = center
        self.fits = fits
        # print(self.npaths)
        for i in range(self.npaths):

            obj = shape_function_parser(self.fits[i],self.center[i])
            if obj == 'Invalid':
                print("Invalid Fits selection: " + str(self.fits[i]))
                sys.exit()
            self.Population[i] = obj

        """
        Not using, need to rewrite this correlated paths using lmfit
        """
    def correlate_update(self):
        corr_list = int(self.corr_paths[0])
        amp = self.Population[corr_list].get_amp()
        gamma = self.Population[corr_list].get_gamma()
        sigma = self.Population[corr_list].get_sigma()
        split_ratio = self.Population[corr_list].get_spin_ratio()

        orbit_split = self.Population[corr_list].get_orbit_splitting()

        for j in range(self.npaths):
            if j not in self.corr_paths:

                self.Population[j].set_spin_ratio(split_ratio)
                self.Population[j].set_orbit_splitting(orbit_split)

                self.Population[j].set_sigma(sigma)
                self.Population[j].set_gamma(gamma)

    def get(self):
        Population = []
        for i in range(self.npaths):
            Population.append(self.Population[i].get())
        return Population

    def get_func(self):
        Population = []
        for i in range(self.npaths):
            Population.append(self.Population[i])
        return Population

    def get_path(self,i):
        return self.Population[i].get()

    def verbose(self):
        """
        Print out the Populations
        """
        for i in range(self.npaths):
            self.Population[i].verbose()

    def set_path(self,i,params):
        params_names = self.Population[i].get_params_names()
        dicts = {}
        for j,key in enumerate(params_names):
            dicts[key] = params[j]

        self.Population[i].set(dicts)
