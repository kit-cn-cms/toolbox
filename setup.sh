alias rootpy='python3 -i    $TOOLBOX/scripts/rootpy.py'
alias  roofi='python3 $TOOLBOX/scripts/roofi.py'
alias  fitpy='python3 -i    $TOOLBOX/scripts/fitpy.py'
alias  dnnpy='python3 -i    $TOOLBOX/scripts/dnnpy.py'

alias mrcrab='python       $TOOLBOX/scripts/mrcrab.py'
alias yieldTable='python   $TOOLBOX/scripts/yieldTable.py'

alias condorSubmit='python $TOOLBOX/scripts/condorSubmit.py'

alias summary='python3 -m correctionlib.cli summary'

PYTHONPATH=$TOOLBOX:$PYTHONPATH
PYTHON27PATH=$TOOLBOX:$PYTHON27PATH
PYTHON3PATH=$TOOLBOX:$PYTHON3PATH
echo "added $TOOLBOX to PYTHONPATH"



