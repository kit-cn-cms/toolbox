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
