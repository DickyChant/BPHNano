#!/usr/bin/env python3
#
# Example of running the postprocessor to skim events with a cut, and 
# adding a new variable using a Module.
#
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor
from importlib import import_module
import os
import sys
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

fnames = ["test_mc.root"]

#fnames = [
#"/eos/cms/store/group/phys_b2g/sqian/VV_comb_workdir/NanoPost/postNano/BPHnano_Lambda_data_0.root",
#"/eos/cms/store/group/phys_b2g/sqian/VV_comb_workdir/NanoPost/postNano/BPHnano_Lambda_data_1.root",
#"/eos/cms/store/group/phys_b2g/sqian/VV_comb_workdir/NanoPost/postNano/BPHnano_Lambda_mc_v2_10.root",
#"/eos/cms/store/group/phys_b2g/sqian/VV_comb_workdir/NanoPost/postNano/BPHnano_Lambda_mc_v2_11.root",
#"/eos/cms/store/group/phys_b2g/sqian/VV_comb_workdir/NanoPost/postNano/BPHnano_Lambda_mc_v2_12.root",
#"/eos/cms/store/group/phys_b2g/sqian/VV_comb_workdir/NanoPost/postNano/BPHnano_Lambda_mc_v2_13.root",
#"/eos/cms/store/group/phys_b2g/sqian/VV_comb_workdir/NanoPost/postNano/BPHnano_Lambda_mc_v2_14.root",
#"/eos/cms/store/group/phys_b2g/sqian/VV_comb_workdir/NanoPost/postNano/BPHnano_Lambda_mc_v2_15.root",
#"/eos/cms/store/group/phys_b2g/sqian/VV_comb_workdir/NanoPost/postNano/BPHnano_Lambda_mc_v2_16.root",
#"/eos/cms/store/group/phys_b2g/sqian/VV_comb_workdir/NanoPost/postNano/BPHnano_Lambda_mc_v2_17.root",
#"/eos/cms/store/group/phys_b2g/sqian/VV_comb_workdir/NanoPost/postNano/BPHnano_Lambda_mc_v2_18.root",
#"/eos/cms/store/group/phys_b2g/sqian/VV_comb_workdir/NanoPost/postNano/BPHnano_Lambda_mc_v2_1.root",
#"/eos/cms/store/group/phys_b2g/sqian/VV_comb_workdir/NanoPost/postNano/BPHnano_Lambda_mc_v2_2.root",
#"/eos/cms/store/group/phys_b2g/sqian/VV_comb_workdir/NanoPost/postNano/BPHnano_Lambda_mc_v2_3.root",
#"/eos/cms/store/group/phys_b2g/sqian/VV_comb_workdir/NanoPost/postNano/BPHnano_Lambda_mc_v2_4.root",
#"/eos/cms/store/group/phys_b2g/sqian/VV_comb_workdir/NanoPost/postNano/BPHnano_Lambda_mc_v2_5.root",
#"/eos/cms/store/group/phys_b2g/sqian/VV_comb_workdir/NanoPost/postNano/BPHnano_Lambda_mc_v2_6.root",
#"/eos/cms/store/group/phys_b2g/sqian/VV_comb_workdir/NanoPost/postNano/BPHnano_Lambda_mc_v2_7.root",
#"/eos/cms/store/group/phys_b2g/sqian/VV_comb_workdir/NanoPost/postNano/BPHnano_Lambda_mc_v2_8.root",
#"/eos/cms/store/group/phys_b2g/sqian/VV_comb_workdir/NanoPost/postNano/BPHnano_Lambda_mc_v2_9.root",
#        ]
#fnames = [
#"/eos/cms/store/group/phys_b2g/sqian/VV_comb_workdir/NanoPost/nano_lambdaB/LambdaBToJpsiLambda_Unbiased_0.root",
#"/eos/cms/store/group/phys_b2g/sqian/VV_comb_workdir/NanoPost/nano_lambdaB/LambdaBToJpsiLambda_Unbiased_1.root",
#"/eos/cms/store/group/phys_b2g/sqian/VV_comb_workdir/NanoPost/nano_lambdaB/LambdaBToJpsiLambda_Unbiased_2.root"
#]


p = PostProcessor(outputDir=".",
                  inputFiles=fnames,
                  cut="nMuMu>=1",
                  provenance=True,
                  maxEntries=50000000, #just read the first maxEntries events
                  )
p.run()
