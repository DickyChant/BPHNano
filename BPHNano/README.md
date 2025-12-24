# BDh

## Setup (CMSSW)

From inside your CMSSW area (e.g. `CMSSW_13_3_0/src`):

```bash
cmsenv
scram b -j 8
```

## Setup (CRAB)

If you use `BPHNano/production/submit_on_crab.py`, make sure CRAB and a valid proxy are available:

```bash
source /cvmfs/cms.cern.ch/common/crab-setup.sh
voms-proxy-init -voms cms
voms-proxy-info -all
```

## command to generate configuration file with cmsDriver.py

## cmsDriver Options
Here is a list required cmsDriver options. Many branches not needed, so we could customize the output file content
```
from PhysicsTools.NanoAOD.nano_cff import *
from PhysicsTools.BPHNano.nanoBPH_cff import *
process = nanoAOD_customizeMC(process)
process = nanoAOD_customizeBDh_MC(process)
process.nanoAOD_BPH_step = cms.Path(process.nanoSequence + cms.Sequence(cms.Task(lhcInfoTable)) + cms.Sequence(genWeightsTableTask))
```
then replace 
```
#process.schedule = cms.Schedule(process.nanoAOD_step,process.endjob_step,process.NANOAODSIMoutput_step)
```
with 
```
process.schedule = cms.Schedule(process.nanoAOD_BPH_step,process.endjob_step,process.NANOAODSIMoutput_step)

```

## Processing examples
    * **Run3Summer22MiniAODv4** 
      * era: Run3
      * conditions: auto:phase1_2022_realistic
      * Example:
      	* ```cmsDriver.py RECO --conditions auto:phase1_2022_realistic --datatier NANOAOD --era Run3 --eventcontent NANOAODSIM --filein /store/mc/Run3Summer22MiniAODv4/DstarToD0Pi_D0To2Mu_MuFilter_SoftQCDnonD_TuneCP5_13p6TeV_pythia8-evtgen/MINIAODSIM/130X_mcRun3_2022_realistic_v5-v1/30000/71ec4425-d76b-446d-9d89-a7b250c56568.root --fileout file:test_mc.root --nThreads 8 -n 1000 --no_exec --python_filename test_mc.py --scenario pp --step NANO --mc --customise_commands="process.add_(cms.Service('InitRootHandlers', EnableIMT = cms.untracked.bool(False)))"```
  * Data
    * **Run2022**
      * era: Run3,run3_nanoAOD_124
      * conditions: 140X_dataRun3_Prompt_v4
      * Example:
      	* ```cmsDriver.py RECO --conditions 140X_dataRun3_Prompt_v4 --datatier NANOAOD --era Run3,run3_nanoAOD_124 --eventcontent NANOAOD --filein file:/eos/cms/store/user/dmytro/tmp/store+data+Run2022C+ParkingDoubleMuonLowMass0+MINIAOD+PromptReco-v1+000+357+271+00000+ea64a9c2-6b1f-4744-b4ea-41aa0e3c3e1b.root --fileout file:test_data.root --nThreads 4 -n 10000 --no_exec --python_filename test_data.py --scenario pp --step NANO --customise_commands="process.add_(cms.Service('InitRootHandlers', EnableIMT = cms.untracked.bool(False)))"```

## Optional Filtering
If you want to add event filtering to the commands below you just need to modify the step option the following way
* `--step NANO,FILTER:PhysicsTools/BPHNano/BDhFilter_cff.BDhFilterSequence`

## test commands
```
cmsRun test/run_BDh_cfg.py inputFiles="file:postprocess/condor/3d1335a2-5a61-46ec-919f-ea4c8bb01898.root" outputFiles="data.root" maxEvents=10 isMC=false skip=40
cmsRun test/run_BDh_cfg.py inputFiles="file:postprocess/condor/MiniAODv4_237.root" outputFiles="MC.root" maxEvents=500  skip=0
```
