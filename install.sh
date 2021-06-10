target=~/.profile
echo "adding source script for TOOLBOX to $target" 
echo ""                     >> $target
echo "source $PWD/setup.sh" >> $target
echo ""                     >> $target

echo "done." 
echo "this will be automatically loaded when you open your shell"
echo "or via 'source $target'"
echo ""

CMSSW_BASE=/nfs/dust/cms/user/swieland/ttH_legacy/CMSSW_11_1_0_pre4
export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
source $VO_CMS_SW_DIR/cmsset_default.sh
cd $CMSSW_BASE
eval `scram runtime -sh`
cd -

python testprint.py
