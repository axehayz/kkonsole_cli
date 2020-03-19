#! /usr/bin/env bash

# Below -- commands for autocompletion in bash. <autocomplete href="http://click.palletsprojects.com/en/7.x/bashcomplete/"></autocomplete>
# THE BELOW RAN WHEN USED WITH --editable PIP PYTHON INSTALL AND MANUALLY ADDING THE BELOW COMMANDS. 
# TRY WITH PATH AS ROOT KKONSOLE DIR; AND/OR USING A .SH SCRIPT AND USING RUN IN DOCKERFILE
# CMD _KPERFORM_COMPLETE=source kperform > /kkonsole/config/kperform-complete.sh && \
#    touch ~/.bashrc && \ 
#    echo ". /kkonsole/config/kperform-complete.sh" > ~/.bashrc && \
#    source ~/.bashrc

_KPERFORM_COMPLETE=source kperform > /kkonsole/config/kperform-complete.sh
_KKONSOLE_COMPLETE=source kkonsole > /kkonsole/config/kkonsole-complete.sh
touch ~/.bashrc
echo ". /kkonsole/config/kperform-complete.sh" >> ~/.bashrc
echo ". /kkonsole/config/kkonsole-complete.sh" >> ~/.bashrc
# source ~/.bashrc