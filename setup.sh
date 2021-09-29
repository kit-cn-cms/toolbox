alias rootpy='python -i    $TOOLBOX/scripts/rootpy.py'
alias  fitpy='python -i    $TOOLBOX/scripts/fitpy.py'
alias  dnnpy='python -i    $TOOLBOX/scripts/dnnpy.py'

alias mrcrab='python       $TOOLBOX/scripts/mrcrab.py'
alias yieldTable='python   $TOOLBOX/scripts/yieldTable.py'

alias condorSubmit='python $TOOLBOX/scripts/condorSubmit.py'

PYTHONPATH=$TOOLBOX:$PYTHONPATH
PYTHON27PATH=$TOOLBOX:$PYTHON27PATH
PYTHON3PATH=$TOOLBOX:$PYTHON3PATH
echo "added $TOOLBOX to PYTHONPATH"

cd $TOOLBOX
if [[ $(git rev-parse HEAD) != $(git ls-remote origin master | cut -f1) ]]
then

    if read -q "choice?Do you want to update TOOLBOX? [y/N] ";
    then
        echo "\nupdating..."
        git pull origin master
        echo "done."
    fi
fi
cd -


