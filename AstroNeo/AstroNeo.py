# from .helper import *
from . import helper
from . import fitness
from . import individual
# from .import_lib import *
# from .ini_parser import *
# from .fitness import *
# from .individual import Individual
# from .background_function import shirley, nobg, shirley_temp
import cProfile
# import pstats

# from .run_verbose import *

# ----------------------------
# Import Library
import os, copy, random, logging
from psutil import cpu_count
import time, datetime, subprocess
import csv
import sys
from loky import ProcessPoolExecutor
# import sherpa
import matplotlib as mpl
import matplotlib.pyplot as plt
import pathlib
import numpy as np
import operator
import random
import copy
# from .import_lib import *
from . import input_arg
# from .helper import *

# Need further testing to see if this is needed...
os.environ['HEADAS'] = '/Users/andy/projects/xspec/heasoft-6.31.1/aarch64-apple-darwin22.4.0'
os.system(f"source $HEADAS/headas-init.sh")

import xspec

sys.path.append("/Users/andy/projects/Astro_Neo/input_files/ACX2")
import acx2_xspec

xspec.xset.Xset.chatter = 0


# Set the number of threads
os.environ['NUMEXPR_MAX_THREADS'] = str(cpu_count())


# ----------------------------


class AstroNEO:

    def initialize_params(self, verbose=False):
        """
        Initialize Parameters
        """

        # print("Initialize Parameters")
        self.intervalK = 0.05
        file_dict, timeing_mode = input_arg.input()
        if timeing_mode:
            t1 = helper.timecall()

        self.file_dict =  input_arg.ini_parser(file_dict)

        # if timeing_mode:
            # print(f'Inital import function took {} second' % initial_elapsed)
    def initialize_variable(self):
        """
        Initalize variables
        """
        self.ProcessPool = ProcessPoolExecutor(4)
        self.genNum = 0
        self.nChild = 4
        self.globBestFit = [0, np.inf]
        self.currBestFit = [0, np.inf]
        self.bestDiff = np.inf
        self.bestBest = np.inf
        self.diffCounter = 0

        self.pathDictionary = {}
        # self.MetaDictionary = {}
        # Not used
        # self.sortedFourier = 0
        # self.bestFitIndi = (())
        # self.bestChir_magTotal = [0]*(326)
        # self.bestYTotal = [0]*(401)

        # Typical INI parameters
        # self.ind_options = individual_path
        # if self.ind_options == True:
        # self.path_lists = path_list
        # else:
        # self.path_lists = list(range(1,pathrange+1))
        # for i in range(len(self.path_lists)):
        # self.path_lists[i] = str(self.path_lists[i])
        # self.npaths = len(self.path_lists)

        # Inputs
        self.data_file = self.file_dict["data_file"]
        # self.fits_file = fits_file
        # print(self.fits_file)
        # Paths
        self.npaths = self.file_dict['npaths']
        self.fits = self.file_dict['fits'].split(",")

        self.center = self.file_dict['center']
        # self.corr = corr
        # self.corr_list = corr_list

        # Populations
        self.npops = self.file_dict['size_population']
        self.ngen = self.file_dict['number_of_generation']
        self.steady_state = self.file_dict['steady_state']

        # Mutation Parameters
        self.mut_opt = self.file_dict['mutated_options']
        self.mut_chance = self.file_dict['chance_of_mutation']
        # self.mut_chance_e0 = chance_of_mutation_e0

        # Crosover Parameters
        self.n_bestsam = int(self.file_dict['best_sample']*self.npops*(0.01))
        self.n_lucksam = int(self.file_dict['lucky_few']*self.npops*(0.01))

        # Time related
        self.time = False
        self.tt = 0

        # Figure related:
        self.printgraph = self.file_dict['printgraph']
        if self.printgraph:
            self.fig = plt.figure()
            # Add one figs
            self.ax = self.fig.add_subplot(111)
        # Profile related:
        self.profile_toggle = self.file_dict['profile']
        if self.profile_toggle:
            self.profiler = cProfile.Profile()
            self.profiler.enable()



    def initialize_logger(self):
        """Initialize logger
        """
        # Initialize logger
        self.logger = logging.getLogger('')

        # Delete handler
        self.logger.handlers = []
        file_handler = logging.FileHandler(
            self.log_path, mode='a+', encoding='utf-8')
        stdout_handler = logging.StreamHandler(sys.stdout)

        formatter = logging.Formatter('%(message)s')
        file_handler.setFormatter(formatter)
        stdout_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(stdout_handler)

        self.logger.setLevel(logging.INFO)
        self.logger.info(helper.banner())

    def initialize_file_path(self, i=0):
        """
        Initalize file paths for each of the file first
        """
        self.base = os.getcwd()
        self.output_path = os.path.join(self.base, self.file_dict['output_file'])
        self.log_path = os.path.splitext(copy.deepcopy(self.output_path))[0] + ".log"

        self.check_output_file(self.output_path)
        self.check_output_file(self.log_path)
    def check_if_exists(self, path_file):
        """
        Check if the directory exists
        """
        if os.path.exists(path_file):
            os.remove(path_file)
        # Make Directory when its missing
        path = pathlib.Path(path_file)
        path.parent.mkdir(parents=True, exist_ok=True)

    def check_output_file(self, file):
        """
        check if the output file for each of the file
        """
        file_base = os.path.splitext(file)[0]
        self.check_if_exists(file)
        self.file = file

        self.file_initial = open(self.output_path, "a+")
        self.file_initial.write(
            "Gen,TPS,FITTNESS,CURRFIT,CURRIND,BESTFIT,BESTIND\n")  # writing header
        self.file_initial.close()

        # Not using right now
        # file_score = os.path.splitext(file)[0] + '_score.csv'
        # self.check_if_exists(file_score)
        # self.file_score = file_score

        file_data = os.path.splitext(file)[0] + '_data.csv'
        self.check_if_exists(file_data)
        self.file_data = file_data
        # Not using right now
        # file_gen = os.path.splitext(file)[0] + '_generations.csv'
        # self.check_if_exists(file_gen)

    def initialize_fits(self):

        old_dir = os.getcwd()
        # print(old_dir)
        data_file = "/Users/andy/projects/Astro_Neo/input_files/astronomy_test/left_pha_grp.fits"
        bg_file = "/Users/andy/projects/Astro_Neo/input_files/astronomy_test/left_mbg.fits"
        rsp_file = "/Users/andy/projects/Astro_Neo/input_files/astronomy_test/left_rmf.fits"

        file_dir = os.chdir('/Users/andy/projects/Astro_Neo/input_files/astronomy_test/')
        self.xspec = xspec


        self.xspec.AllData.clear()
        # l_src = xspec.Spectrum(data_file,
        #                       backFile=bg_file,
        #                       respFile=rsp_file)
        self.l_src = self.xspec.Spectrum('left_pha_grp.fits')

        self.xspec.Plot.xAxis = "angstrom"
        self.l_src.ignore("**-7.0 30.0-**")

        # os.chdir(old_dir)
        self.xspec.AllData.show()

        self.xspec.Plot.xAxis = "angstrom"
        self.xspec.Plot.xLog = False
        self.xspec.Plot.yLog = False
        self.xspec.Plot.perHz = False
        self.xspec.Plot.area = True
        self.xspec.Plot.background = True

        self.xspec.Fit.statMethod = "cstat"  # using the Cash statistic


        self.xspec.Plot("data")
        # xspec.AllModels.setEnergies("xbin.txt")   #using the specified energy bins

        # l_folded = xspec.Plot.model()

        self.l_chans = xspec.Plot.x()
        self.l_rates = xspec.Plot.y()
        self.l_xErrs = xspec.Plot.xErr()
        self.l_yErrs = xspec.Plot.yErr()
        self.l_bkg = xspec.Plot.backgroundVals()


    def generateIndividual(self):
        # self.fits = 'Test'
        # self.center = ''
        ind = individual.Individual(self.npaths, self.fits, self.center)
        # sys.exit()
        return ind

    def generateFirstGen(self):
        self.Populations = []

        for i in range(self.npops):
            self.Populations.append(self.generateIndividual())


    def eval_Population(self):
        """Evaluate the population for GA

        Returns:
            list: list of score
        """

        scores = []
        populationPerf = {}
        for i, individual in enumerate(self.Populations):

            temp_score = self.ProcessPool.submit(fitness.fitness, (individual,self.xspec))
            scores.append(temp_score)

        # Gather the data
        reuslts = [i.result() for i in scores]

        for i, individual in enumerate(self.Populations):
            populationPerf[individual] = reuslts[i]


        # for i, individual in enumerate(self.Populations):

        #     temp_score = fitness.fitness(individual)
        #     scores.append(temp_score)

        #     populationPerf[individual] = temp_score

        self.sorted_population = sorted(
            populationPerf.items(), key=operator.itemgetter(1), reverse=False)

        self.currBestFit = self.sorted_population[0]

        # return score

    def next_generation(self):
        """Next Generation for GA
        """
        self.st = time.time()
        # ray.init()
        self.logger.info("---------------------------------------------------------")
        self.logger.info(datetime.datetime.fromtimestamp(
            self.st).strftime('%Y-%m-%d %H:%M:%S'))
        self.logger.info(f"{helper.bcolors.BOLD}Gen: {helper.bcolors.ENDC}{self.genNum+1}")

        self.genNum += 1

        # Evaluate Fittness
        self.eval_Population()
        # self.sorted_population()
        # print(score)
        self.bestDiff = abs(self.globBestFit[1]-self.currBestFit[1])
        # print(self.bestDiff)
        if self.currBestFit[1] < self.globBestFit[1]:
            self.globBestFit = self.currBestFit

        # Rechenberg mutation
        if self.genNum > 20:
            if self.bestDiff < 0.1:
                self.diffCounter += 1
            else:
                self.diffCounter -= 1
            if (abs(self.diffCounter) / float(self.genNum)) > 0.2:
                self.mut_chance += 0.5
                self.mut_chance = abs(self.mut_chance)
            elif (abs(self.diffCounter) / float(self.genNum)) < 0.2:
                self.mut_chance -= 0.5
                self.mut_chance = abs(self.mut_chance)


        self.output_best_parameters()

        self.selectFromPopulation()
        self.createChildren()
        self.logger.info(f"Number of Breeders: {str(len(self.parents))}")
        self.logger.info(f"DiffCounter: {self.diffCounter}")
        self.logger.info(f"Diff %: {self.diffCounter / self.genNum}")
        self.logger.info(f"Mutation Chance: {self.mut_chance}")
        self.mutatePopulation()

        self.et = helper.timecall()
        self.tdiff = self.et - self.st
        self.tt = self.tt + self.tdiff
        self.logger.info(f"Time: {str(round(self.tdiff, 3))} s")


    def output_best_parameters(self):

        with np.printoptions(precision=5, suppress=True):
            self.logger.info(
                f"Best Fit: {helper.bcolors.BOLD}{self.sorted_population[0][1]}{helper.bcolors.ENDC}")
            self.logger.info(f"2nd Fit: {self.sorted_population[1][1]}")
            self.logger.info(f"3rd Fit: {self.sorted_population[2][1]}")
            self.logger.info(f"4th Fit: {self.sorted_population[3][1]}")
            self.logger.info(f"Last Fit: {self.sorted_population[-1][1]}")
            self.logger.info(f"Different from last best fit: {self.bestDiff}")
            # print(bcolors.BOLD + "Best fit :", bcolors.OKBLUE +
            #       str(self.currBestFit[1]) + bcolors.ENDC)
            # CurrchiR = self.currBestFit[1]/(len(self.x_raw)-4*self.npaths)
            # print(bcolors.BOLD + "Best fit ChiR:",
            #       bcolors.OKBLUE + str(CurrchiR) + bcolors.ENDC)

            self.logger.info(f"Best Fit Combination:")
            params_list = self.currBestFit[0].get_func()[0].get_func()
            self.logger.info(f"    TBabs_2_nH: {np.round(params_list['TBabs_2_nH'],5)}")
            self.logger.info(f"    PhoIndex: {np.round(params_list['PhoIndex'],5)}")
            self.logger.info(f"    Pl_norm: {np.round(params_list['Pl_norm'],5)}")
            self.logger.info(f"    vapec_kT: {np.round(params_list['vapec_kT'],5)}")
            self.logger.info(f"    vapec_C: {np.round(params_list['vapec_C'],5)}")
            self.logger.info(f"    vapec_N: {np.round(params_list['vapec_N'],5)}")
            self.logger.info(f"    vapec_O: {np.round(params_list['vapec_O'],5)}")
            self.logger.info(f"    vapec_Ne: {np.round(params_list['vapec_Ne'],5)}")
            self.logger.info(f"    vapec_Mg: {np.round(params_list['vapec_Mg'],5)}")
            self.logger.info(f"    vapec_Fe: {np.round(params_list['vapec_Fe'],5)}")
            self.logger.info(f"    vapec_norm: {np.round(params_list['vapec_norm'],5)}")
            self.logger.info(f"    vapec_6_kT: {np.round(params_list['vapec_6_kT'],5)}")
            self.logger.info(f"    vapec_6_norm: {np.round(params_list['vapec_6_norm'],5)}")
            self.logger.info(f"    vacx2_collnpar: {np.round(params_list['vacx2_collnpar'],5)}")
            self.logger.info(f"    vacx2_norm: {np.round(params_list['vacx2_norm'],7)}")

            # print("Best fit combination:\n",
            #       np.asarray(self.currBestFit[0].get()))
            # self.logger.info(bcolors.BOLD + "History Best:", bcolors.OKBLUE +
            #       str(self.globBestFit[1]) + bcolors.ENDC)
            self.logger.info(f"{helper.bcolors.BOLD}History Best :{helper.bcolors.OKBLUE}{self.globBestFit[1]}{helper.bcolors.ENDC}")
            # GlobchiR = self.globBestFit[1]/(len(self.x_raw)-4*self.npaths)
            # print(bcolors.BOLD + "History Best ChiR:",
            #       bcolors.OKBLUE + str(GlobchiR) + bcolors.ENDC)
            # print("History Best Indi:\n", np.asarray(
            #     self.globBestFit[0].get()))

    def mutatePopulation(self):
        """
        ## Mutation operators
        # 0 = original: generated a new versions:
        # 1 = mutated every genes in the total populations
        # 2 = mutated genes inside population based on secondary probability
        # 4 = metropolis hastings mutation
        """
        st = helper.timecall()
        self.nmutate = 0
        self.nmutate_success = []
        # if self.mut_opt == 0:
        for i in range(self.npops):
            if random.random()*100 < self.mut_chance:
                self.nmutate += 1
                self.Populations[i] = self.mutateIndi(i)

        if self.mut_opt == 2:
            self.logger.info(f"Total Metroplis Hasting Success: {sum(self.nmutate_success)}")

        self.logger.info(f"Mutate Times: {self.nmutate}")

        tdiff = helper.timecall() - st
        self.logger.info(f"Mutate Time: {str(round(tdiff, 3))} s")
    def mutateIndi(self,indi):
        """Mutate each individual

        Args:
            indi (ind_type): individual to be mutated

        Returns:
            ind_type: mutated individual
        """

        # Metroplis Hastings Mutation
        if self.mut_opt == 2:
            n_success = 0
            og_individual = self.generateIndividual()
            # Create a new individual with the same parameters
            og_pars = copy.copy(self.Populations[indi].get_func()[0].get())
            og_individual.set_path(0,og_pars)
            og_score = fitness.fitness((og_individual,self.xspec))

            new_individual = self.generateIndividual()
            mut_score = fitness.fitness((new_individual,self.xspec))

            T = - self.bestDiff/np.log(1-(self.genNum/self.ngen))
            if mut_score < og_score:
                n_success = n_success + 1

                newIndi = new_individual
            elif np.exp(-(mut_score-og_score)/(T+np.nan)) > np.random.uniform():
                n_success = n_success + 1
                newIndi = new_individual
            else:
                newIndi = og_individual

            self.nmutate_success.append(n_success)
            # self.logger.info(f"Metroplis Hasting Success: {nmutate_success}")
        else:
            newIndi = self.generateIndividual()
        return newIndi



    def selectFromPopulation(self):
        self.parents = []
        # choose the top samples
        for i in range(self.n_bestsam):
            self.parents.append(self.sorted_population[i][0])

    def crossover(self, individual1, individual2):
        """
        Uniform Cross-Over, 50% percentage chance
        """
        child = self.generateIndividual()

        for i in range(self.npaths):
            individual1_path = individual1.get_path(i)
            individual2_path = individual2.get_path(i)

            n_params = len(individual1_path)
            temp_path = []
            for j in range(n_params):
                if np.random.randint(0, 2) == True:
                    temp_path.append(individual1_path[j])
                else:
                    temp_path.append(individual2_path[j])

            child.set_path(i, temp_path)

        return child

    def createChildren(self):
        """
        Generate Children
        """
        self.nextPopulation = []
        # --- append the breeder ---
        for i in range(len(self.parents)):
            self.nextPopulation.append(self.parents[i])
        # print(len(self.nextPopulation))
        # --- use the breeder to crossover
        for i in range(abs(self.npops-self.n_bestsam)-self.n_lucksam):
            par_ind = np.random.choice(
                len(self.parents), size=2, replace=False)
            child = self.crossover(
                self.parents[par_ind[0]], self.parents[par_ind[1]])
            self.nextPopulation.append(child)
        # print(len(self.nextPopulation))

        for i in range(self.n_lucksam):
            self.nextPopulation.append(self.generateIndividual())

        random.shuffle(self.nextPopulation)
        self.Populations = self.nextPopulation

    def run_verbose_start(self):
        """Generate Verbose output at the start
        """
        self.logger.info("-----------Inputs File Stats---------------")
        self.logger.info(f"{helper.bcolors.BOLD}File{helper.bcolors.ENDC}: {self.data_file}")
        self.logger.info(f"{helper.bcolors.BOLD}File{helper.bcolors.ENDC}: {self.output_path}")
        # print(f"{helper.bcolors.BOLD}CSV series{helper.bcolors.ENDC}: {self.csv_series}")
        self.logger.info(f"{helper.bcolors.BOLD}Population{helper.bcolors.ENDC}: {self.npops}")
        self.logger.info(f"{helper.bcolors.BOLD}Num Gen{helper.bcolors.ENDC}: {self.ngen}")
        self.logger.info(f"{helper.bcolors.BOLD}Num Path{helper.bcolors.ENDC}: {self.npaths}")
        self.logger.info(f"{helper.bcolors.BOLD}Fits{helper.bcolors.ENDC}: {self.fits}")
        # print(f"{helper.bcolors.BOLD}Path{helper.bcolors.ENDC}: {self.path_lists}")
        # print(f"{helper.bcolors.BOLD}Path Optimize{helper.bcolors.ENDC}: {self.}")
        self.logger.info(f"{helper.bcolors.BOLD}Printout{helper.bcolors.ENDC}: {self.printgraph}")
        self.logger.info(f"{helper.bcolors.BOLD}profiler{helper.bcolors.ENDC}: {self.profile_toggle}")
        # print(f"{helper.bcolors.BOLD}Steady State{helper.bcolors.ENDC}: {steady_state}")
        # print(f"{helper.bcolors.BOLD}Output Paths{helper.bcolors.ENDC}: {num_output_paths}")
        self.logger.info("-------------------------------------------")

    def run_verbose_end(self):
        """Generate verbose output at the end
        """
        self.logger.info("-----------Output Stats---------------")
        self.logger.info(f"{helper.bcolors.BOLD}Total Time(s){helper.bcolors.ENDC}: {round(self.tt,4)}")
        # print(f"{helper.bcolors.BOLD}File{helper.bcolors.ENDC}: {self.data_path}")
        # print(f"{helper.bcolors.BOLD}{helper.bcolors.ENDC}: {self.npops}")
        # print(f"{helper.bcolors.BOLD}Num Gen{helper.bcolors.ENDC}: {self.ngen}")
        # print(f"{helper.bcolors.BOLD}Num Path{helper.bcolors.ENDC}: {self.npaths}")
        # print(f"{helper.bcolors.BOLD}Path{helper.bcolors.ENDC}: {self.path_lists}")
        self.logger.info("-------------------------------------------")



    def run(self):
        self.run_verbose_start()
        self.historic = []
        self.historic.append(self.Populations)
        for i in range(self.ngen):
            # self.active_background(self.globBestFit[0])
            temp_gen = self.next_generation()
            self.output_generations()
            if self.printgraph:
                # test_y = self.export_paths(self.globBestFit[0])
                # real_y = np.array(self.y_scaler.inverse_transform(
                #     test_y.reshape(-1, 1))).flatten() + self.bg
                # self.ax.plot(self.x_scaler.inverse_transform(
                #     self.x_normal.reshape(-1, 1)), real_y, 'k--', label='Fit')
                # self.ax.set_title('Generation: ' + str(i+1))
                # self.ax.scatter(self.x_raw, self.y_background +
                #                 self.bg, s=10, label='data')
                # self.out_str = str(np.asarray(self.currBestFit[0].get()))
                # self.ax.text(0.1, 0.8, s=self.out_str,
                #              transform=self.ax.transAxes)
                model_params = self.globBestFit[0].get_func()[0].get_func()
                """

                model = self.xspec.Model("tbabs*po+lsmooth*vapec")
                model.TBabs.nH.frozen = True
                model.lsmooth.Sig_6keV.frozen = True
                model.lsmooth.Index = 1
                model.vapec.C.frozen = False
                model.vapec.N.frozen = False
                model.vapec.O.frozen = False
                model.vapec.Ne.frozen = False
                model.vapec.Mg.frozen = False
                model.vapec.Fe.frozen = False
                model.vapec.Redshift.frozen = True

                # nH
                model.TBabs.nH = model_params['nH']
                # Powerlaw
                model.powerlaw.PhoIndex = model_params['PhoIndex']
                model.powerlaw.norm = model_params['Plnorm']
                # lsmooth
                model.lsmooth.Sig_6keV = model_params['Sig_6keV']
                # Vapec
                model.vapec.kT = model_params['kT']
                model.vapec.C = model_params['C']
                model.vapec.N = model_params['N']
                model.vapec.O = model_params['O']
                model.vapec.Ne = model_params['Ne']
                model.vapec.Mg = model_params['Mg']
                model.vapec.Fe = model_params['Fe']
                model.vapec.Redshift = model_params['Redshift']
                model.vapec.norm = model_params['VapecNorm']
                """
                model = xspec.Model("TBabs(TBabs*powerlaw + lsmooth(vapec + vapec + zashift*vacx2))")

                # Model

                # Tbabs <1>
                model.TBabs.nH.frozen = True
                model.TBabs.nH = 0.0279

                # Tbabs <2>

                # Powerlaw <3>

                # lsmooth <4>
                model.lsmooth.Sig_6keV.frozen = True
                model.lsmooth.Sig_6keV = 0.02
                model.lsmooth.Index.frozen = True
                model.lsmooth.Index = 1

                # vapec <5>
                model.vapec.C.frozen = False
                model.vapec.N.frozen = False
                model.vapec.O.frozen = False
                model.vapec.Ne.frozen = False
                model.vapec.Mg.frozen = False
                model.vapec.Fe.frozen = False
                # self.model.vapec.Redshift.frozen = True
                model.vapec.Redshift = 0.00081

                # model.vapec.N = 0.990385
                # model.vapec.O = 6.48552e-18
                # model.vapec.Ne = 0.839257
                # model.vapec.Mg = 1.53165
                # model.vapec.Fe = 0.179656
                # self.model.vapec.Redshift.frozen = True
                model.vapec.Redshift = 0.00081

                # vapec <6>
                model.vapec_6.kT.frozen = False
                model.vapec_6.C.link = model.vapec.C
                model.vapec_6.N.link = model.vapec.N
                model.vapec_6.O.link = model.vapec.O
                model.vapec_6.Ne.link = model.vapec.Ne
                model.vapec_6.Mg.link = model.vapec.Mg
                model.vapec_6.Fe.link = model.vapec.Fe
                model.vapec_6.Redshift.link = model.vapec.Redshift

                # zashift <7>
                model.zashift.Redshift.frozen = True
                model.zashift.Redshift = 0.00081

                # vacx2 <8>
                model.vacx2.temperature.link = model.vapec.kT
                model.vacx2.collnpar = 280
                model.vacx2.collntype = 4
                model.vacx2.acxmodel = 2
                model.vacx2.recombtype = 2

                model.vacx2.C.link = model.vapec.C
                model.vacx2.N.link = model.vapec.N
                model.vacx2.O.link = model.vapec.O
                model.vacx2.Ne.link = model.vapec.Ne
                model.vacx2.Mg.link = model.vapec.Mg
                model.vacx2.Fe.link = model.vapec.Fe


                # Set up params afterward
                model.TBabs_2.nH = model_params['TBabs_2_nH']
                # --------
                model.powerlaw.PhoIndex = model_params['PhoIndex']
                model.powerlaw.norm = model_params['Pl_norm']
                # --------
                model.vapec.kT = model_params['vapec_kT']
                model.vapec.C = model_params['vapec_C']
                model.vapec.N = model_params['vapec_N']
                model.vapec.O = model_params['vapec_O']
                model.vapec.Ne = model_params['vapec_Ne']
                model.vapec.Mg = model_params['vapec_Mg']
                model.vapec.Fe = model_params['vapec_Fe']
                model.vapec.norm = model_params['vapec_norm']
                # --------
                model.vapec_6.kT = model_params['vapec_6_kT']
                model.vapec_6.norm = model_params['vapec_6_norm']
                # --------
                model.vacx2.collnpar = model_params['vacx2_collnpar']
                # model.vacx2.C = model_params['vacx2_C']
                # model.vacx2.N = model_params['vacx2_N']
                # model.vacx2.O = model_params['vacx2_O']
                # model.vacx2.Ne = model_params['vacx2_Ne']
                model.vacx2.norm = model_params['vacx2_norm']


                # ------
                self.l_src.ignore("**-7.0 30.0-**")

                self.xspec.Plot("data")
                self.xspec.Plot.show()
                l_folded = self.xspec.Plot.model()



                # plt.plot()

                plt.step(self.l_chans,self.l_rates, where='mid', color='blue', linewidth=1.2, alpha=1)
                plt.step(self.l_chans, l_folded, where='mid', color='red', linewidth=2,label='Fit')
                # plt.xlim([7,30])
                # plt.ylim([-0.00005,0.00035])


                # plot_fit(1)
                plt.title(f'Generation: {self.genNum}')
                plt.show(block=False)
                plt.pause(0.001)
                plt.cla()
                if i == self.ngen-1:
                    time.sleep(10)
                    plt.close('all')

        self.run_verbose_end()
        # print(self.globBestFit)
        # Final
        # model = self.globBestFit[0].get_func()[0].get_func()
        # set_source(1, model)
        # plot_fit(1)
        plt.title(f'Final Result')
        # Exit profiler

        plt.legend()
        plt.show

        if self.profile_toggle:
            self.profiler.disable()
            stats = pstats.Stats(self.profiler).sort_stats('cumtime')
            ('Visualze result using Snakeviz')
            stats.dump_stats('Export_Data.txt')


    def output_generations(self):
        """
        Output generations result into two files
        """
        try:
            f1 = open(self.file, "a")
            f1.write(str(self.genNum) + "," + str(self.tdiff) + "," +
                     str(self.currBestFit[1]) + "," + str(self.currBestFit[0].get()) + "," +
                     str(self.globBestFit[1]) + "," + str(self.globBestFit[0].get()) + "\n")
        finally:
            f1.close()
        try:
            f2 = open(self.file_data, "a")
            write = csv.writer(f2)
            bestFit = self.globBestFit[0].get()
            # print(bestFit)
            for i in range(self.npaths):
                write_row_data = []
                for j in range(len(bestFit[i])):
                    write_row_data.append(bestFit[i][j])
                write.writerow(write_row_data)
                # write.writerow((bestFit[i][0], bestFit[i][1], bestFit[i][2], bestFit[i][3]))
            f2.write("#################################\n")
        finally:
            f2.close()

    def __init__(self):
        """
        Steps to Initalize AstroNEO
        """
        # initialize params
        self.initialize_params()
        # variables
        self.initialize_variable()
        # initialze file paths
        self.initialize_file_path()
        # initialize logger
        self.initialize_logger()
        # initialize range
        self.initialize_fits()
        # Generate first generation
        self.generateFirstGen()

        self.run()


def main():

    # profiler = cProfile.Profile()
    # import helper

    # profiler.enable()
    AstroNEO()
    # profiler.disable()
    # stats = pstats.Stats(profiler).sort_stats('cumtime')
    # stats.print_stats()
    # stats.dump_stats('Export_Data.txt')

    # GAMO()


if __name__ == '__main__':
    main()
