target=~/.profile
echo "adding aliases for scripts to $target" 
echo ""                                                              >> $target
echo "# =========================================== #"               >> $target
echo "# toolbox commands"                                            >> $target
echo ""                                                              >> $target
echo "TOOLBOX=$PWD"                                                  >> $target
echo ""                                                              >> $target
echo "alias rootpy='python -i    \$TOOLBOX/scripts/rootpy.py'"       >> $target
echo "alias  fitpy='python -i    \$TOOLBOX/scripts/fitpy.py'"        >> $target
echo "alias  dnnpy='python -i    \$TOOLBOX/scripts/dnnpy.py'"        >> $target
echo ""                                                              >> $target
echo "alias mrcrab='python       \$TOOLBOX/scripts/mrcrab.py'"       >> $target
echo ""                                                              >> $target
echo "alias condorSubmit='python \$TOOLBOX/scripts/condorSubmit.py'" >> $target

echo "adding toolbox to PYTHONPATH in $target"
echo ""                                                              >> $target
echo "PYTHONPATH=\$TOOLBOX:\$PYTHONPATH"                             >> $target
echo "PYTHON27PATH=\$TOOLBOX:\$PYTHON27PATH"                         >> $target
echo "PYTHON3PATH=\$TOOLBOX:\$PYTHON3PATH"                           >> $target
echo "echo \"added \$TOOLBOX to PYTHONPATH\""                        >> $target
echo ""                                                              >> $target
echo "source \$TOOLBOX/check_for_updates.sh"                         >> $target
echo "# =========================================== #"               >> $target

echo "done." 
echo "this will be automatically loaded when you open your shell"
echo "or via 'source $target'"
echo ""
python testprint.py
