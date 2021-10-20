# Environment files using anaconda for CIAO

https://anaconda.org/CXC

Select the right one depend on the type of Operating system you have (Linux, MacOS, etc) 

Install the environment using the following command

    `conda env create -n <env_name> -f <environment.yml>`

This will install ciao with xspec included. To check if xspec is install:

    `from sherpa.astro import ui`
    `from sherpa.astro import xspec`
    `xspec.get_xsversion()`

