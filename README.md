# Astro Neo

#### Versions: 0.0.1

#### Last update: Jan 28, 2023

Astro Neo

## Prerequisites
<!-- It is highly recommend to utilize `anaconda` or `pipx` package managers to prevent unforseen dependency conflicts. EXAFS Neo uses [`larch`](https://xraypy.github.io/xraylarch/) to process the x-ray spectrum.

  - Python: 3.x
  - Numpy: 1.17.2
  - Larch: >0.9.46
  - Matplotlib: 3.1.2

It is highly recommend to create a new environment in `anaconda` to run EXAFS Neo to prevent packages conflicts.

        conda create --name exafs python=3.7  numpy matplotlib pyqt
        conda activate exafs
        conda install -yc GSECARS xraylarch -->

## Installations

<!-- Create new environment using the environment files given:

Linux:

        conda env create ciao -f models/ciao-4.13-Linux-environment.yml

Mac:

        conda env create ciao -f models/ciao-4.13-macOS-environment.yml

Afterward install the Astro Neo packages by:

        pip install setup.py
<!-- To install EXAFS Neo, simply clone the repo:

        git clone https://github.com/laumiulun/EXAFS-Neo-Public.git
        cd EXAFS-Neo-Public/
        python setup.py install -->

Linux:

        conda create -n ciao -c <https://cxc.cfa.harvard.edu/conda/ciao> -c conda-forge ciao sherpa ds9 ciao-contrib caldb_main marx

Mac (x86 Intel):

        conda create -n ciao -c https://cxc.cfa.harvard.edu/conda/ciao -c conda-forge ciao sherpa ds9 ciao-contrib caldb_main marx

Mac (M1):

        CONDA_SUBDIR=osx-64 conda create -n ciao -c https://cxc.cfa.harvard.edu/conda/ciao -c conda-forge ciao sherpa ds9 ciao-contrib caldb_main marx

## Usage

To perform a simple test, make sure the right environment is set, and select a input file as a input arguments:

        astro-neo -i test/test.ini

<!-- To run a sample test, make sure the enviornment is set correctly, and select a input file:

        exafs -i test/test.ini -->

## Update
<!-- EXAFS Neo is under active development, to update the code after pulling from the repository:

        git pull --rebase
        python setup.py install -->

Astro Neo is under active development, to update the code after pulling the latest changes from the repository:

        git pull --rebase
        pip install setup.py

## GUI
<!-- We also have provided a GUI for use in additions to our program, with additional helper script to facilitate post-analysis. To use the GUI:

        cd gui
        python XAFS_GUI.py

The GUI contains helper function which -->

We also have provided a GUI for use in additions to our program, with additional helper script to facilitate pre and post-analysis. The GUI is under active development and in beta still:

        cd gui
        python Astro_GUI.py

<!-- ## Potential Errors
If you get an error message involving psutl, make sure you are in the right conda environment and reinstall psutl and xraylarch:

        conda activate exafs
        conda install psutl
        conda install -yc GSECARS xraylarch -->

<!-- ## Video Demonstration
You can see a list of video demonstrations of the EXAFS Neo package presented, future presentation related to this software will be posted as they are available

- https://youtu.be/KwhItvwhapg [Feb 15, 2021] (University of Washington)
- https://youtu.be/jqISqq_FFR8 [Dec 10, 2020] (Canadian Light Source) -->

## Citation
<!--
Jeff Terry, Miu Lun Lau, Jiateng Sun, Chang Xu, Bryan Hendricks, Julia Kise, Mrinalini Lnu, Sanchayni Bagade, Shail Shah, Priyanka Makhijani, Adithya Karantha, Travis Boltz, Max Oellien, Matthew Adas, Shlomo Argamon, Min Long, and Donna Post Guillen, “Analysis of Extended X-ray Absorption Fine Structure (EXAFS) Data Using Artificial Intelligence Techniques,” Applied Surface Science 547, 149059 https://doi.org/10.1016/j.apsusc.2021.149059 (2021). -->
