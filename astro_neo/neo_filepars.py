# from dataclasses import dataclass, field
from attrs import define, field

from pathlib import Path

from astro_neo.utils import checkKey


@define
class NeoFilePars:
    base: str = Path.cwd()
    data_file: str = ''
    output_file: Path = ''
    output_datafile: Path = ''
    feff_file: list = field(factory=list)
    log_file: str = 'test.csv'

    firstPass: bool = False
    multi_data_toggle: bool = False
    multi_data: list = field(factory=list)
    nComp: int = 1

    front: list = field(factory=list)

    data_path: Path = None
    output_path: Path = None
    log_path: Path = None

    pathOptimize: bool = False
    end: str = ".dat"

    def initialize_filepath(self):
        """
        Initialize File Path
        @return:
        """
        self.data_path = self.base / self.data_file
        self.output_path = self.base / self.output_file
        self.log_path = Path(str(self.output_path.with_suffix('')) + ".log")

        self.initialize_outputs()

    def read_inputs(self, input_dicts):
        """

        """

        self.data_file = checkKey('data_file', input_dicts, '')
        self.output_file = checkKey('output_file', input_dicts, 'exafs_neo_out.csv')
        self.log_file = checkKey('log_file', input_dicts, 'exafs_neo.log')
        self.pathOptimize = checkKey('pathOptimize', input_dicts, False)

    def initialize_outputs(self):
        """

        """
        base_file = self.output_path.stem
        self.output_datafile = self.output_path.with_name(f'{base_file}_data.csv')

    def write_outputs(self, neoRunPars, bestFitPars):

        with open(self.output_path, "a") as f1:
            data_line = f"{neoRunPars.currGen},{neoRunPars.tt},{bestFitPars.globBestVal}\n"
            f1.writelines(data_line)

    def write_data_outputs(self, bestFitPars):
        globBestFit = bestFitPars.globBestInd.get()
        with open(self.output_datafile, "a") as f2:
            bestFit = globBestFit
            for path in bestFit:
                line = f"{path[0]},{path[1]},{path[2]},{path[3]}\n"
                f2.writelines(line)
            f2.write("#################################\n")


if __name__ == "__main__":
    # exafs_pars = EXAFSPars()
    inputs_pars = {'data_file': 'path_files/Cu/cu_10k.xmu', 'output_file': 'tests/output.csv', 'feff_file': 'test/feff',
                   'kmin': 0.95,
                   'kmax': 9.775,
                   'kweight': 3.0,
                   'deltak': 0.05, 'rbkg': 1.1, 'bkgkw': 1.0, 'bkgkmax': 15.0, 'pathOptimize': False}

    exafs_NeoPars = NeoFilePars()

    exafs_NeoPars.read_inputs(inputs_pars)
    exafs_NeoPars.initialize_filepath()
    print(exafs_NeoPars)