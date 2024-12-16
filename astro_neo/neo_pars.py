import numpy as np
from attr import attr
from attrs import define, field

from astro_neo.helper import time_call
from astro_neo.neo_filepars import NeoFilePars
from astro_neo.utils import checkKey, clamp_checkKey


@define
class NeoBestFit:
    currBestInd: float = None
    currBestVal: float = np.inf
    globBestInd: float = None
    globBestVal: float = np.inf

    bestDiff: float = np.inf
    # diffCounter: int = 0
    bestE0: float = 0

    bestChir_magTotal: np.array = field(default=np.zeros(326))
    bestYTotal: np.array = field(default=np.zeros(326))


@define(kw_only=True, slots=True)
class NeoFixedPars:
    npath: int = 1

    # Neo Fixed Parameters
    nPops: float = 100
    nGen: float = 100
    steadyState: bool = False

    selOpt: int = 0
    croOpt: int = 0

    DE: bool = False

    pathOptimize: bool = False
    pathOptimizePercent: float = 0.01
    pathOptimizeOnly: bool = False
    filter_percentage: float = 0.2

    solver: str = 'GA'

    printGraph: bool = True
    distributed: int = 1
    debug_mode: bool = False

    def read_inputs(self, input_dicts):
        self.npath = checkKey('npath', input_dicts, 1)

        self.nPops = checkKey('nPops', input_dicts, 100)
        self.nGen = checkKey('nGen', input_dicts, 100)
        self.steadyState = checkKey('steadyState', input_dicts, False)

        self.selOpt = checkKey('selOpt', input_dicts, 0)
        self.croOpt = checkKey('croOpt', input_dicts, 0)

        self.DE = checkKey('DE', input_dicts, False)

        self.pathOptimize = checkKey('pathOptimize', input_dicts, False)
        self.pathOptimizePercent = checkKey('pathOptimizePercent', input_dicts, 0.01)
        self.pathOptimizeOnly = checkKey('pathOptimizeOnly', input_dicts, False)
        self.filter_percentage = checkKey('filter_percentage', input_dicts, 0.2)

        self.solver = checkKey('solver', input_dicts, 'GA')

        self.printGraph = checkKey('printGraph', input_dicts, True)
        self.debug_mode = checkKey('debug_mode', input_dicts, False)
        self.distributed = checkKey('distributed', input_dicts, 1)
        if self.printGraph:
            # TODO: Implement this
            # self.fig = plt.figure()
            # self.ax = self.fig.add_subplot(111)
            pass


@define
class NeoRunPars:
    currGen: int = 1
    time: bool = False
    tt: float = 0
    diffCounter: int = 0
    cycles: int = 0
    currGen_st: float = 0
    currGen_tt: float = 0
    nGen: int = 100

    def start_gen(self):
        self.currGen_st = time_call()

    def end_gen(self, neo_population):
        self.currGen += 1
        self.tt += self.currGen_tt

    def calc_curr_gen_time(self):
        self.currGen_tt = time_call() - self.currGen_st

    def read_inputs(self, input_dicts):
        self.nGen = checkKey('nGen', input_dicts, 100)


@define
class NeoMutPars:
    """
    Neo Mutation Parameters
    """
    mutOpt: int = 1
    mutChance: float = field(default=0.3)
    mutChanceE0: float = field(default=0.3)
    mutCR: float = field(default=0.9)
    mutF: float = field(default=0.8)
    nmut: int = 0

    def read_inputs(self, input_dicts):
        self.mutOpt = checkKey('mut_options', input_dicts, 1)
        self.mutChance = checkKey('mutChance', input_dicts, 0.3)
        self.mutChanceE0 = checkKey('mutChanceE0', input_dicts, 0.3)
        self.mutCR = clamp_checkKey('mutCR', input_dicts, 0.9, [0.0, 1.0])
        self.mutF = clamp_checkKey('mutF', input_dicts, 0.8, [0.0, 2.0])

    @mutChance.validator
    def check_mutchance(self, attribute, value):
        if value > 1.0 or value < 0.0:
            raise ValueError("mutChance should be between 0 and 1")

    @mutCR.validator
    def check_mutCR(self, attribute, value):
        if value > 1.0 or value < 0.0:
            raise ValueError("mutCR should be between 0 and 1")

    @mutF.validator
    def check_mutF(self, attribute, value):
        if value > 2.0 or value < 0.0:
            raise ValueError("mutF should be between 0 and 1")


@define
class NeoCrossPars:
    croOpt: int = 0

    def read_inputs(self, input_dicts):
        self.croOpt = checkKey('croOpt', input_dicts, 0)


@define
class NeoSelPars:
    """
    Neo Selection Parameters
    """
    selOpt: int = 0
    nBestSample: float = 0.3
    nLuckSample: float = 0.2

    parents: list = field(factory=list)
    __nPop: int = 0
    nBest: int = 0
    nLuck: int = 0
    nCross: int = 0

    def read_inputs(self, input_dicts):
        self.selOpt = checkKey('selOpt', input_dicts, 0)
        self.nBestSample = checkKey('nBestSample', input_dicts, 0.3)
        self.nLuckSample = checkKey('nLuckSample', input_dicts, 0.2)
        self.__nPop = checkKey('nPops', input_dicts, 100)
        self.nBest = int(self.__nPop * self.nBestSample)
        self.nLuck = int(self.__nPop * self.nLuckSample)
        self.nCross = self.__nPop - self.nBest - self.nLuck


@define
class NeoSol:
    solOpt: int = 0

    def read_inputs(self, input_dicts):
        self.solOpt = checkKey('solver_type', input_dicts, 0)


class NeoPars:
    def __init__(self, verbose_lvl=5):
        """
        Wrapped all paras together
        """

        self.verbose_lvl = verbose_lvl
        self.fixedPars = NeoFixedPars()
        self.runPars = NeoRunPars()
        self.mutPars = NeoMutPars()
        self.crossPars = NeoCrossPars()
        self.selPars = NeoSelPars()
        # self.exafsPars = NeoStaticPars()
        self.bestFitPars = NeoBestFit()
        self.neoFilePars = NeoFilePars()
        # self.exafsRangePars = EXAFSPathRange()
        self.neo_paths = NeoPath()
        self.solPars = NeoSol()

    def read_inputs(self, input_dicts):
        self.fixedPars.read_inputs(input_dicts)
        self.runPars.read_inputs(input_dicts)
        self.neo_paths.read_inputs(input_dicts)
        self.neoFilePars.read_inputs(input_dicts)
        self.mutPars.read_inputs(input_dicts)
        self.selPars.read_inputs(input_dicts)
        self.solPars.read_inputs(input_dicts)
        self.crossPars.read_inputs(input_dicts)
        self.neoFilePars.initialize_filepath()

        # self.exafsPathPars.read_inputs(self.neoFilePars, self.exafsPars)

        # self.exafsPathPars.initialize()

    def output(self):
        self.neoFilePars.write_outputs(self.runPars, self.bestFitPars)
        self.neoFilePars.write_data_outputs(self.bestFitPars)

    def end_gen(self, neo_population):
        self.runPars.end_gen(neo_population)
        self.output()


@define(slots=True)
class NeoStaticPars:
    """

    """

    def read_inputs(self, input_dicts):
        pass
        # self.kmin = checkKey('kmin', input_dicts, 0.95)
        # self.kmax = checkKey('kmax', input_dicts, 9.775)
        # self.dk = checkKey('deltak', input_dicts, 0.05)
        # self.kweight = checkKey('kweight', input_dicts, 2.0)
        #
        # self.rbkg = checkKey('rbkg', input_dicts, 0.0)
        # self.bkgkw = checkKey('bkgkw', input_dicts, 1.0)
        # self.bkgkmax = checkKey('bkgkmax', input_dicts, 15.0)
        #
        # self.pathrange = checkKey('pathrange', input_dicts, None)
        # self.individual_paths = checkKey('individualOptions', input_dicts, False)
        # self.npath = checkKey('npath', input_dicts, 1)
        # self.calculate_pars()


@define
class NeoPath:
    npaths: int = 1
    fits: list = field(factory=list)
    center: list = field(factory=list)

    def read_inputs(self, input_dicts):
        self.npaths = checkKey('npath', input_dicts, 1)
        self.fits = checkKey('fits', input_dicts, ['XspecSpectrum'] * self.npaths)
        self.center = checkKey('center', input_dicts, [0] * self.npaths)


if __name__ == "__main__":
    # exafs_pars = EXAFSPars()
    # inputs_pars = {'data_file': '../path_files/Cu/cu_10k.xmu', 'output_file': '',
    #                'feff_file': '../path_files/Cu/path_75/feff', 'kmin': 0.95,
    #                'kmax': 9.775,
    #                'kweight': 3.0, 'pathrange': [1, 2, 3, 4, 5],
    #                'deltak': 0.05, 'rbkg': 1.1, 'bkgkw': 1.0, 'bkgkmax': 15.0}

    # exafs_NeoPars = NeoFilePars()
    #
    # exafs_NeoPars.read_inputs(inputs_pars)
    # exafs_NeoPars.initialize_filepath()
    # print(exafs_NeoPars)
    # astro_NeoPars = NeoPars()
    # astro_NeoPars.read_inputs(inputs_pars)

    # print(astro_NeoPars)
    # print(exafs_NeoPars.exafsPathPars)

    neo_mut_pars = NeoMutPars(mutCR=0.5)
    inputs_pars = {"mut_options": 1}
    neo_mut_pars.read_inputs(input_dicts=inputs_pars)
