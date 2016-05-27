#!/bin/sh

if [ ! -d py27 ]; then
    virtualenv py27
    py27/bin/pip install -e hg+http://bitbucket.org/cmorisse/openerp-jsonrpc-client/#egg=openerp-jsonrpc-client
fi
py27/bin/python test_getCustFullInfo.py
