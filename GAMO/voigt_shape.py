import numpy as np
from scipy.special import wofz


def voigt_fuc(x,amplitude,center,sigma,gamma,alpha=0,use_alpha=False):
    """
    Return the Voigt line shape at x with Lorentzian component HWHM gamma
    and Gaussian component HWHM alpha.

    There are two components to the Voigt shape, one is the lorenization and the other is the gaussian components.
    Gamma: Lorentzian
    Sigma: Gaussian
    """
    if use_alpha:
        sigma =  alpha / np.sqrt(2 * np.log(2))

    return amplitude*np.real(wofz((x - center + 1j*gamma)/sigma/np.sqrt(2))) / sigma\
                                                           /np.sqrt(2*np.pi)

if __name__ == "__main__":
    from lmfit.models import VoigtModel
    x = np.linspace(-1,1,201)
    y_temp = np.linspace(-1,1,201)

    amplitude = 1
    center = -0.5
    sigma = 1
    gamma = 1

    y = voigt_fuc(x,amplitude, center,sigma, gamma)

    # testing the model using lmfit
    fit_model = VoigtModel()
    result = fit_model.fit(data=y_temp,x=x,amplitude=amplitude,center=center,sigma=sigma,gamma=gamma)
    # print(result)
