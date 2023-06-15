import xspec
import sys, os
xspec.xset.Xset.chatter = 0
sys.path.append("/Users/andy/projects/Astro_Neo/input_files/ACX2")
import acx2_xspec

def init_process():
  """Summary process
  """
  old_dir = os.getcwd()
  data_file = "/Users/andy/projects/Astro_Neo/input_files/astronomy_test/left_pha_grp.fits"
  bg_file = "/Users/andy/projects/Astro_Neo/input_files/astronomy_test/left_mbg.fits"
  rsp_file = "/Users/andy/projects/Astro_Neo/input_files/astronomy_test/left_rmf.fits"

  file_dir = os.chdir('/Users/andy/projects/Astro_Neo/input_files/astronomy_test/')
  xspec.AllData.clear()

  l_src = xspec.Spectrum('left_pha_grp.fits')
  xspec.Plot.xAxis = "angstrom"
  l_src.ignore("**-7.0 30.0-**")

  xspec.AllData.show()

  xspec.Plot.xAxis = "angstrom"
  xspec.Plot.xLog = False
  xspec.Plot.yLog = False
  xspec.Plot.perHz = False
  xspec.Plot.area = True
  xspec.Plot.background = True
  xspec.Fit.statMethod = "cstat"  # using the Cash statistic

def fitness(input):
  """
  Evaluate fitness of a individual

  """
  loss = 0

  indObj = input[0]
  xspec_data = input[1]
  Individual = indObj.get_func()[0]

  Params_list = [2,3,4,7,9,10,11,12,13,19,22,23,38,41,60]

  model_params = Individual.get_pars_dicts(Params_list)

  model = xspec_data.Model("TBabs(TBabs*powerlaw + lsmooth(vapec + vapec + zashift*vacx2))",
                            setPars={1:0.0279, 5:0.02,6:1,21:0.00081,39:0.00081,42:4,43:2,44:2,})

  # Model

  # Tbabs <1>
  # model.TBabs.nH.frozen = True
  # model.TBabs.nH = 0.0279

  # Tbabs <2>

  # Powerlaw <3>

  # lsmooth <4>
  # model.lsmooth.Sig_6keV.frozen = True
  # model.lsmooth.Sig_6keV = 0.02
  # model.lsmooth.Index.frozen = True
  # model.lsmooth.Index = 1

  # vapec <5>
  # model.vapec.C.frozen = False
  # model.vapec.N.frozen = False
  # model.vapec.O.frozen = False
  # model.vapec.Ne.frozen = False
  # model.vapec.Mg.frozen = False
  # model.vapec.Fe.frozen = False
  # self.model.vapec.Redshift.frozen = True
  # model.vapec.Redshift = 0.00081

  # model.vapec.N = 0.990385
  # model.vapec.O = 6.48552e-18
  # model.vapec.Ne = 0.839257
  # model.vapec.Mg = 1.53165
  # model.vapec.Fe = 0.179656
  # self.model.vapec.Redshift.frozen = True
  # model.vapec.Redshift = 0.00081

  # vapec_2 <6>
  model.vapec_6.kT.frozen = False
  model.vapec_6.C.link = model.vapec.C
  model.vapec_6.N.link = model.vapec.N
  model.vapec_6.O.link = model.vapec.O
  model.vapec_6.Ne.link = model.vapec.Ne
  model.vapec_6.Mg.link = model.vapec.Mg
  model.vapec_6.Fe.link = model.vapec.Fe
  model.vapec_6.Redshift.link = model.vapec.Redshift

  # zashift <7>
  # model.zashift.Redshift.frozen = True
  # model.zashift.Redshift = 0.00081

  # vacx2 <8>
  model.vacx2.temperature.link = model.vapec.kT
  model.vacx2.C.link = model.vapec.C
  model.vacx2.N.link = model.vapec.N
  model.vacx2.O.link = model.vapec.O
  model.vacx2.Ne.link = model.vapec.Ne
  model.vacx2.Mg.link = model.vapec.Mg
  model.vacx2.Fe.link = model.vapec.Fe


  # Set up params afterward
  # model.TBabs_2.nH = model_params['TBabs_2_nH']
  # --------
  # model.powerlaw.PhoIndex = model_params['PhoIndex']
  # model.powerlaw.norm = model_params['Pl_norm']
  # --------
  # model.vapec.kT = model_params['vapec_kT']
  # model.vapec.C = model_params['vapec_C']
  # model.vapec.N = model_params['vapec_N']
  # model.vapec.O = model_params['vapec_O']
  # model.vapec.Ne = model_params['vapec_Ne']
  # model.vapec.Mg = model_params['vapec_Mg']
  # model.vapec.Fe = model_params['vapec_Fe']
  # model.vapec.norm = model_params['vapec_norm']
  # --------
  # model.vapec_6.kT = model_params['vapec_6_kT']
  # model.vapec_6.norm = model_params['vapec_6_norm']
  # --------
  # model.vacx2.collnpar = model_params['vacx2_collnpar']
  # model.vacx2.C = model_params['vacx2_C']
  # model.vacx2.N = model_params['vacx2_N']
  # model.vacx2.O = model_params['vacx2_O']
  # model.vacx2.Ne = model_params['vacx2_Ne']
  # model.vacx2.norm = model_params['vacx2_norm']

  model.setPars(model_params)

  # print(self.xspec.Fit.statMethod)
  loss = xspec_data.Fit.statistic
  return loss
