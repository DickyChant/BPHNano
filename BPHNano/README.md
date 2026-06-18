# BDh
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
* Configuration by MiniAOD campaigns
  * Monte Carlo
    * **RunIII2024Summer24MiniAODv6**
      * Example:
        * CMSSW_15_0_17
      	* ```cmsDriver.py RECO --conditions 150X_mcRun3_2024_realistic_v2 --datatier NANOAOD --era Run3_2024 --eventcontent NANOAODSIM --filein filein.root --fileout file:test_mc.root --nThreads 4 -n 1000 --no_exec --python_filename test_mc.py --scenario pp --step NANO --mc ```
    * **Run3Summer23BPixMiniAODv4**
      * Example:
        * CMSSW: CMSSW_13_0_24
      	* ```cmsDriver.py RECO --conditions 130X_mcRun3_2023_realistic_postBPix_v6 --datatier NANOAOD --era Run3_2023 --eventcontent NANOAODSIM --filein filein.root --fileout file:test_mc.root --nThreads 4 -n 1000 --no_exec --python_filename test_mc_23postBpix.py --scenario pp --step NANO --mc ```
    * **Run3Summer23MiniAODv4**
      * era: Run3_2023,run3_nanoAOD_pre142X
      * conditions: auto:phase1_2023_realistic
      * Example:
        * CMSSW: CMSSW_13_0_24
      	* ```cmsDriver.py RECO --conditions 130X_mcRun3_2023_realistic_v15 --datatier NANOAOD --era Run3_2023 --eventcontent NANOAODSIM --filein filein.root --fileout file:test_mc.root --nThreads 4 -n 1000 --no_exec --python_filename test_mc_23preBpix.py --scenario pp --step NANO --mc ```
    * **Run3Summer22EEMiniAODv4** 
      * Example:
        * CMSSW: CMSSW_13_0_24
      	* ```cmsDriver.py RECO --conditions 130X_mcRun3_2022_realistic_postEE_v6 --datatier NANOAOD --era Run3 --eventcontent NANOAODSIM --filein filein.root --fileout file:test_mc.root --nThreads 4 -n 1000 --no_exec --python_filename test_mc_22postEE.py --scenario pp --step NANO --mc ```
    * **Run3Summer22MiniAODv4** 
      * Example:
        * CMSSW: CMSSW_13_0_24
      	* ```cmsDriver.py RECO --conditions 130X_mcRun3_2022_realistic_v5 --datatier NANOAOD --era Run3 --eventcontent NANOAODSIM --filein filein.root --fileout file:test_mc.root --nThreads 4 -n 1000 --no_exec --python_filename test_mc_22preEE.py --scenario pp --step NANO --mc ```


  * Data
    * **Run2024**
      * era: Run3,run3_nanoAOD_pre142X
      * conditiongs: auto:run3_data_prompt
      * Example:
      	* ```cmsDriver.py RECO --conditions auto:run3_data_prompt --datatier NANOAOD --era Run3,run3_nanoAOD_pre142X --eventcontent NANOAOD --filein filein.root --fileout file:test_data.root --nThreads 4 -n 10000 --no_exec --python_filename test_data_24.py --scenario pp --step NANO ```
    * **Run2023**
      * era: Run3,run3_nanoAOD_pre142X
      * conditiongs: auto:run3_data_prompt
      * Example:
      	* ```cmsDriver.py RECO --conditions auto:run3_data_prompt --datatier NANOAOD --era Run3,run3_nanoAOD_124 --eventcontent NANOAOD --filein filein.root --fileout file:test_data.root --nThreads 4 -n 10000 --no_exec --python_filename test_data_23.py --scenario pp --step NANO ```
    * **Run2022**
      * era: Run3,run3_nanoAOD_pre142X
      * conditiongs: auto:run3_data_prompt
      * Example:
      	* ```cmsDriver.py RECO --conditions auto:run3_data_prompt --datatier NANOAOD --era Run3,run3_nanoAOD_124 --eventcontent NANOAOD --filein filein.root --fileout file:test_data.root --nThreads 4 -n 10000 --no_exec --python_filename test_data_22.py --scenario pp --step NANO ```


