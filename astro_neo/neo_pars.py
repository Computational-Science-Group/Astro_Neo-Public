from attrs import define, field
import numpy as np

from astro_neo.helper import time_call
from astro_neo.neo_filepars import NeoFilePars
from astro_neo.utils import checkKey


# from exafs_neo.pathrange import Pathrange_limits, read_pathrange_file

# from exafs_neo.neoFilePars import NeoFilePars
# from exafs_neo.utils import checkKey, time_call


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
    debug_mode: bool = False

    def read_inputs(self, input_dicts):
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
        self.currGen_tt = time_call() - self.currGen_st
        self.tt += self.currGen_tt

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
    nmut: int = 0

    def read_inputs(self, input_dicts):
        self.mutOpt = checkKey('mut_options', input_dicts, 1)
        self.mutChance = checkKey('mutChance', input_dicts, 0.3)
        self.mutChanceE0 = checkKey('mutChanceE0', input_dicts, 0.3)

    @mutChance.validator
    def check_mutchance(self, attribute, value):
        if value > 1.0 or value < 0.0:
            raise ValueError("mutChance should be between 0 and 1")


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
        self.exafsPars = NeoStaticPars()
        self.bestFitPars = NeoBestFit()
        self.neoFilePars = NeoFilePars()
        # self.exafsRangePars = EXAFSPathRange()
        self.exafsPathPars = EXAFSPath()
        self.solPars = NeoSol()

    def read_inputs(self, input_dicts):
        self.fixedPars.read_inputs(input_dicts)
        self.runPars.read_inputs(input_dicts)
        self.exafsPars.read_inputs(input_dicts)
        self.neoFilePars.read_inputs(input_dicts)
        self.mutPars.read_inputs(input_dicts)
        self.selPars.read_inputs(input_dicts)
        self.solPars.read_inputs(input_dicts)
        self.crossPars.read_inputs(input_dicts)
        self.neoFilePars.initialize_filepath(cycles=0)

        self.exafsPathPars.read_inputs(self.neoFilePars, self.exafsPars)

        self.exafsPathPars.initialize()

    def output(self):
        self.neoFilePars.write_outputs(self.runPars, self.bestFitPars)
        self.neoFilePars.write_data_outputs(self.bestFitPars)

    def end_gen(self, neo_population):
        self.output()
        self.runPars.end_gen(neo_population)


@define(slots=True)
class NeoStaticPars:
    kmin: float = 0.95
    kmax: float = 9.775
    dk: float = 0.05
    kweight: float = 2.0

    rbkg: float = 0.0
    bkgkw: float = 1.0
    bkgkmax: float = 15.0

    small: float = 0.0
    big: float = 0.0
    mid: float = 0.0
    intervalK: list = field(factory=list)

    individual_paths: bool = False

    pathrange: list = field(factory=list)
    npath: int = 0

    def calculate_pars(self):
        self.small = int(self.kmin / self.dk)
        self.big = int(self.kmax / self.dk)
        self.mid = int(self.big - self.small + 1)
        self.intervalK = np.linspace(self.small, self.big, self.mid)

    def read_inputs(self, input_dicts):
        self.kmin = checkKey('kmin', input_dicts, 0.95)
        self.kmax = checkKey('kmax', input_dicts, 9.775)
        self.dk = checkKey('deltak', input_dicts, 0.05)
        self.kweight = checkKey('kweight', input_dicts, 2.0)

        self.rbkg = checkKey('rbkg', input_dicts, 0.0)
        self.bkgkw = checkKey('bkgkw', input_dicts, 1.0)
        self.bkgkmax = checkKey('bkgkmax', input_dicts, 15.0)

        self.pathrange = checkKey('pathrange', input_dicts, None)
        self.individual_paths = checkKey('individualOptions', input_dicts, False)
        self.npath = len(self.pathrange)
        self.calculate_pars()


@define
class EXAFSPath:
    # mylarch: str = Interpreter()
    # g: larch.symboltable.Group = None
    # best: larch.symboltable.Group = None
    # sumgroup: larch.symboltable.Group = None
    exp: list = field(factory=list)
    pathname: list = field(factory=list)
    ncomp: int = 0
    individual_paths: bool = False
    path_lists: list = field(factory=list)
    pathDictionary: dict = field(factory=dict)

    # def initialize(self):
    # self.read_inputs(exafs_neo)

    end: str = None
    front: list = field(factory=list)
    npaths: int = None
    exafs_static_pars: NeoStaticPars = None
    exafs_file_pars: NeoFilePars = None

    def read_inputs(self, exafs_filepars: NeoFilePars, exafs_static_pars: NeoStaticPars):
        self.exafs_file_pars = exafs_filepars
        self.exafs_static_pars = exafs_static_pars
        # self.g = read_ascii(str(exafs_filepars.data_path))
        # self.best = read_ascii(str(exafs_filepars.data_path))
        # self.sumgroup = read_ascii(str(exafs_filepars.data_path))
        self.ncomp = exafs_filepars.nComp
        self.individual_paths = exafs_static_pars.individual_paths
        self.npaths = exafs_static_pars.npath
        self.front = exafs_filepars.front
        self.end = exafs_filepars.end
        self.path_lists = exafs_static_pars.pathrange

    def initialize(self):
        # self.__initialize_group()
        # self.__initialize_paths()
        # self.__initialize_ftf()
        pass


if __name__ == "__main__":
    # exafs_pars = EXAFSPars()
    inputs_pars = {'data_file': '../path_files/Cu/cu_10k.xmu', 'output_file': '',
                   'feff_file': '../path_files/Cu/path_75/feff', 'kmin': 0.95,
                   'kmax': 9.775,
                   'kweight': 3.0, 'pathrange': [1, 2, 3, 4, 5],
                   'deltak': 0.05, 'rbkg': 1.1, 'bkgkw': 1.0, 'bkgkmax': 15.0}

    # exafs_NeoPars = NeoFilePars()
    #
    # exafs_NeoPars.read_inputs(inputs_pars)
    # exafs_NeoPars.initialize_filepath()
    # print(exafs_NeoPars)
    astro_NeoPars = NeoPars()
    astro_NeoPars.read_inputs(inputs_pars)

    print(astro_NeoPars)
    # print(exafs_NeoPars.exafsPathPars)
