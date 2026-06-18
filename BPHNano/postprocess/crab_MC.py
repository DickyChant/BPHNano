import sys

# if using this file directly
from CRABClient.UserUtilities import config
config = config()

config.section_("General")
config.General.requestName = 'NanoPost_2022_MC_2026Jan14'
config.General.workArea = '/afs/cern.ch/work/y/yilai/gamma/crab_projects_MC_upsilon_'+config.General.requestName
config.General.transferLogs = True

config.section_("JobType")
config.JobType.pluginName = 'Analysis'
year = "2022pre"

if "2022pre" in year:
    config.JobType.psetName = "test_mc_22preEE.py"
if "2022post" in year:
    config.JobType.psetName = "test_mc_22postEE.py"
if "2023pre" in year:
    config.JobType.psetName = "test_mc_23preEE.py"
if "2023post" in year:
    config.JobType.psetName = "test_mc_23postEE.py"

#config.JobType.psetName = 'PSet.py'
config.JobType.scriptExe = 'crab_script_mc.sh'
config.JobType.scriptArgs = []
config.JobType.inputFiles = ['BPH_postproc_mc.py', 'test_mc_22preEE.py', "test_mc_22postEE.py", 'test_mc_23preEE.py', "test_mc_23postEE.py"]
config.JobType.outputFiles = ['test_mc_Skim.root']
#config.JobType.sendPythonFolder = True
config.section_("Data")
#config.Data.inputDataset = '/BuToD0K_D0ToKs2Pi_Run3/yilai-Run3Summer22_MiniAODv4-5443ed9e0a49f9c5d5f0b2fff4804347/USER'
#config.Data.inputDataset = '/LambdaBToJpsiLambda_JpsiFilter_MuFilter_LambdaFilter_TuneCP5_13p6TeV_pythia8-evtgen/Run3Summer22MiniAODv4-130X_mcRun3_2022_realistic_v5-v2/MINIAODSIM'
#config.Data.inputDataset = '/LambdaBToJpsiLambda_Unbiased_TuneCP5_13p6TeV_pythia8-evtgen/Run3Summer22EEMiniAODv4-130X_mcRun3_2022_realistic_postEE_v6-v2/MINIAODSIM'
#config.Data.inputDataset = '/lambdab_lambda2K_2/yilai-Run3Summer22_MiniAODv4-9542347e91aacc6744c44ee907c98ff2/USER'
#config.Data.inputDataset = '/lambdab_lambda2Pi/yilai-Run3Summer22_MiniAODv4-9542347e91aacc6744c44ee907c98ff2/USER'
#config.Data.inputDataset = '/JPsiMuMu_JPsiNoFilter_2MuPtEtaFilter_TuneCP5_13p6TeV-pythia8-evtgen/Run3Summer22EEMiniAODv4-130X_mcRun3_2022_realistic_postEE_v6-v4/MINIAODSIM'
#config.Data.inputDataset = '/BuToJpsiK_JpsiToMuMu_MuFilter_Pt-2_TuneCP5_13p6TeV_pythia8-evtgen/Run3Summer22EEMiniAODv4-130X_mcRun3_2022_realistic_postEE_v6-v2/MINIAODSIM'
#config.Data.inputDataset = '/Jpsito2Mu_JpsiPT8_TuneCP5_13p6TeV_pythia8/Run3Summer22EEMiniAODv4-MUO_POG_130X_mcRun3_2022_realistic_postEE_v6-v2/MINIAODSIM'
config.Data.inputDataset = '/Upsilonto2Mu_UpsilonFilter_2MuFilter_TuneCP5_13p6TeV_pythia8/Run3Summer22EEMiniAODv4-130X_mcRun3_2022_realistic_postEE_v6-v2/MINIAODSIM'

#config.Data.inputDBS = 'phys03'
config.Data.inputDBS = 'global'
#config.Data.splitting = 'FileBased'
#config.Data.unitsPerJob = 2
config.Data.splitting = 'EventAwareLumiBased'
config.Data.unitsPerJob = 100000
#config.Data.totalUnits = 5
config.JobType.maxMemoryMB = 2000  ## 2500*4
#config.JobType.maxJobRuntimeMin = 1315  ## 21.9 hours
config.JobType.numCores = 2
#config.Data.splitting = 'EventAwareLumiBased'
#config.Data.unitsPerJob = 10000

#config.Data.outLFNDirBase = '/store/user/yilai/NanoPost'
config.Data.outLFNDirBase = '/store/group/phys_b2g/sqian/VV_comb_workdir/NanoPost/EEC/'
config.Data.publication = False
config.Data.outputDatasetTag = config.General.requestName
config.section_("Site")
config.Site.storageSite = "T2_CH_CERN"
#config.Site.storageSite = "T3_US_FNALLPC"

# config.section_("User")
#config.User.voGroup = 'dcms'

