# from dataclasses import dataclass, field
from pathlib import Path

from attrs import define, field

from astro_neo.utils import checkKey


@define
class NeoFilePars:
    data_dir: Path = Path.cwd()
    data_file: str = ''
    bg_file: str = ''
    rsp_file: str = ''
    output_file: Path = ''
    output_datafile: Path = ''
    log_file: str = 'test.csv'

    firstPass: bool = False
    multi_data_toggle: bool = False
    multi_data: list = field(factory=list)
    nComp: int = 1

    front: list = field(factory=list)

    data_path: Path = None
    bg_path: Path = None
    rsp_path: Path = None
    output_path: Path = None
    log_path: Path = None

    pathOptimize: bool = False
    end: str = ".dat"

    def initialize_filepath(self):
        """
        Initialize File Path
        @return:
        """
        self.data_path = self.data_dir / self.data_file
        self.bg_path = self.data_dir / self.bg_file
        self.rsp_path = self.data_dir / self.rsp_file
        self.output_path = self.data_dir / self.output_file
        self.log_path = Path(str(self.output_path.with_suffix('')) + ".log")

        self.initialize_outputs()

    def read_inputs(self, input_dicts):
        """

        """
        self.data_dir = checkKey('data_dir', input_dicts, Path.cwd())
        if isinstance(self.data_dir, str):
            self.data_dir = Path(self.data_dir)
        self.data_file = checkKey('data_file', input_dicts, '')
        self.bg_file = checkKey('bg_file', input_dicts, 'bg_file.fits')
        self.rsp_file = checkKey('rsp_file', input_dicts, 'rsp_file.fits')
        self.output_file = checkKey('output_file', input_dicts, 'neo_out.csv')
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
        globBestFit = bestFitPars.globBestInd.get_model().get_params()
        with open(self.output_datafile, "a") as f2:
            # bestFit = globBestFit
            for key, value in sorted(globBestFit.items()):
                line = f"{key},{round(value,4)}\n"
                f2.writelines(line)
            f2.write("#################################\n")


if __name__ == "__main__":
    # exafs_pars = EXAFSPars()
    inputs_pars = {'data_dir': '/Users/andy/projects/Astro_Neo', 'data_file': 'path_files/Cu/cu_10k.xmu',
                   'output_file': 'tests/output.csv', 'feff_file': 'test/feff',
                   'kmin': 0.95,
                   'kmax': 9.775,
                   'kweight': 3.0,
                   'deltak': 0.05, 'rbkg': 1.1, 'bkgkw': 1.0, 'bkgkmax': 15.0, 'pathOptimize': False}

    exafs_NeoPars = NeoFilePars()

    exafs_NeoPars.read_inputs(inputs_pars)
    exafs_NeoPars.initialize_filepath()
    print(exafs_NeoPars)
