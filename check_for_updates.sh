cd $TOOLBOX
if [[ $(git rev-parse HEAD) != $(git ls-remote origin master | cut -f1) ]]
then

    if read -q "choice?Do you want to update TOOLBOX? [y/N] ";
    then
        echo "\ncommits to be updated:"

        # collecting all commits
        IFS=$'\n' commits=($(git log --pretty=oneline origin master))
        for commit in $commits
        do
            IFS=' ' read -rA c <<< "$commit"
            # print all commits up to the one that is currently active
            if [[ $(git rev-parse HEAD) == $c[1] ]]
            then
                break
            fi
            echo $commit
        done
        echo "\nupdating..."
        git pull origin master
        echo "done."
    fi
fi
cd -
