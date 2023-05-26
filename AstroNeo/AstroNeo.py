from .helper import *
from .import_lib import *
from .ini_parser import *
# from larch import Interpreter
from .pathObj import VoigtObj
from .individual import Individual, BackgroundObj
from .pathrange import Pathrange_limits
from .background_function import shirley, nobg, shirley_temp
from .voigt_shape import voigt_fuc
import cProfile
import pstats

# from .run_verbose import *


class AstroNEO:

    def initialize_params(self, verbose=False):
        """
        Initialize Parameters
        """

        print("Initialize Parameters")
        self.intervalK = 0.05

    def initialize_variable(self):
        """
        Initalize variables
        """
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
        self.data_file = data_file
        # self.fits_file = fits_file
        # print(self.fits_file)
        # Paths
        self.npaths = npaths
        self.fits = fits.split(",")

        self.center = center
        # self.corr = corr
        # self.corr_list = corr_list

        # Populations
        self.npops = size_population
        self.ngen = number_of_generation
        self.steady_state = steady_state

        # Mutation Parameters
        self.mut_opt = mutated_options
        self.mut_chance = chance_of_mutation
        # self.mut_chance_e0 = chance_of_mutation_e0

        # Crosover Parameters
        self.n_bestsam = int(best_sample*self.npops*(0.01))
        self.n_lucksam = int(lucky_few*self.npops*(0.01))

        # Time related
        self.time = False
        self.tt = 0

        # Figure related:
        self.printgraph = printgraph
        if self.printgraph:
            self.fig = plt.figure()
            # Add one figs
            self.ax = self.fig.add_subplot(111)
        # Profile related:
        self.profile_toggle = profile
        if self.profile_toggle:
            self.profiler = cProfile.Profile()
            self.profiler.enable()

        # CSV-Series check
        # self.csv_percent = 0.2
    # def reinitialize_varshirleiable():
    #     self.genNum = 0
    #     self.globBestFit = [0,99999]
    #     self.currBestFit = [0,99999]
    #     self.bestDiff = 9999
    #     self.bestBest = 999999999
    #     self.diffCounter = 0

    def initialize_file_path(self, i=0):
        """
        Initalize file paths for each of the file first
        """
        # self.csv_series = csv_series
        self.base = os.getcwd()
        # self.front = os.path.join(self.base,feff_file)
        # self.front = self.base
        # print(output_file)
        # if self.csv_series == True:
        # self.data_path = os.path.join(self.base,csv_file[i])
        # self.output_path = os.path.splitext(os.path.join(self.base,output_file))[0] + "_" + str(i) + ".csv"
        # os.path.splitext(file)[0] + '_data.csv'
        # else:
        # self.data_path = os.path.join(self.base,csv_file)
        # self.output_path = os.path.join(self.base,output_file)
        # self.end ='.dat'
        self.output_path = os.path.join(self.base, output_file)
        self.check_output_file(self.output_path)

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
        # file = 'data/G130M_G160M.fits'
        # file = {}
        # file['fits'] = '/Users/andy/projects/Astro_Neo/input_files/uv/data/left_pha_grp.fits'
        # file['rsp'] = '/Users/andy/projects/Astro_Neo/input_files/uv/data/left_rmf.fits'
        # sherpa.astro.ui.load_pha(1, file['fits'], use_errors=True)
        # load_rmf(1, file['rsp'])
        # set_analysis(1, "wave")  # set the analysis methods
        # notice_id(1, 7, 30)  # select the spectrum between 7 to 30

        # set_method('levmar')
        # set_xsabund('angr')
        # set_xsxsect('vern')
        # set_xscosmo(70, 0, 0.73)

        old_dir = os.getcwd()
        print(old_dir)
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

        self.xspec.Plot("data")
        # xspec.AllModels.setEnergies("xbin.txt")   #using the specified energy bins

        # l_folded = xspec.Plot.model()
        self.l_chans = xspec.Plot.x()
        self.l_rates = xspec.Plot.y()
        self.l_xErrs = xspec.Plot.xErr()
        self.l_yErrs = xspec.Plot.yErr()
        self.l_bkg = xspec.Plot.backgroundVals()


        print(np.min(self.l_chans))
        # os.chdir(old_dir)

        # set_stat("chi2xspecvar")

    def initialize_range(self, i=0, BestIndi=None):
        """
        Initalize range

        To Do list:
            Initalize range will be difference for each paths depend if the run are
            in series, therefore the ranges will self-adjust
        """

        # print(self.path_lists)
        # print("Initialize Range")
        """
        if i == 0:
            self.pathrange_Dict = []
            for i in self.path_lists:
                self.pathrange_Dict.append(Pathrange_limits(i))

            # print(self.pathrange_Dict)
            # sys.exit()
            # test = self.pathrange_Dict[-1]
            # print(test)
            # print(test.get_paths())
            # print(test.get_rangeS02())
            #
            self.dt_S02 = [0.01,2]
            self.dt_Sigma2 = [0.001,2]
            self.dt_DeltaR = [0.01,2]
            # sys.exit()
            # self.rangeS02 = (np.linspace(5, 95, 91) * 0.01)  # <- should be separate
            self.rangeE0 = (np.linspace(-100, 100, 201) * \
                            0.01) # <- e0, for everything
            # <- Larger range B
            self.rangeE0_large = (np.linspace(-600, 600, 1201) * 0.01)
        """

        # data = np.loadtxt(self.data_file, delimiter=',', skiprows=1)
        # print(data[:,0])
        # self.x_raw = data[:, 0]
        # self.y_raw = data[:, 1]

        # print(data[:,1])
        # print(self.x_raw)
        # print(self.y_raw)
        # plt.plot(self.x_raw,self.y_raw)
        # plt.show()
        # Background subtraction
        # self.intitalize_fits()

        # self.bg = nobg(self.x_raw, self.y_raw)
        # # self.Bg_obj = Background_Obj(1,'ShirleyExp')
        # # self.bg = shirley(self.x_raw,self.y_raw)
        # # self.
        # self.y_background = self.y_raw - self.bg
        # self.center_range = [np.min(self.x_raw), np.max(self.x_raw)]

        # self.y_scaler = MinMaxScaler()
        # self.y_normal = self.y_scaler.fit_transform(
        #     self.y_background.reshape(-1, 1))

        # self.x_scaler = MinMaxScaler()
        # self.x_normal = self.x_scaler.fit_transform(self.x_raw.reshape(-1, 1))

    def create_range(self, value, percentage, dt, prec):
        minus = round(value - percentage*value, prec)
        plus = round(value + percentage*value, prec)
        range = np.arange(minus, plus+dt, dt)
        return range

    def generateIndividual(self):
        # self.fits = 'Test'
        # self.center = ''
        ind = Individual(self.npaths, self.fits, self.center)
        # sys.exit()
        return ind

    def generateFirstGen(self):
        self.Populations = []

        for i in range(self.npops):
            self.Populations.append(self.generateIndividual())

    def fitness(self, indObj):
        """
        Evaluate fitness of a individual

        To do
        """
        loss = 0

        Individual = indObj.get_func()[0]

        model_params = Individual.get_func()

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


        loss = self.xspec.Fit.statistic
        # yTotal = np.zeros(len(self.x_raw))

        # for i, paths in enumerate(Individual):
        #     y = paths.get_func(self.x_raw, self.y_normal)
        #     # print(y.shape)
        #     yTotal += y
        # # Least Square
        # for j in range(len(self.x_normal)):
        #     loss = loss + (yTotal[j]*self.x_raw[j] **
        #                    2 - self.y_normal[j] * self.x_raw[j]**2)**2
        # print(Individual)
        # set_source(1, model)

        # loss = (get_staterror(1, filter=True))
        # loss = get_stat_info()[0].statval
        # print(loss)
        return loss

    def eval_Population(self):
        """Evaluate the population for GA

        Returns:
            _type_: _description_
        """

        score = []
        populationPerf = {}

        for i, individual in enumerate(self.Populations):

            temp_score = self.fitness(individual)
            score.append(temp_score)

            populationPerf[individual] = temp_score

        self.sorted_population = sorted(
            populationPerf.items(), key=operator.itemgetter(1), reverse=False)

        self.currBestFit = self.sorted_population[0]

        return score

    def next_generation(self):
        """Next Generation for GA
        """
        self.st = time.time()
        # ray.init()
        print("---------------------------------------------------------")
        print(datetime.datetime.fromtimestamp(
            self.st).strftime('%Y-%m-%d %H:%M:%S'))
        print(f"{bcolors.BOLD}Gen: {bcolors.ENDC}{self.genNum+1}")

        self.genNum += 1

        # Evaluate Fittness
        score = self.eval_Population()
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

        with np.printoptions(precision=5, suppress=True):
            print(
                f"Best Fit: {bcolors.BOLD}{self.sorted_population[0][1]}{bcolors.ENDC}")
            print(f"2nd Fit: {self.sorted_population[1][1]}")
            print(f"3rd Fit: {self.sorted_population[2][1]}")
            print(f"4th Fit: {self.sorted_population[3][1]}")
            print(f"Last Fit: {self.sorted_population[-1][1]}")
            print(f"Different from last best fit: {self.bestDiff}")
            # print(bcolors.BOLD + "Best fit :", bcolors.OKBLUE +
            #       str(self.currBestFit[1]) + bcolors.ENDC)
            # CurrchiR = self.currBestFit[1]/(len(self.x_raw)-4*self.npaths)
            # print(bcolors.BOLD + "Best fit ChiR:",
            #       bcolors.OKBLUE + str(CurrchiR) + bcolors.ENDC)

            print("Best fit combination:\n",
                  np.asarray(self.currBestFit[0].get()))
            print(bcolors.BOLD + "History Best:", bcolors.OKBLUE +
                  str(self.globBestFit[1]) + bcolors.ENDC)
            # GlobchiR = self.globBestFit[1]/(len(self.x_raw)-4*self.npaths)
            # print(bcolors.BOLD + "History Best ChiR:",
            #       bcolors.OKBLUE + str(GlobchiR) + bcolors.ENDC)
            # print("History Best Indi:\n", np.asarray(
            #     self.globBestFit[0].get()))

        nextBreeders = self.selectFromPopulation()
        self.createChildren()
        print(f"Number of Breeders: {str(len(self.parents))}")
        print(f"DiffCounter: {self.diffCounter}")
        print(f"Diff %: {self.diffCounter / self.genNum}")
        print(f"Mutation Chance: {self.mut_chance}")
        self.mutatePopulation()

        self.et = timecall()
        self.tdiff = self.et - self.st
        self.tt = self.tt + self.tdiff
        print(f"Time: {str(round(self.tdiff, 5))} s")

    def mutatePopulation(self):
        """
        # Mutation operators
        # 0 = original: generated a new versions:
        # 1 = mutated every genes in the total populations
        # 2 = mutated genes inside population based on secondary probability

        # TODO:
            options 2 and 3 needs to reimplmented
        """
        self.nmutate = 0

        if self.mut_opt == 0:
            for i in range(self.npops):
                if random.random()*100 < self.mut_chance:
                    self.nmutate += 1
                    self.Populations[i] = self.mutateIndi()

        # if self.mut_opt == 1:

        # if random.random() * 100 < self.mut_chance_e0:
        #     e0 = random.choice(self.rangeE0)
        #     print("Mutate e0 to:", e0)
        #     for individual in self.Populations:
        #         individual.set_e0(e0)
        print("Mutate Times:", self.nmutate)
        """
        if mutated_options == 1:
            for i in range(len(population)):
                for j in range(len(population[i])):
                    if random.random() * 100 < chance_of_mutation:
                        mutateTime += 1
                        if j == 0:
                            mutate_val = random.choice(rangeA)
                            population[i][j] == mutate_val
                        if j == 2:
                            mutate_val = random.choice(rangeC)
                            population[i][j] == mutate_val
                        if j == 3:
                            mutate_val = random.choice(rangeD)
                            population[i][j] == mutate_val

        if mutated_options == 2:
            for i in range(len(population)):
                if random.random() * 100 < chance_of_mutation:
                    for j in range(len(population[i])):
                        if random.random() * 100 < chance_gene_mut:
                            mutateTime += 1
                            if j == 0:
                                mutate_val = random.choice(rangeA)
                                population[i][j] == mutate_val
                            if j == 2:
                                mutate_val = random.choice(rangeC)
                                population[i][j] == mutate_val
                            if j == 3:
                                mutate_val = random.choice(rangeD)
                                population[i][j] == mutate_val
        """

    def mutateIndi(self):
        """
        Generate new individual during mutation operator
        """
        mutatIndi = self.generateIndividual()
        return mutatIndi

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
        print("-----------Inputs File Stats---------------")
        print(f"{bcolors.BOLD}File{bcolors.ENDC}: {self.data_file}")
        print(f"{bcolors.BOLD}File{bcolors.ENDC}: {self.output_path}")
        # print(f"{bcolors.BOLD}CSV series{bcolors.ENDC}: {self.csv_series}")
        print(f"{bcolors.BOLD}Population{bcolors.ENDC}: {self.npops}")
        print(f"{bcolors.BOLD}Num Gen{bcolors.ENDC}: {self.ngen}")
        print(f"{bcolors.BOLD}Num Path{bcolors.ENDC}: {self.npaths}")
        print(f"{bcolors.BOLD}Fits{bcolors.ENDC}: {self.fits}")
        # print(f"{bcolors.BOLD}Path{bcolors.ENDC}: {self.path_lists}")
        # print(f"{bcolors.BOLD}Path Optimize{bcolors.ENDC}: {self.}")
        print(f"{bcolors.BOLD}Printout{bcolors.ENDC}: {self.printgraph}")
        print(f"{bcolors.BOLD}profiler{bcolors.ENDC}: {self.profile_toggle}")
        # print(f"{bcolors.BOLD}Steady State{bcolors.ENDC}: {steady_state}")
        # print(f"{bcolors.BOLD}Output Paths{bcolors.ENDC}: {num_output_paths}")
        print("-------------------------------------------")

    def run_verbose_end(self):
        """Generate verbose output at the end
        """
        print("-----------Output Stats---------------")
        print(f"{bcolors.BOLD}Total Time(s){bcolors.ENDC}: {round(self.tt,4)}")
        # print(f"{bcolors.BOLD}File{bcolors.ENDC}: {self.data_path}")
        # print(f"{bcolors.BOLD}{bcolors.ENDC}: {self.npops}")
        # print(f"{bcolors.BOLD}Num Gen{bcolors.ENDC}: {self.ngen}")
        # print(f"{bcolors.BOLD}Num Path{bcolors.ENDC}: {self.npaths}")
        # print(f"{bcolors.BOLD}Path{bcolors.ENDC}: {self.path_lists}")
        print("-------------------------------------------")

    def active_background(self, indObj):
        if self.genNum % 5 == 0 and self.genNum > 1:
            # 1. Inverse transfer
            # construct new background using the bestfit
            Individual = indObj.get_func()
            yTotal = np.zeros(len(self.x_raw))
            for i, paths in enumerate(Individual):
                y = paths.get_func(self.x_raw)
                yTotal += y
            self.bg = shirley_temp(self.x_raw, yTotal)
            self.y_background = self.y_raw - self.bg
            # self.y_scaler = MinMaxScaler()
            self.y_normal = self.y_scaler.fit_transform(
                self.y_background.reshape(-1, 1))

            file_name = 'array' + str(self.genNum/10) + ".txt"
            out_array = np.concatenate(
                (self.x_raw.reshape(-1, 1), self.bg.reshape(-1, 1)), axis=1)

            np.savetxt(file_name, out_array, delimiter=',')



    def run(self):
        self.run_verbose_start()
        self.historic = []
        self.historic.append(self.Populations)
        for i in range(self.ngen):
            # self.active_background(self.globBestFit[0])
            temp_gen = self.next_generation()
            self.output_generations()
            if printgraph:
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
                # set_source(1, model)

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
        if self.profile_toggle:
            self.profiler.disable()
            stats = pstats.Stats(self.profiler).sort_stats('cumtime')
            ('Visualze result using Snakeviz')
            stats.dump_stats('Export_Data.txt')

        plt.legend()
        plt.show()

    def fwhm(self, indObj):
        fg = 2*indObj.get_sigma() * np.sqrt(2*np.log(2))
        fl = 2*indObj.get_gamma()
        fv = 0.5346 * fl + np.sqrt(0.2166*fl**2 + fg**2)
        return (fg, fl, fv)

    def export_paths(self, indObj):
        area_list = []
        Individual = indObj.get_func()
        # print(type(indObj))
        yTotal = np.zeros(len(self.x_raw))
        for i, paths in enumerate(Individual):
            y = paths.get_func(self.x_raw, self.y_normal)

            yTotal += y
            area = np.trapz(y.flatten(), x=self.x_normal.flatten())
            y_peak = self.y_scaler.inverse_transform(
                y.reshape(-1, 1)).flatten() + self.bg
            self.ax.plot(self.x_scaler.inverse_transform(
                self.x_normal.reshape(-1, 1)), y_peak, label='peak' + str(i))

            area_list.append(area)

        Total_area = np.sum(area_list)
        print(area_list/Total_area)
        return yTotal

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
        # initialize range
        self.initialize_fits()
        # Generate first generation
        self.generateFirstGen()

        self.run()


def main():

    # profiler = cProfile.Profile()

    # profiler.enable()
    AstroNEO()
    # profiler.disable()
    # stats = pstats.Stats(profiler).sort_stats('cumtime')
    # stats.print_stats()
    # stats.dump_stats('Export_Data.txt')

    # GAMO()
