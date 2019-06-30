#!/usr/bin/env python3
# coding: utf8

# auteur originel : Gabriel Pettier
# fork : nany
# license GPL V3 or later

# pour poster les messages sur le forum
# nécessite python 3 minimum.

from counter_path import FORUM_URL, POSTFILE, STATFILE, MYPATH, FILESPATH
from counter_funclib import log
from time import sleep
import counter_forum as forum
import sys

if len(sys.argv) > 1 and sys.argv[1] == 'stat':
    pfile = STATFILE
    urlfile = FILESPATH + 'url_poststat'
else:
    pfile = POSTFILE
    urlfile = FILESPATH + 'url_TdCT'

if pfile == STATFILE:
    log('ENVOI DES STATISTIQUES' + '\n')
else:
    log('ENVOI DES COMPTES DE POINTS' + '\n')
log('début\n                  ‾‾‾‾‾')

sleep(2)

browser = forum.getBrowser()

sleep(1)

forum.log_in(browser, FORUM_URL)

sleep(1)

forum.post(browser, pfile, urlfile)

sleep(1)

forum.log_out(browser, FORUM_URL)

log('fin\n                  ‾‾‾\n')

