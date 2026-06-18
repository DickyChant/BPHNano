#this is not meant to be run locally
#
echo Check if TTY
if [ "`tty`" != "not a tty" ]; then
  echo "YOU SHOULD NOT RUN THIS IN INTERACTIVE, IT DELETES YOUR LOCAL FILES"
else

echo "ENV..................................."
env 
echo "VOMS"
voms-proxy-info -all
echo "CMSSW BASE, python path, pwd"
echo $CMSSW_BASE 
echo $PYTHON_PATH
echo $PWD 
#rm -rf $CMSSW_BASE/lib/
#rm -rf $CMSSW_BASE/src/
#rm -rf $CMSSW_BASE/module/
#rm -rf $CMSSW_BASE/python/
#mv lib $CMSSW_BASE/lib
#mv src $CMSSW_BASE/src
#mv module $CMSSW_BASE/module
#mv python $CMSSW_BASE/python

echo Found Proxy in: $X509_USER_PROXY
echo "Running script with arguments: $@"
# Run the main CMSSW configuration
#echo ">>> Running cmsRun..."
#cmsRun test_mc_2022.py
echo 'cmsRun -j FrameworkJobReport.xml -p PSet.py'
cmsRun -j FrameworkJobReport.xml PSet.py
echo 'DONE cmsRun PSet.py'

echo "After cmsRun PSet.py PWD: " $PWD 
echo "After cmsRun PSet.py ls:"
ls

# Run post-processing script (if needed)
echo ">>> Running post-processing..."
python3 BPH_postproc_mc.py
fi
