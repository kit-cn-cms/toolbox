target=~/.profile
echo "adding source script for TOOLBOX to $target" 
echo ""                          >> $target
echo "export TOOLBOX=$PWD"       >> $target
echo "source \$TOOLBOX/setup.sh" >> $target
echo ""                          >> $target

echo "done." 
echo "this will be automatically loaded when you open your shell"
echo "or via 'source $target'"
echo ""

