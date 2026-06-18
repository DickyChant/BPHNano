import sys

# if using a list
# source /cvmfs/cms.cern.ch/common/crab-setup.sh
# python3  xx.py xx.txt
from CRABClient.UserUtilities import config
config = config()

# if using this file directly
#from WMCore.Configuration import config
#config = config()


config.section_("General")
config.General.requestName = 'BNanoPost_2022_Data_26Jan2'
config.General.workArea = '/afs/cern.ch/work/y/yilai/gamma/crab_projects_data_26Jan2'
config.General.transferLogs = True

config.section_("JobType")
config.JobType.pluginName = 'Analysis'

year = "2022pre"

if "2022pre" in year:
    config.JobType.psetName = "test_data_22.py"
if "2022post" in year:
    config.JobType.psetName = "test_data_22.py"
if "2023pre" in year:
    config.JobType.psetName = "test_data_23.py"
if "2023post" in year:
    config.JobType.psetName = "test_data_23.py"

#config.JobType.psetName = 'PSet.py'
config.JobType.scriptExe = 'crab_script_data.sh'
config.JobType.scriptArgs = []
config.JobType.inputFiles = ['BPH_postproc_data.py', 'test_data_22.py', 'test_data_23.py']
config.JobType.outputFiles = ['test_data_Skim.root']
#config.JobType.sendPythonFolder = True
config.section_("Data")
config.Data.inputDataset = '/ParkingDoubleMuonLowMass1/Run2022F-22Sep2023-v1/MINIAOD'
#config.Data.inputDBS = 'phys03'
config.Data.inputDBS = 'global'
config.Data.splitting = 'EventAwareLumiBased'
config.Data.unitsPerJob = 100000 # events
config.JobType.maxMemoryMB = 4000  ## 2500*4
#config.JobType.maxJobRuntimeMin = 1315  ## 21.9 hours
config.JobType.numCores = 4

if "2022pre" in year:
    config.Data.lumiMask = '/eos/user/c/cmsdqm/www/CAF/certification/Collisions22/Cert_Collisions2022_355100_362760_Golden.json'
if "2022post" in year:
    config.Data.lumiMask = '/eos/user/c/cmsdqm/www/CAF/certification/Collisions22/Cert_Collisions2022_355100_362760_Golden.json'
if "2023pre" in year:
    config.Data.lumiMask = '/eos/user/c/cmsdqm/www/CAF/certification/Collisions23/Cert_Collisions2023_366442_370790_Golden.json'
if "2023post" in year:
    config.Data.lumiMask = '/eos/user/c/cmsdqm/www/CAF/certification/Collisions23/Cert_Collisions2023_366442_370790_Golden.json'

#config.Data.outLFNDirBase = '/store/user/yilai/NanoPost_NosaveTrk'
config.Data.outLFNDirBase = '/store/group/phys_b2g/sqian/VV_comb_workdir/NanoPost/EEC/'
config.Data.publication = False
config.Data.outputDatasetTag = config.General.requestName
config.section_("Site")
config.Site.storageSite = "T2_CH_CERN"

#config.Site.storageSite = "T3_US_FNALLPC"

# config.section_("User")
#config.User.voGroup = 'dcms'

if __name__ == '__main__':
    f=open(sys.argv[1]) 
    content = f.readlines()
    content = [x.strip() for x in content] 
    from CRABAPI.RawCommand import crabCommand
    n=10
    for dataset in content :
        config.Data.inputDataset = dataset
        n+=1
        nnn="%s"%n
        config.General.requestName = "BNanoPost_Data_"+dataset.split('/')[1][:30]+dataset.split('/')[2][:30]+nnn
        config.Data.outputDatasetTag = dataset.split('/')[2][:30]+nnn
        print(config.General.requestName, config.Data.outputDatasetTag)
        crabCommand('submit', config = config)
        #crabCommand('submit', config = config, dryrun = True)

