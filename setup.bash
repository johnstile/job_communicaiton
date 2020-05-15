#!/bin/bash
# By: John Stile <john@stilen.com>
# Purpose: Setup isolated python environemtn and required modules 

if [ -d "venv" ]; then
    echo "[>>] virtualenv found"
else
    TASK='Create virtualenv'
    echo "[>>] $TASK"
    virtualenv --python=python3 venv
    if [ $? != 0 ]; then
        echo "[!!] FAIL: $TASK"
        exit 1
    fi
fi

TASK='Activate virtualenv'
echo "[>>] $TASK"
. venv/bin/activate
if [ $? != 0 ]; then
    echo "[!!] FAIL: $TASK"
    exit 1
fi

TASK='Install python modules requriements'
echo "[>>] $TASK"
pip install -r pip_requirements.txt
if [ $? != 0 ]; then
    echo "[!!] FAIL: $TASK"
    exit 1
fi

TASK="Update everything"
echo "[>>] $TASK"
pip install pip-review
pip-review --auto
if [ $? != 0 ]; then
    echo "[!!] FAIL: $TASK"
    exit 1
fi

